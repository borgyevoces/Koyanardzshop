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
                
                # Helper to send via MailerSend HTTP API
                def _send_via_mailersend(subject, message, from_email, recipient_email):
                    api_key = os.getenv('MAILERSEND_API_KEY', '').strip()
                    if not api_key:
                        raise RuntimeError('MAILERSEND_API_KEY not configured')

                    url = 'https://api.mailersend.com/v1/email'
                    headers = {
                        'Authorization': f'Bearer {api_key}',
                        'Content-Type': 'application/json',
                    }
                    # Include a sender name and validate the from_email format
                    payload = {
                        'from': {
                            'email': from_email,
                            'name': 'Koya Nardz Shop'
                        },
                        'to': [{'email': recipient_email}],
                        'subject': subject,
                        'text': message,
                    }
                    try:
                        resp = requests.post(url, json=payload, headers=headers, timeout=10)
                        if resp.status_code not in (200, 201, 202):
                            logger.error(f"MailerSend API returned {resp.status_code}: {resp.text}")
                        else:
                            logger.info(f"MailerSend: email queued/sent to {recipient_email} for user {instance.username}")
                    except Exception as e:
                        logger.error(f"Failed to send via MailerSend to {recipient_email}: {e}")

                # Fallback helper using Django send_mail (kept as threaded to avoid blocking)
                def _send_via_django(subject, message, from_email, recipient_list):
                    try:
                        send_mail(
                            subject,
                            message,
                            from_email,
                            recipient_list,
                            fail_silently=False,
                        )
                        logger.info(f"OTP email sent successfully to {recipient_list} for user {instance.username}")
                    except Exception as e:
                        logger.error(f"Failed to send OTP email to {recipient_list}: {str(e)}")

                # Choose MailerSend API if configured, otherwise use Django's send_mail
                chosen_from = settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') and settings.DEFAULT_FROM_EMAIL else settings.EMAIL_HOST_USER
                # Log and validate the chosen from address to help diagnose provider rejections
                logger.info(f"OTP sending: chosen from_email='{chosen_from}' recipient='{instance.email}' for user={instance.username}")

                if os.getenv('MAILERSEND_API_KEY', '').strip():
                    # Basic validation: must contain an @ to be considered an email address
                    if not chosen_from or '@' not in chosen_from:
                        logger.error("MailerSend: invalid or missing DEFAULT_FROM_EMAIL/EMAIL_HOST_USER; set a valid sender email in Render env as DEFAULT_FROM_EMAIL and verify it in MailerSend dashboard")
                    else:
                        threading.Thread(
                            target=_send_via_mailersend,
                            args=(subject, message, chosen_from, instance.email),
                            daemon=True
                        ).start()
                else:
                    threading.Thread(
                        target=_send_via_django,
                        args=(subject, message, settings.EMAIL_HOST_USER, [instance.email]),
                        daemon=True
                    ).start()