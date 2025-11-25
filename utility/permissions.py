from rest_framework.permissions import BasePermission, SAFE_METHODS

class isAdminUserOrReadOnly(BasePermission):
    """
    Custom permission to only allow admin users to edit objects. All users can read.
    """
    def has_permission(self, request, view):
        user = request.user
        if user.is_staff:
            return True
        if request.method in SAFE_METHODS:
            return True
        return False