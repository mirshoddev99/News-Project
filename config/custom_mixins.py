from django.contrib.auth.models import User
from django.shortcuts import redirect


class DispatchMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)
