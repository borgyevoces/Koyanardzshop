# Google OAuth Configuration - Quick Setup

## ✅ What Was Done

You successfully ran:
```bash
python manage.py migrate
```

This created all the necessary allauth database tables for:
- User accounts
- Social authentication
- Google OAuth provider data

## 🔑 Next: Get Your Google OAuth Credentials

1. **Visit Google Cloud Console:**
   - Go to: https://console.cloud.google.com/
   - Create a new project (or select existing)

2. **Create OAuth 2.0 Credentials:**
   - Go to: **APIs & Services** → **Credentials**
   - Click: **+ CREATE CREDENTIALS** → **OAuth client ID**
   - Select: **Web application**
   - Name: "Koya Nardz"

3. **Add Authorized Redirect URIs:**
   ```
   http://localhost:8000/accounts/google/login/callback/
   http://127.0.0.1:8000/accounts/google/login/callback/
   ```

4. **Copy Your Credentials:**
   - Client ID: `xxx.apps.googleusercontent.com`
   - Client Secret: `xxxxx`

## 📝 Add to `.env` File

Create or edit `.env` in the project root:

```
GOOGLE_OAUTH_CLIENT_ID=your_client_id_here
GOOGLE_OAUTH_CLIENT_SECRET=your_client_secret_here
```

## ⚙️ Configure in Django Admin

1. **Start Django server:**
   ```bash
   python manage.py runserver
   ```

2. **Go to Admin:**
   - Visit: http://localhost:8000/admin/
   - Login with your superuser account

3. **Create Social Application:**
   - Go to: **Social applications** (on left menu)
   - Click: **+ Add**
   - Fill:
     - **Provider:** Google
     - **Name:** Google
     - **Client id:** (paste your Client ID)
     - **Secret key:** (paste your Client Secret)
     - **Sites:** Select your site
   - Click: **Save**

## 🧪 Test Google Login

1. **Go to Signup Page:**
   - Visit: http://localhost:8000/register/
   - Click: Google button
   - You should be redirected to Google login

2. **Or Go to Login Page:**
   - Visit: http://localhost:8000/login/
   - Click: Google button

## ❓ Troubleshooting

### "Site matching query does not exist"
- Go to Django Admin → **Sites**
- Make sure there's a site with Domain: `localhost:8000`
- Set Site ID in this site to 1

### "Redirect URI mismatch"
- Check your Google Cloud redirect URIs match exactly
- Format should be: `http://domain:port/accounts/google/login/callback/`

### "No such table: socialaccount_socialapp"
- Run: `python manage.py migrate` again

### Social application doesn't appear in dropdown
- Make sure you created it in Django Admin first
- Refresh the page

## 📱 Production (Render.com)

For production:

1. **Update Redirect URIs in Google Cloud:**
   ```
   https://your-render-app.onrender.com/accounts/google/login/callback/
   ```

2. **Add Environment Variables on Render:**
   - `GOOGLE_OAUTH_CLIENT_ID=xxx`
   - `GOOGLE_OAUTH_CLIENT_SECRET=xxx`

3. **Update Site in Production Django Admin:**
   - Domain: `your-render-app.onrender.com`
   - Set it as your SITE_ID in settings

## ✨ Now Users Can:

✅ Sign up with email/password
✅ Sign in with Google
✅ Sign up with Google (creates account automatically)
✅ Link Google account to existing email account

All in one unified authentication system!
