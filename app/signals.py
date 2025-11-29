from django.db.models.signals import post_save
from django.conf import settings
from django.dispatch import receiver
from django.core.mail import send_mail
from django.utils import timezone
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
                # For Google OAuth: require account completion before login
                # Keep account inactive until they complete setup
                instance.is_active = False
                instance.is_oauth_pending = True
                instance.save()
                logger.info(f"Google OAuth account created for {instance.username} - set to inactive pending profile completion")
            else:
                # Require email verification for normal signups
                otp = OtpToken.objects.create(user=instance, otp_expires_at=timezone.now() + timezone.timedelta(minutes=5))
                instance.is_active = False
                instance.save()
                
                # Send verification email
                subject = "Email Verification - Koya Nardz Shop"
                message = f"""
Dear {instance.username},

Thank you for signing up at Koya Nardz Shop!

Your OTP verification code is:
{otp.otp_code}

This code expires in 5 minutes.

Please visit this link to verify your email:
http://127.0.0.1:8000/signup/{instance.username}

If you didn't create this account, please ignore this email.

Best regards,
Koya Nardz Shop Team
                """
                
                try:
                    send_mail(
                        subject,
                        message,
                        settings.EMAIL_HOST_USER,
                        [instance.email],
                        fail_silently=False,
                    )
                    logger.info(f"OTP email sent successfully to {instance.email} for user {instance.username}")
                except Exception as e:
                    logger.error(f"Failed to send OTP email to {instance.email}: {str(e)}")
                    # Don't raise the exception - let the user know about it through another mechanism if needed