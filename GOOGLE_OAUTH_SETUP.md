# Google OAuth Setup Guide

## Step 1: Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Go to **APIs & Services** → **Credentials**
4. Click **+ CREATE CREDENTIALS** → **OAuth client ID**
5. Choose **Web application**
6. Add authorized redirect URIs:
   - `http://localhost:8000/accounts/google/login/callback/`
   - `http://127.0.0.1:8000/accounts/google/login/callback/`
   - `https://yourdomain.com/accounts/google/login/callback/` (for production)
7. Copy your **Client ID** and **Client Secret**

## Step 2: Add Credentials to Environment

Add these to your `.env` file:

```
GOOGLE_OAUTH_CLIENT_ID=your_client_id_here
GOOGLE_OAUTH_CLIENT_SECRET=your_client_secret_here
```

## Step 3: Run Migrations

```bash
python manage.py migrate
```

This creates the necessary allauth tables for social authentication.

## Step 4: Configure in Django Admin

1. Go to `http://localhost:8000/admin/`
2. Navigate to **Sites** and ensure you have a site with:
   - Domain: `localhost:8000` (for development)
   - Name: `Koya Nardz` (or your site name)
3. Go to **Social applications** and create a new one:
   - Provider: Google
   - Name: Google
   - Client id: (paste your Client ID)
   - Secret key: (paste your Client Secret)
   - Sites: Select your site

## Step 5: Test Google Login

- Visit signup page and click Google button
- Or visit login page and click Google button
- You should be redirected to Google login
- After authenticating, you'll be redirected back and logged in

## Troubleshooting

### "Site matching query does not exist"
- Make sure you have a Site in Django admin matching your current domain
- Set SITE_ID = 1 in settings.py

### "Redirect URI mismatch"
- Check the redirect URIs in Google Cloud Console match your app's callback URL
- Format: `http://domain.com/accounts/google/login/callback/`

### "Provider not found"
- Make sure migrations ran: `python manage.py migrate`
- Make sure allauth apps are in INSTALLED_APPS

### Users can't access their account after Google login
- Check SOCIALACCOUNT_AUTO_SIGNUP = True in settings.py
- Check ACCOUNT_EMAIL_VERIFICATION in settings.py

## Production Deployment

For production on Render:

1. Add to Render environment variables:
   ```
   GOOGLE_OAUTH_CLIENT_ID=your_client_id
   GOOGLE_OAUTH_CLIENT_SECRET=your_client_secret
   SITE_ID=1
   ```

2. In Google Cloud Console, add this redirect URI:
   ```
   https://your-render-app.onrender.com/accounts/google/login/callback/
   ```

3. In Django admin (production site), update the Site:
   - Domain: `your-render-app.onrender.com`
   - Name: `Koya Nardz`

## How It Works

1. User clicks "Sign in with Google" button
2. User is redirected to Google login page
3. After authentication, Google redirects back to your app
4. django-allauth automatically:
   - Creates a CustomUser if email doesn't exist
   - Links the Google account to the user
   - Logs the user in
   - Redirects to LOGIN_REDIRECT_URL (/)

Both email signup and Google OAuth share the same user database, so users can:
- Sign up with email/password
- Later log in with Google if their email matches
- Or vice versa
