from django.db.models.signals import post_save
from django.conf import settings
import os
import requests
from django.dispatch import receiver
from django.core.mail import send_mail
from django.utils import timezone
import threading
from .models import OtpToken
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_token(sender, instance, created, **kwargs):
    if created:
        if instance.is_superuser:
            pass
        else:
            # Check if this is a Google OAuth signup (no password set)
            is_google_oauth = not instance.has_usable_password()
            
            if is_google_oauth:
                # Auto-activate Google OAuth accounts - no profile completion needed
                instance.is_active = True
                instance.is_oauth_pending = False
                instance.save()
                logger.info(f"Google OAuth account created and activated for {instance.username}")
            else:
                # For normal signups, DO NOT send OTP email here
                # The register view handles OTP creation and email sending
                # Mark as inactive - will be activated after OTP verification in register view
                instance.is_active = False
                instance.save()
                logger.info(f"User {instance.username} created (inactive, OTP will be sent by register view)")