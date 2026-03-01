from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*roles):
    """Restrict view access to users with specific roles."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            if request.user.role not in roles:
                messages.error(request, 'You do not have permission to access that page.')
                return redirect('dashboard:redirect')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def admin_required(view_func):
    return role_required('ADMIN')(view_func)


def trainer_required(view_func):
    return role_required('TRAINER')(view_func)


def member_required(view_func):
    return role_required('MEMBER')(view_func)
