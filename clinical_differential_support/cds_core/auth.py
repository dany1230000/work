from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.urls import reverse


def staff_required(view_func):
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if request.user.is_active and request.user.is_staff:
            return view_func(request, *args, **kwargs)
        return redirect_to_login(
            request.get_full_path(),
            reverse("cds_core:review_login"),
        )

    return wrapped
