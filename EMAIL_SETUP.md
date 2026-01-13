# Email Configuration Guide

## Problem
Render.com blocks outbound SMTP connections to external mail servers (like Gmail SMTP). This causes the error:
```
OSError: [Errno 101] Network is unreachable
```

## Solution: Use SendGrid

SendGrid is a transactional email service that works perfectly with Render and has a free tier.

### Step 1: Create SendGrid Account

1. Go to [SendGrid Sign Up](https://sendgrid.com/pricing/) (Free tier available)
2. Create a free account
3. Verify your email address

### Step 2: Get API Key

1. Log in to SendGrid Dashboard
2. Go to **Settings** → **API Keys**
3. Click **Create API Key**
4. Name it (e.g., "Koyanardzshop Render")
5. Select **Restricted Access** and give these permissions:
   - `mail.send`
6. Copy the API key (you'll only see it once!)

### Step 3: Configure on Render

1. Go to your Render service
2. Click **Environment**
3. Add new environment variable:
   - **Key:** `SENDGRID_API_KEY`
   - **Value:** Paste your API key from SendGrid
4. Save and redeploy

### Step 4: Verify Email Sender (Optional but Recommended)

To avoid sandbox mode limitations:

1. In SendGrid Dashboard, go to **Settings** → **Sender Authentication**
2. Click **Create New Sender**
3. Add your sender email (e.g., `noreply@yourdomain.com`)
4. Follow the verification steps (add DNS records)
5. Once verified, emails will be sent with full capability

### For Local Development

If you want to use Gmail locally while SendGrid is used on production:

1. Get a Gmail [App Password](https://myaccount.google.com/apppasswords)
   - Select "Mail" and "Windows Computer"
   - Google will generate a 16-character password
2. Set `EMAIL_HOST_PASSWORD` in `.env` to this password
3. Keep `SENDGRID_API_KEY` empty in `.env` for local development

### Testing Email

To test if emails are working:

```bash
# In Django shell
python manage.py shell

from django.core.mail import send_mail
send_mail(
    'Test Email',
    'This is a test email.',
    'noreply@koyanardzshop.com',
    ['your-email@example.com'],
)
```

You should receive the email within seconds.

### Configuration Details

**Current Setup:**
- **Local:** Gmail SMTP (requires app password)
- **Production (Render):** SendGrid (via Anymail)

**Files Modified:**
- `.env` - Added `SENDGRID_API_KEY` variable
- `BuynSell/settings.py` - Added SendGrid backend configuration
- `app/views.py` - Improved error messages (doesn't expose technical details)

### Troubleshooting

| Issue | Solution |
|-------|----------|
| "Invalid API Key" | Copy API key again from SendGrid, no spaces |
| Emails not received | Check SendGrid bounce rate in dashboard |
| Sandbox mode error | Verify sender email in SendGrid Settings |
| "Network unreachable" | Make sure `SENDGRID_API_KEY` is set on Render |

### Free Tier Limits

- **SendGrid Free:** 100 emails/day, unlimited days
- If you need more, upgrade to Pro ($29.95/month) for 100K emails/month

### More Information

- [SendGrid Django Integration](https://docs.sendgrid.com/for-developers/sending-email/django/)
- [Anymail Documentation](https://anymail.readthedocs.io/)
- [Render Network Restrictions](https://render.com/docs/deploy-node-express-app#network)
