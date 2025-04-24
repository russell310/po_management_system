from rest_framework.permissions import BasePermission

class IsManager(BasePermission):
    """
    Custom permission to grant access only to users who belong to the 'Manager' group.
    Usage:
        Apply this permission class to DRF views or viewsets to restrict access
        to managerial users only.

    Example:
        class MyView(APIView):
            permission_classes = [IsManager]
    """
    def has_permission(self, request, view):
        return request.user.groups.filter(name="Manager").exists()
