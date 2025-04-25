import os
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm 
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.utils.decorators import method_decorator

from .forms import UserForm, ProfileForm, LocationForm
from main.models import Listing, LikedListing

def login_view(request):
    if request.method == 'POST':
        login_form = AuthenticationForm(request=request, data=request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            print(user)
            if user is not None:
                login(request, user)
                messages.success(request, f"You are now logged in as {username}")
                return redirect("home")
            else:
                messages.error(request, f"An error occured when trying to login.")
        else:
            messages.error(request, f"An error occured when trying to login.")
    elif request.method == 'GET':
        login_form = AuthenticationForm()
    return render(request, 'views/login.html', {'login_form': login_form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('main')

class RegisterView(View):
    def get(self, request):
        register_form = UserCreationForm()
        return render(request, 'views/register.html', {'register_form': register_form})
    def post(self, request):
        register_form = UserCreationForm(data=request.POST)
        if register_form.is_valid():
            user = register_form.save()
            user.refresh_from_db()
            login(request, user)
            messages.success(request, f'User {user.username} has been created successfully.')
            return redirect("home")
        else:
            messages.error(request, f"An error occured when trying to register.")
            return render(request, 'views/register.html', {'register_form': register_form})
       
        
@method_decorator(login_required, name='dispatch')
class ProfileView(View):

    def get(self, request):
        user_listing = Listing.objects.filter(seller=request.user.profile)
        user_liked_listing = LikedListing.objects.filter(profile=request.user.profile).all()
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
        location_form = LocationForm(instance=request.user.profile.location)

        return render(request, 'views/profile.html', 
                      {'user_form': user_form, 'profile_form': profile_form, 
                       'location_form': location_form, 'user_listing': user_listing, 'user_liked_listing': user_liked_listing})
    def post(self, request):
        user_listing = Listing.objects.filter(seller=request.user.profile)
        user_liked_listing = LikedListing.objects.filter(profile=request.user.profile).all()
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        location_form = LocationForm(request.POST, instance=request.user.profile.location)

        if user_form.is_valid() and profile_form.is_valid() and location_form.is_valid():
            # Handle the deletion of the old profile picture before saving the new one
            if 'photo' in request.FILES:
                old_photo = request.user.profile.photo
                if old_photo:
                    # Log old photo path for debugging
                    print(f"Old photo path: {old_photo.path}")
                    if os.path.isfile(old_photo.path):
                        try:
                            os.remove(old_photo.path)  # Attempt to remove the old photo
                            print(f"Deleted old photo: {old_photo.path}")
                        except Exception as e:
                            print(f"Error deleting old photo: {e}")

            user_form.save()
            profile_form.save()  # This saves the new photo if it's been uploaded
            location_form.save()

            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
        else:
            messages.error(request, 'An error occurred while updating the profile.')
            return render(request, 'views/profile.html', 
                        {'user_form': user_form, 'profile_form': profile_form, 
                        'location_form': location_form, 'user_listing': user_listing, 'user_liked_listing': user_liked_listing})