from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.response import Response
from rest_framework import status
from custom_user.models import User
from authentication.api.serializers import CustomerRegistrationSerializer, LoginSerializer, PasswordChangeSerializer, PasswordResetCodeSerializer, PasswordResetSerializer
from rest_framework.parsers import MultiPartParser,FormParser
from rest_framework.decorators import action
import threading
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.utils import timezone
from authentication.models import VerificationCode
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.password_validation import validate_password as django_validate_password

class HandleThreading(threading.Thread):
    def __init__(self, subject, message, recipient_list):
        self.subject = subject
        self.message = message
        self.recipient_list = recipient_list
        self.success = None
        threading.Thread.__init__(self)

    def run(self):
        from_email = 'favouroghenevwoke@gmail.com'
        try:
            send_mail(self.subject, self.message, from_email, self.recipient_list, fail_silently=False)
            self.success = True
        except Exception as e:
            self.errors = str(e)
            self.success = False

class CustomerRegistrationViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    http_method_names = ['post']
    serializer_class = CustomerRegistrationSerializer

    def create(self, request):
        serializer = CustomerRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')
        if User.objects.filter(email=email).exists():
            return Response({"error": "A user with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({'message':'Registration is successful', 'data' : serializer.data}, status=status.HTTP_201_CREATED)


class LoginViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    http_method_names = ['post']

    @swagger_auto_schema(
        operation_description="User login endpoint",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'password'],
            properties={
                'username': openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    description='Username or email'
                ),
                'password': openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    description='Password',
                    format='password'
                ),
            }
        ),)
    def create(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {'message' : 'Login successfull', 'data' : serializer.validated_data}, status=status.HTTP_200_OK)
    
class PasswordChangeViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']

    @swagger_auto_schema(
        operation_description="Change password endpoint",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['old_password', 'new_password'],
            properties={
                'old_password': openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    description='Old Password',
                    format='password'
                ),
                'new_password': openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    description='New Password',
                    format='password'
                ),
            }
        ),)
    @action(detail=False, methods=['post'],)
    def change_password(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        old_password = serializer.validated_data.get('old_password')
        new_password = serializer.validated_data.get('new_password')

        if not user.check_password(old_password):
            return Response({"error": "Old password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)

class PasswordResetCodeViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    serailizer_class = PasswordResetCodeSerializer

    @swagger_auto_schema(
        operation_description="Request code for password reset",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email'],
            properties={
                'email': openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    description='email',
                    format='email'
                ),
            }
        ),)
    @action(detail=False, methods=['post'],)
    def send_password_reset_code(self, request):
        serializer = self.serailizer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')
        
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            verification_code = VerificationCode.create_code(user=user)
            message = f"Dear {user.first_name},\n\n The code for resetting your password is {verification_code.code}.\n\n Ignore this message if you did not request for this code"
            
            thread= HandleThreading(message=message, recipient_list=[user.email], subject='Reset password code')
            thread.start()
            thread.join()
            if thread.success:
                return Response({'message' : 'Code has been sent'})
            else:
                return Response({'message' : thread.errors}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
           
        else:
            return Response({'message':'User with these email does not exist',}, status=status.HTTP_400_BAD_REQUEST)
        
    
class PasswordResetViewSet(viewsets.ViewSet):
    http_method_names = ['post']
    serializer_class = PasswordResetSerializer

    def validate_reset_code(self, user, code_input):
        try:
            code = VerificationCode.objects.get(user=user, code=code_input)
            times_used = code.times_used
        except VerificationCode.DoesNotExist:
            return False, 'Invalid code'
        if code.expires_at < timezone.now():
            return False, 'Expired code'
        if times_used > 0:
            return False, 'Code has been used'
        code.times_used =+ 1
        code.save()
        return True, 'success'


    @swagger_auto_schema(
        operation_description="Endpoint for password reset",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'reset_code', 'new_password'],
            properties={
                'email': openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    description='email',
                    format='email'
                ),
                'reset_code': openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    description='reset_code',
                    format='code'
                ),
                'new_password': openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    description='new_password',
                    format='password'
                ),
            }
        ),)
    @action(detail=False, methods=['post'],)
    def reset_password(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid()
        email = serializer.validated_data.get('email')
        if not email:
            return Response({'message':'email field is required'}, status=status.HTTP_400_BAD_REQUEST)
        print(f"email {email}")
        code = serializer.validated_data.get('reset_code')
        new_password = serializer.validated_data.get('new_password')

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)

            valid, msg = self.validate_reset_code(user, code)
            if not valid:
                return Response({'message': msg}, status=status.HTTP_400_BAD_REQUEST)
            try:
                django_validate_password(new_password)
            except ValidationError as e:
                return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password reset is successful'})
        else:
            return Response({'message': 'User with this email does not exists'}, status=status.HTTP_400_BAD_REQUEST)

class LogOutViewSet(viewsets.ViewSet):
    http_method_names = ['post']
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="logout endpoint",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh'],
            properties={
                'refresh': openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    description='refresh',
                    format='refresh'
                ),
            }
        ))
    @action(detail=False, methods=['post'],)
    def logout(self, request):
        try:
            print(f" this is the {request.data['refresh']}")
            refresh_token = request.data['refresh']
            if not refresh_token:
                return Response({'message':'refresh_token is not provided'})
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            return Response({'message': request.data.get('refresh')}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'message' : 'Logout is successful'})
    