from rest_framework.permissions import BasePermission


class IsObjectOwner(BasePermission):
    """
    This class is to check if obj.user == request.user.
    Permissions will be called one by one:
    - if action has detail=False, this class will only check has_permission();
    - if action has detail=True, this class will check both
      has_permission() and has_object_permission().
    If the user has no permissions, then the below message will be shown.
    """
    message = 'You do not have permission to access this object.'

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user