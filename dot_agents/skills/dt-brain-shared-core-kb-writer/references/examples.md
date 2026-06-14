# KB Article Examples

Use these ❌ BAD / ✅ GOOD pairs to understand the expected quality level for each section.

## Environment Section

**❌ BAD - Incomplete Environment**:
```markdown
## Environment
- Windows
- Using Chrome
```

**✅ GOOD - Complete Environment**:
```yaml
## Environment
Product: GitLab CE
Version: 16.5.2
Operating System: Windows 11 Pro (22H2)
Environment: Production
User Role: Developer (Maintainer access)
Browser: Chrome 120.0.6099.129
Network: Corporate VPN (Cisco AnyConnect 4.10)
```

## Problem / Symptom Section

**❌ BAD - Vague Problem Description**:
```markdown
## Problem
Users can't log in. The system shows an error.
```

**✅ GOOD - Specific Problem with Error Code**:
```markdown
## Problem

When attempting to log in to the GitLab web interface, users see a red banner with the message:

> "403 Forbidden: Your account has been blocked. Contact your administrator."

**What happened**:
1. User navigated to https://gitlab.company.com
2. Entered valid username and password
3. Clicked "Sign in" button
4. Received 403 error immediately (< 1 second)

**Expected behavior**: User should be redirected to GitLab dashboard after successful login.

**Actual behavior**: Login rejected with 403 error, user remains on login page.

**Frequency**: Affects 5 users consistently since 2024-02-08. Other users can log in normally.
```

**❌ BAD - Mixing Problem with Solution**:
```markdown
## Problem
VPN won't connect. You need to check your credentials and restart the VPN client.
```

**✅ GOOD - Problem Only, No Solution**:
```markdown
## Problem

When connecting to company VPN, users receive error:

> "VPN Error 691: The remote connection was denied because the user name and password combination you provided is not recognized."

**What happened**:
1. User opened Cisco AnyConnect VPN client
2. Entered credentials (username@company.com + password)
3. Clicked "Connect"
4. Connection attempt fails after 15-20 seconds with Error 691

**Expected behavior**: VPN connects successfully, user can access internal resources.

**Actual behavior**: Connection fails with authentication error despite correct credentials verified in Active Directory.

**Frequency**: Started affecting 3 users on 2024-02-09 morning. Same credentials work for Windows login.
```

## Cause Section

**❌ BAD - No Explanation**:
```markdown
## Cause
The account was disabled.
```

**✅ GOOD - Technical Explanation**:
```markdown
## Cause

The affected user accounts were automatically disabled by GitLab's "Max login attempts" security policy.

**Root cause**: GitLab 16.5+ enforces a security policy that locks accounts after 5 consecutive failed login attempts within 15 minutes. This prevents brute-force attacks.

**Why this happened**:
1. Users changed their passwords via the corporate password reset portal
2. Password change synced to Active Directory immediately
3. GitLab LDAP sync runs every 30 minutes (on the hour and half-hour)
4. Users attempted to log in with new password before LDAP sync completed
5. Multiple failed attempts with old password triggered account lock
6. Even after LDAP sync, locked accounts remain disabled until admin unlocks them

**Why the 403 error**: GitLab returns HTTP 403 for locked accounts to distinguish from authentication failures (HTTP 401), preventing attackers from enumerating valid usernames.
```

**✅ GOOD - User-Friendly Explanation**:
```markdown
## Cause

Your account was temporarily locked for security reasons after too many incorrect login attempts.

**What happened**: GitLab automatically locks accounts after 5 failed login attempts within 15 minutes to protect against unauthorized access. This is a safety feature.

**Why you saw this error**: The system detected multiple failed logins (likely when you tried your new password before it synced) and locked your account as a precaution.
```

## Resolution Section

**❌ BAD - Vague Steps**:
```markdown
## Resolution
Ask your administrator to unlock your account. Then try logging in again.
```

**✅ GOOD - Detailed, Numbered Steps**:
```markdown
## Resolution

**For Administrators**:

1. **Log in to GitLab admin area**:
   ```
   Navigate to: https://gitlab.company.com/admin
   ```

2. **Locate the locked user account**:
   - Click "Users" in left sidebar
   - Search for affected username
   - Look for "Blocked" badge next to user's name

3. **Unblock the user**:
   - Click on the user's name to open their profile
   - Click "Unblock user" button at top right
   - Confirm by clicking "Unblock" in the confirmation dialog

   **Expected outcome**: User status changes from "Blocked" to "Active"

4. **Verify LDAP sync is current**:
   ```bash
   sudo gitlab-rake gitlab:ldap:check
   ```
   **Expected output**: "LDAP check finished" with no errors

5. **Notify the user** to try logging in again

**For End Users** (after admin unblocks):

1. **Clear browser cache and cookies**:
   - Chrome: Settings → Privacy → Clear browsing data → Last hour
   - Firefox: Settings → Privacy → Clear Data → Cookies and Cache

2. **Close all browser tabs** and restart browser

3. **Navigate to GitLab login page**:
   ```
   https://gitlab.company.com
   ```

4. **Log in with current Active Directory credentials**:
   - Username: your-email@company.com
   - Password: your current AD password (from password reset portal)

5. **Verify access**:
   - You should be redirected to GitLab dashboard
   - Check you can see your projects in the left sidebar

**Verification**: Successfully logged in and can access projects.

**Troubleshooting**: If login still fails with different error, see "Troubleshoot LDAP Authentication Issues (Error 401)"
```

## Full Article: Mixed Sections (Anti-Pattern)

**❌ BAD - Mixed Sections**:
```markdown
## Problem and Resolution

Users can't log in to GitLab with Error 403. This happens because accounts are locked. To fix this, administrators should unblock users in the admin panel by clicking Users → find blocked user → Unblock button.
```

**✅ GOOD - Separated Sections**:
```markdown
## Problem

When attempting to log in to GitLab web interface, users see error message:
> "403 Forbidden: Your account has been blocked. Contact your administrator."

Users are locked out immediately after entering valid credentials.

## Cause

Affected user accounts were automatically disabled by GitLab's "Max login attempts" security policy after 5 consecutive failed login attempts within 15 minutes.

## Resolution

**For Administrators**:

1. Log in to GitLab admin area at https://gitlab.company.com/admin
2. Click "Users" in left sidebar
3. Search for affected username
4. Click user's name → "Unblock user" button
5. Confirm by clicking "Unblock" in dialog

User can now log in normally.
```

## Passive Voice vs Active Voice

**❌ BAD - Passive and Vague**:
```markdown
## Resolution

It might be necessary to restart the service. The configuration file should be checked for errors. If problems persist, it could be a network issue and the logs might need to be reviewed.
```

**✅ GOOD - Active and Specific**:
```markdown
## Resolution

1. **Restart the PostgreSQL service**:
   ```bash
   sudo systemctl restart postgresql
   ```
   **Expected outcome**: Service restarts without errors in 5-10 seconds.

2. **Check configuration file for syntax errors**:
   ```bash
   sudo -u postgres psql -c "SHOW config_file;" # Find config location
   sudo pg_config --check /etc/postgresql/14/main/postgresql.conf
   ```
   **Expected outcome**: "configuration file is valid" message.

3. **If error persists, diagnose network connectivity**:
   ```bash
   sudo netstat -tuln | grep 5432  # Verify PostgreSQL listening on port 5432
   sudo tail -50 /var/log/postgresql/postgresql-14-main.log  # Check recent errors
   ```
   **Expected outcome**: Port 5432 shows "LISTEN" state, logs show "database system is ready to accept connections".
```

## Missing Environment Context

**❌ BAD - No Environment**:
```markdown
# Fix SSL Certificate Error

## Problem
Browser shows "Your connection is not private" error.

## Resolution
1. Install SSL certificate
2. Configure web server
3. Restart service
```

**✅ GOOD - Complete Environment Context**:
```markdown
---
title: "Fix SSL Certificate 'Not Private' Error in Chrome with Nginx"
product: "Nginx"
version: "1.24.0"
os: ["ubuntu-22.04", "ubuntu-20.04"]
browser: "Chrome 120+"
---

# Fix SSL Certificate 'Not Private' Error in Chrome with Nginx

## Environment

Web Server: Nginx 1.24.0
Operating System: Ubuntu 22.04 LTS
Certificate Type: Let's Encrypt (via Certbot)
Domain: example.com (single domain, not wildcard)
Browser: Google Chrome 120.0.6099.129
User Role: Server administrator with sudo access
```
