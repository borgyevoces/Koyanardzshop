# Django Admin User & Account Management

## Overview
Complete user and admin account management system integrated into Django Admin with advanced features for managing users, staff, and administrators.

## Features

### 1. User Management (CustomUserAdmin)

#### List Display
- **Username** - User's login name
- **Email** - User's email address
- **First/Last Name** - User's personal information
- **Is Staff** - Staff status indicator
- **Is Superuser** - Admin status indicator
- **Is Active** - Account status (active/inactive)
- **Account Status** - Color-coded status badge showing:
  - 🔴 **Inactive** (Red) - User account is disabled
  - 🟠 **OAuth Pending** (Orange) - OAuth account awaiting completion
  - 🟢 **Admin** (Green) - Superuser/Admin account
  - 🔵 **Staff** (Blue) - Staff member account
  - 🟢 **Active** (Green) - Regular active user
- **Created** - Account creation date

#### Filters
- **Is Staff** - Filter by staff status
- **Is Superuser** - Filter by admin status
- **Is Active** - Filter by account active status
- **Is OAuth Pending** - Filter by OAuth pending status
- **Date Joined** - Filter by registration date

#### Search
Search by:
- Username
- Email
- First Name
- Last Name

#### Field Groups (Fieldsets)

**Account Information**
- Username
- Email
- Password

**Personal Info**
- First Name
- Last Name
- Avatar Image
- Contact Number
- Address

**Permissions** (Collapsible)
- Is Active
- Is Staff
- Is Superuser
- Groups
- User Permissions

**OAuth & Account Status** (Collapsible)
- Is OAuth Pending
- Botpress User Key

**Important Dates** (Collapsible, Read-only)
- Last Login
- Date Joined

#### Bulk Actions

1. **Activate Selected Users** - Set is_active=True for multiple users
2. **Deactivate Selected Users** - Set is_active=False for multiple users
3. **Promote to Staff** - Grant staff privileges to selected users
4. **Remove Staff Status** - Revoke staff privileges
5. **Promote to Admin** - Grant superuser/admin privileges
6. **Remove Admin Status** - Revoke admin privileges

#### Custom Methods

- **account_status()** - Displays color-coded account status
- **created_date()** - Formats account creation date

---

### 2. OTP Token Management (OtpTokenAdmin)

#### List Display
- **User** - Associated user account
- **OTP Code** - 6-character verification code
- **Status** - Color-coded OTP status:
  - 🔴 **Expired** (Red) - OTP has passed expiration time
  - 🟢 **Active** (Green) - OTP is still valid
- **Created At** - When OTP was generated
- **Expires At** - OTP expiration timestamp
- **Last Resend** - When the code was last resent

#### Filters
- **Created At Date** - Filter by creation date
- **Expires At Date** - Filter by expiration date

#### Search
Search by:
- Username
- User email
- OTP code

#### Special Features
- **Read-only fields** - Cannot edit OTP details (user, code, timestamps)
- **No add permission** - Admins cannot manually create OTPs
- **Delete permission** - Only superusers can delete OTP records
- **Automatic sorting** - Lists newest OTPs first

#### Custom Methods

- **is_expired()** - Shows visual status of OTP validity
- **created_time()** - Formatted creation timestamp
- **expires_time()** - Formatted expiration timestamp
- **last_resend()** - Shows last resend time or "Never"

---

## How to Use

### Accessing Django Admin
1. Navigate to `/admin/` on your website
2. Login with superuser credentials
3. You'll see "Users" and "OTP Tokens" sections

### Managing User Accounts

#### Create New User
1. Click "Users" → "Add User"
2. Fill in Username, Email, and Password
3. Click Save
4. Edit the user to add more details (name, avatar, contact, address)

#### Activate/Deactivate Users
1. Select users from the list
2. Choose action: "Activate selected users" or "Deactivate selected users"
3. Click "Go"

#### Promote to Staff
1. Select users from the list
2. Choose "Promote to Staff"
3. Click "Go"
4. Users can now access admin panel with limited permissions

#### Promote to Admin
1. Select users from the list
2. Choose "Promote to Admin"
3. Click "Go"
4. Users become superusers with full admin access

#### Edit User Permissions
1. Click on a user to open their profile
2. Under "Permissions" section, assign groups or specific permissions
3. Save changes

### Monitoring OTP Tokens

#### View Active OTPs
1. Click "OTP Tokens"
2. Green "Active" status shows valid verification codes
3. Red "Expired" status shows codes that have timed out

#### Search for User's OTP
1. Use the search box to find by username or email
2. View OTP code, creation time, and expiration time

#### Clean Up Expired OTPs
1. Filter by expired status
2. Select expired OTPs
3. Delete to clean up database (superuser only)

---

## Technical Details

### Files Modified
- `/app/admin.py` - Complete admin configuration

### Models Registered
1. **CustomUser** - User accounts with extended admin interface
2. **OtpToken** - Email verification tokens with read-only access

### Features Implemented
- Custom user creation form with password validation
- Color-coded status indicators using Django's format_html
- Advanced filtering and search capabilities
- Bulk action system for managing multiple users
- Field grouping with collapsible sections
- Read-only timestamp fields
- Permission-based visibility control

---

## Security Features

✅ **Password Management**
- Passwords are hashed using Django's default hasher
- Password change form uses secure methods

✅ **OTP Protection**
- OTP codes cannot be edited via admin
- Only superusers can delete OTP records
- 1-minute cooldown prevents brute force on resends
- 5-minute expiration enforces time limits

✅ **Permission Control**
- Can assign granular permissions per user
- Staff/Admin status controls access levels
- Inactive users cannot login

✅ **OAuth Support**
- Track OAuth pending status
- Identify accounts needing profile completion

---

## Tips for Admins

1. **Regular Monitoring** - Check for inactive accounts needing cleanup
2. **Bulk Operations** - Use bulk actions to efficiently manage many users
3. **Search Efficiently** - Use search instead of scrolling through lists
4. **Filter by Status** - Use filters to find specific user groups
5. **Review OAuth Users** - Monitor OAuth pending accounts for completion
6. **OTP Monitoring** - Check for unusual OTP request patterns

---

## Future Enhancements

Possible additions:
- Email user accounts about status changes
- Export user list to CSV
- Mass password reset functionality
- User activity logs
- Advanced analytics dashboard
- 2FA setup tracking
