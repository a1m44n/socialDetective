from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'admin'

class IsInvestigator(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'investigator'

class IsViewer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'viewer'

class IsAdminOrInvestigator(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role in ['admin', 'investigator'] 