from rest_framework import viewsets
from booking.models import Booking
from rest_framework.permissions import IsAuthenticated
from booking.api.serializers import BookingSerializer
from rest_framework.response import Response
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
import uuid
import requests
from rest_framework.decorators import action
from drf_yasg import openapi
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status

class BookingViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'put', 'delete', 'patch']
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.all()
    
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data['check_in'] > serializer.validated_data['check_out']:
            return Response({"error": "Check-out date must be after check-in date."}, status=status.HTTP_400_BAD_REQUEST)
        booking = serializer.save()

        try:
            # create payment link
            tx_ref = str(uuid.uuid4())
            amount = float(booking.total_price)
            currency = "NGN"
            redirect_url = "https://your-frontend.com/payment/callback"

            payload = {
                "tx_ref": tx_ref,
                "amount": amount,
                "currency": currency,
                "redirect_url": redirect_url,
                "customer": {
                    "email": request.data.get("email", booking.customer.email),
                    "name": request.data.get("name", f"{booking.customer.first_name} {booking.customer.last_name}")
                },
                "meta": {
                    "booking_id": str(booking.public_id)
                }
            }
            headers = {
                "Authorization": f"Bearer {settings.FLW_SECRET_KEY}",
                "Content-Type": "application/json"
            }
            res = requests.post(f"{settings.FLW_BASE_URL}/payments", json=payload, headers=headers).json()
            
            if res.get("status") == "success":
                payment_link = res["data"]["link"]
                booking.payment_reference = tx_ref
                booking.save()
                return Response({
                    "message": "Payment link successfully generated",
                    "booking_id": booking.public_id,
                    "payment_link": payment_link
                }, status=status.HTTP_201_CREATED)
            
            return Response({"error": res}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            booking.delete()
            return Response({'message':str(e)}, status=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(
        method='get',
        manual_parameters=[
            openapi.Parameter(
                'tx_ref',
                openapi.IN_PATH,
                description="Transaction reference of the booking payment",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Payment successful",
                examples={
                    "application/json": {
                        "message": "Payment successful",
                        "booking_id": 1
                    }
                }
            ),
            400: openapi.Response(description="Payment not successful or error")
        }
    )
    @action(detail=False, methods=['get'], url_path='verify-payment')
    def verify_payment(request,):
        tx_ref = request.query_params.get('tx_ref')
        try:
            headers = {
                "Authorization": f"Bearer {settings.FLW_SECRET_KEY}"
            }
            res = requests.get(f"{settings.FLW_BASE_URL}/transactions/verify?tx_ref={tx_ref}", headers=headers).json()

            if res.get("status") == "success" and res['data']['status'] == 'successful':
                booking_id = res['data']['meta']['booking_id']
                booking = Booking.objects.get(booking_id=booking_id)
                booking.status = "paid"
                booking.save()
                return Response({"message": "Payment successful", "booking_id": booking.id}, status=status.HTTP_200_OK)

            return Response({"message": "Payment not successful", "data": res}, status=status.HTTP_400_BAD_REQUEST)

        except Booking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
    webhook_request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "event": openapi.Schema(type=openapi.TYPE_STRING, description="Event type"),
            "data": openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "tx_ref": openapi.Schema(type=openapi.TYPE_STRING),
                    "status": openapi.Schema(type=openapi.TYPE_STRING),
                    "meta": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "booking_id": openapi.Schema(type=openapi.TYPE_STRING)
                        }
                    )
                }
            )
        }
    )
    swagger_auto_schema(
        method='post',
        request_body=webhook_request_body,
        responses={200: "Webhook received"}
    )
    @action(detail=False, methods=['post'], url_path='flutterwave-webhook', permission_classes=[])
    @csrf_exempt
    def flutterwave_webhook(request):
        try:
            event = request.data
            tx_ref = event['data']['tx_ref']
            status_event = event['data']['status']

            booking_id = event['data']['meta'].get('booking_id')
            if booking_id:
                booking = Booking.objects.get(public_id=booking_id)

                if status_event == 'successful':
                    booking.status = "Confirmed"
                elif status_event == 'failed':
                    booking.status = "failed"
                booking.save()

            return Response({"message": "Webhook received"}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)



        