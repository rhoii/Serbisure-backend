from rest_framework import permissions

class IsServiceWorker(permissions.BasePermission):
    """
    Allows access only to users with the 'service_worker' role.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'service_worker'
        )

class IsServiceWorkerOrReadOnly(permissions.BasePermission):
    """
    Allows anyone to READ, but only Service Workers to WRITE.
    """
    def has_permission(self, request, view):
        # Allow search-only (GET, HEAD, OPTIONS) for everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Check if user is authenticated and is a service worker for other methods
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'service_worker'
        )

class IsHomeowner(permissions.BasePermission):
    """
    Allows access only to users with the 'homeowner' role.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'homeowner'
        )

class IsServiceProviderOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow providers of a service to edit or delete it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the provider of the service.
        return obj.provider == request.user or request.user.is_staff
