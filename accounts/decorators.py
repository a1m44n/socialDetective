from functools import wraps
from django.http import HttpResponseForbidden
from .permissions import IsAdmin, IsInvestigator, IsViewer, IsAdminOrInvestigator

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not IsAdmin().has_permission(request, None):
            return HttpResponseForbidden("Admin access required")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def investigator_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not IsInvestigator().has_permission(request, None):
            return HttpResponseForbidden("Investigator access required")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def viewer_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not IsViewer().has_permission(request, None):
            return HttpResponseForbidden("Viewer access required")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def admin_or_investigator_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not IsAdminOrInvestigator().has_permission(request, None):
            return HttpResponseForbidden("Admin or Investigator access required")
        return view_func(request, *args, **kwargs)
    return _wrapped_view 