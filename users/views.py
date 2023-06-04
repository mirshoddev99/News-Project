from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View

from config.custom_mixins import DispatchMixin
from .forms import UserRegistrationForm, UserEditForm, ProfileEditForm
from .models import Profile


class ProfileView(DispatchMixin, LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        contex = {"user": user}
        return render(request, 'users/user_profile.html', contex)


class UserRegisterView(View):
    def get(self, request):
        user_form = UserRegistrationForm()
        return render(request, 'users/register.html', {"user_form": user_form})

    def post(self, request):
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data["password"])
            new_user.save()
            Profile.objects.create(user=new_user)
            messages.success(request, 'You have successfully registered')
            return render(request, 'users/register_done.html', {"new_user": new_user})
        return render(request, 'users/register.html', {"user_form": user_form})


class EditUser(DispatchMixin, View, LoginRequiredMixin):

    def get(self, request):
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
        return render(request, 'users/profile_edit.html', {"user_form": user_form, "profile_form": profile_form})

    def post(self, request):
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile, data=request.POST, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('user_profile')
        return render(request, 'users/profile_edit.html', {"user_form": user_form, "profile_form": profile_form})
