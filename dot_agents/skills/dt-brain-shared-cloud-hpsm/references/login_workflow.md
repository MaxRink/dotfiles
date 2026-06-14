# HPSM Login Workflow

Reference for logging into HPSM (HP Service Manager / TDI Trouble Ticket) using `playwright-cli`.

**HPSM URL**: `https://ttm.ioss-ttm.in.pan-net.eu:8443/sm/index.do?lang=en`

---

## 1. Prerequisites

- **VPN**: Must be connected to the DT/TDI VPN. HPSM is only reachable from the internal network.
- **Environment variables**: The following must be set before running any commands:
  - `HPSM_USERNAME` — your LDAP username
  - `HPSM_PASSWORD` — your LDAP password
- **playwright-cli**: Must be available in the shell.

### Password quoting in .env

If the password contains special characters (e.g., `$`, `!`, `` ` ``), wrap it in
**single quotes** in `.env` to prevent shell expansion:

```bash
export HPSM_PASSWORD='MyP$ssw0rd!'
```

Without quotes, `$ssw0rd` would be interpreted as a variable reference.

---

## 2. Login Steps

### Snapshot-based approach (recommended)

The login form renders consistently with snapshot-friendly refs. This is the simplest
and most reliable approach.

```bash
# Step 1: Open HPSM in the browser
playwright-cli open "https://ttm.ioss-ttm.in.pan-net.eu:8443/sm/index.do?lang=en"

# Step 2: Take a snapshot (page loads in ~3 seconds)
# The snapshot will show:
#   - form "TDI Trouble Ticket LOGIN"
#     - textbox "Username" [ref=e14]
#     - textbox "Password" [ref=e18]
#     - button "LOGIN" [ref=e29]
playwright-cli snapshot

# Step 3: Fill username and password, then click LOGIN
playwright-cli fill <username-ref> "$HPSM_USERNAME"
playwright-cli fill <password-ref> "$HPSM_PASSWORD"
playwright-cli click <login-ref>

# Step 4: Wait for dashboard to load (~5 seconds) and verify
sleep 5
playwright-cli snapshot
# Success: page title shows "CaaS | TDI Trouble Ticket"
# Success: snapshot contains navigation tree with "Incident Management"
```

> **Note**: The `fill` command works well for the login form — no need for `type` with delays.
> Replace refs with actual values from your snapshot (they may differ between sessions).

### Run-code approach (fallback)

Only use this if the snapshot-based approach fails (e.g., refs are unreliable):

```bash
playwright-cli run-code "async page => {
  await page.waitForSelector('input[type=\"text\"], input[name=\"Login\"], #LoginUserName', { timeout: 30000 });
  await page.waitForTimeout(2000);

  const selectors = {
    username: ['#LoginUserName', 'input[name=\"Login\"]', 'input[placeholder=\"Username\"]', 'input[type=\"text\"]'],
    password: ['#LoginPassword', 'input[name=\"Password\"]', 'input[placeholder=\"Password\"]', 'input[type=\"password\"]']
  };

  for (const sel of selectors.username) {
    const el = await page.\$(sel);
    if (el) { await el.click(); await el.fill(''); await el.type('${HPSM_USERNAME}', { delay: 50 }); break; }
  }
  await page.waitForTimeout(500);

  for (const sel of selectors.password) {
    const el = await page.\$(sel);
    if (el) { await el.click(); await el.fill(''); await el.type('${HPSM_PASSWORD}', { delay: 50 }); break; }
  }
  await page.waitForTimeout(500);

  const btnSelectors = ['button:has-text(\"LOGIN\")', 'input[type=\"submit\"]', '#LoginButton'];
  for (const sel of btnSelectors) {
    const btn = await page.\$(sel);
    if (btn) { await btn.click(); break; }
  }

  await page.waitForLoadState('domcontentloaded', { timeout: 90000 });
  return 'Login submitted';
}"
```

---

## 3. Verification

After clicking LOGIN, verify that the dashboard loaded successfully.

### Quick check

```bash
playwright-cli snapshot
```

**Success indicators:**
- Page title: `CaaS | TDI Trouble Ticket` (shown in snapshot header)
- Navigation tree visible with: `treeitem " Incident Management"`, `treeitem " Change Management"`
- Active tab: `tab "CaaS" [active] [selected]`

**Failure indicators:**
- Page title still: `Login | TDI Trouble Ticket`
- Snapshot shows: `"Invalid login name/password. Please try again."`

---

## 4. LDAP Error Recovery

HPSM authenticates via LDAP. Transient failures are common.

### How LDAP errors manifest

LDAP transient errors appear as **"Invalid login name/password. Please try again."**
on the login page — the same message as actual wrong credentials. This is misleading
but confirmed through testing.

The error does **not** show "LDAP error" text — it reuses the generic login failure message.

### Recovery procedure

1. **Wait 10 seconds** before retrying — the LDAP server needs time to recover.
2. **Re-fill the login form** (the fields are cleared after failure; refs change).
3. **Take a fresh snapshot** to get updated refs before filling again.
4. **Retry up to 3 times**. If all attempts fail, report the error.

### Login with retry

```bash
# Attempt login up to 3 times with LDAP retry
for attempt in 1 2 3; do
  echo "Login attempt $attempt..."
  playwright-cli snapshot
  # Read new refs from snapshot (they change after each failed attempt)
  # Fill username, password, click LOGIN
  playwright-cli fill <username-ref> "$HPSM_USERNAME"
  playwright-cli fill <password-ref> "$HPSM_PASSWORD"
  playwright-cli click <login-ref>
  sleep 5

  # Check result
  playwright-cli snapshot
  # If "Incident Management" appears → success
  # If "Invalid login" appears → wait 10s and retry
  sleep 10
done
```

> **Key learning**: After a failed login, element refs change (e.g., `e14` → `e15`).
> Always take a fresh snapshot before each retry attempt.

---

## 5. Saving Auth State

After a successful login, save the browser's authentication state to skip login next time.

### Save state

```bash
playwright-cli state-save hpsm-auth.json
```

### Restore state

```bash
playwright-cli state-load hpsm-auth.json
playwright-cli goto "https://ttm.ioss-ttm.in.pan-net.eu:8443/sm/index.do?lang=en"
```

### Verify restored session

```bash
playwright-cli snapshot
# Confirm "Incident Management" appears — if not, the session expired
```

> **Tip**: HPSM sessions expire after extended inactivity. If a restored session
> shows the login page, discard the state file and perform a fresh login.

---

## 6. Troubleshooting

| Problem | Cause | Solution |
|---|---|---|
| Page doesn't load / timeout | Not connected to VPN | Connect to DT/TDI VPN and retry |
| Login form not found | Page still loading | Wait longer (5-10 seconds) before snapshot |
| "Invalid login name/password" on first attempt | LDAP transient error | Wait 10s, take fresh snapshot, retry (up to 3 times) |
| "Invalid login name/password" on all attempts | Wrong credentials | Verify `HPSM_USERNAME`/`HPSM_PASSWORD`; check for shell expansion issues with `$` in password |
| Password truncated or wrong | `$` in password expanded by shell | Use single quotes in `.env`: `export HPSM_PASSWORD='P$ss'` |
| Navigation tree not visible after login | Page still loading | Wait 5+ seconds after LOGIN click; dashboard takes time |
| Session expired after state restore | HPSM session timeout | Delete state file and perform fresh login |

### Useful diagnostic commands

```bash
# Check what the browser currently shows
playwright-cli snapshot

# Take a screenshot for visual debugging
playwright-cli screenshot hpsm-debug.png

# List all open browser sessions
playwright-cli list
```
