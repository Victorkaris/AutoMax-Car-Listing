from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Profile, Location

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        print(f"Signal triggered: Creating profile for {instance.username}")
        Profile.objects.create(user=instance)

@receiver(post_save, sender=Profile)
def create_profile_location(sender, instance, created, **kwargs):
    if created:
        location = Location.objects.create()  # Create a new Location
        instance.location = location  # Assign it to Profile
        instance.save()  

@receiver(post_delete, sender=Profile)
def delete_profile_location(sender, instance, *args, **kwargs):
            if instance.location:
                instance.location.delete()