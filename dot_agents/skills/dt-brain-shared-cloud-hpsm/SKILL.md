---
name: dt-brain-shared-cloud-hpsm
description: >-
  Automate HPSM (TDI Trouble Ticket) workflows using playwright-cli: scrape incidents,
  create change requests, and plan & schedule changes. Use when the user mentions "HPSM",
  "trouble ticket", "change request", "create change", "plan change", "plan and schedule",
  "incident queue", "scrape incidents", "INFRA-CAAS-L2S incidents", or needs to interact
  with the TDI Trouble Ticket system.
allowed-tools: Bash(playwright-cli:*)
---

<!-- Imported from tdi-caas/tools/dt-brain-shared/.claude/skills/cloud-hpsm by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# cloud-hpsm — HPSM Automation Skill

## Overview

**HPSM** (HP Service Manager), also known as the **TDI Trouble Ticket** system, is the legacy ITSM platform used by Deutsche Telekom TDI for incident management, change management, and service operations.

This skill automates HPSM using **`playwright-cli`** commands issued interactively (not scripts). The AI drives a real browser session, navigating HPSM's iframe-heavy UI by taking snapshots, clicking elements, and filling forms.

### Three Workflows

| # | Workflow | Description |
|---|----------|-------------|
| 1 | **Scrape Incidents** | Navigate to the incident queue for a given assignment group (default: `INFRA-CAAS-L2S`), extract all open incidents, and return structured data. |
| 2 | **Create Change** | Open a new change request form, fill in all required fields (title, description, impact, urgency, service, etc.), and save to obtain a change ID. |
| 3 | **Plan & Schedule** | Search for an existing change by ID, navigate to the Plan & Schedule phase, fill planning fields (dates, coordinator, owner, implementation/remediation plans), and save. |

---

## Prerequisites

1. **VPN** — You must be connected to the DT/TDI VPN. HPSM is not accessible from the public internet.
2. **Environment variables** — The following must be set (typically in `.env`):
   - `HPSM_USERNAME` — HPSM login username
   - `HPSM_PASSWORD` — HPSM login password
3. **`playwright-cli`** — Must be available in PATH. This is a CLI wrapper around Playwright that supports interactive browser automation via commands like `open`, `goto`, `click`, `fill`, `snapshot`, `eval`, `press`, `screenshot`, and `run-code`.

> **Tip**: Use `playwright-cli open --headed <url>` to show the browser window during execution.
> This is useful for debugging and for the user to watch the automation in real-time.

---

## HPSM Connection

| Parameter | Value |
|-----------|-------|
| **URL** | `https://ttm.ioss-ttm.in.pan-net.eu:8443/sm/index.do?lang=en` |
| **Viewport** | 1920×1080 (required — HPSM renders differently at smaller sizes) |
| **Default timeout** | 30 000 ms (HPSM is slow; increase to 60 000 ms for saves) |
| **Auth** | HTTP form login with `HPSM_USERNAME` / `HPSM_PASSWORD` |

### Login Flow

1. Navigate to the HPSM URL.
2. Take a snapshot — the login form shows `textbox "Username"`, `textbox "Password"`, `button "LOGIN"`.
3. Use `playwright-cli fill` and `click` with the snapshot refs.
4. LDAP may fail on first attempt with "Invalid login name/password" — retry with 10s cooldown (up to 3 times). After each failure, take a fresh snapshot as refs change.
5. After login, HPSM loads a frameset. The page title changes to `CaaS | TDI Trouble Ticket`.
6. Always take a `snapshot` after login to confirm the navigation tree is visible.

> **Important**: If password contains `$`, wrap it in single quotes in `.env`:
> `export HPSM_PASSWORD='P$ssw0rd'`

---

## Quick Start

### Scrape incidents assigned to INFRA-CAAS-L2S

```bash
# Automated (recommended):
source .env && .venv/bin/python .claude/skills/cloud-hpsm/scripts/scrape_incidents.py

# With a different assignment group:
source .env && .venv/bin/python .claude/skills/cloud-hpsm/scripts/scrape_incidents.py INFRA-IAAS-L2S

# Table format output:
source .env && .venv/bin/python .claude/skills/cloud-hpsm/scripts/scrape_incidents.py --format table
```

Or manually with `playwright-cli`:

```bash
# 1. Launch browser and navigate to HPSM
playwright-cli open "https://ttm.ioss-ttm.in.pan-net.eu:8443/sm/index.do?lang=en"
# 2. Login (snapshot → fill refs → click LOGIN, with LDAP retry)
# 3. Navigate: click "Incident Management" treeitem → click "Incident Queue" treeitem
# 4. Wait for table to load (~8s), expand group, extract with eval
# See: references/scrape_incidents.md for full steps
```

### Create a change request

```bash
# Automated (recommended):
source .env && .venv/bin/python .claude/skills/cloud-hpsm/scripts/create_change.py \
    --title "Upgrade cluster firmware" \
    --description "Upgrade firmware on worker nodes to patch CVEs" \
    --effect "Nodes remain vulnerable to known security issues" \
    --end-date "31/03/26 00:00:00"

# Dry run (fill form but don't save):
source .env && .venv/bin/python .claude/skills/cloud-hpsm/scripts/create_change.py \
    --title "Test change" --description "Test" --effect "None" \
    --end-date "31/03/26 00:00:00" --dry-run --headed

# Normal Change with custom options:
source .env && .venv/bin/python .claude/skills/cloud-hpsm/scripts/create_change.py \
    --model "Normal Change" \
    --title "Network reconfiguration" \
    --description "Reconfigure TOR switch VLANs" \
    --effect "Network not optimized" \
    --end-date "15/04/26 00:00:00" \
    --group INFRA-NETWORKS-L2S \
    --impact "3 - Multiple Users" \
    --urgency "3 - Average"
```

### Plan & schedule an existing change

```bash
# 1. Search for the change by ID
# 2. Navigate to Plan & Schedule phase
# 3. Fill dates, coordinator, owner, plans
# 4. Save
# See: Workflow 3 reference for full steps
```

---

## Workflow 1: Scrape Incidents

**Goal:** Extract all open incidents from a given assignment group's queue.

**Default assignment group:** `INFRA-CAAS-L2S`

**High-level steps:**
1. Login to HPSM (with LDAP retry).
2. Click `treeitem " Incident Management"` in the sidebar navigation tree.
3. Click `treeitem "Incident Queue"` in the expanded sub-menu.
4. Wait for the ExtJS treegrid to load (~8 seconds).
5. Click the assignment group's `gridcell` to expand it.
6. Use `playwright-cli eval` on the treegrid ref to extract `.x-grid3-row[aria-level="2"]` data rows.
7. Parse and return structured incident data (ID, title, status, priority, assignee, etc.).

**Automated script:**

```bash
source .env && .venv/bin/python .claude/skills/cloud-hpsm/scripts/scrape_incidents.py [ASSIGNMENT_GROUP]
```

> 📖 **Full step-by-step instructions:** See [references/scrape_incidents.md](references/scrape_incidents.md)

---

## Workflow 2: Create Change

**Goal:** Create a new change request with all required fields populated.

### Change Form Fields (HPSM `name` attributes)

| Field | HPSM `name` Attribute |
|-------|----------------------|
| Title | `instance/header/brief.description` |
| Requester Group | `instance/panip.requested.by.group` |
| Coordinator Group | `instance/panip.change.coord.group` |
| Requested End Date | `instance/requestedDate` |
| Reason for Change | `instance/header/reason` |
| Service | `instance/affected.item` |
| Impact | `instance/initial.impact` |
| Urgency | `instance/severity` |
| Risk Assessment | `instance/header/risk.assessment` |
| Description | `instance/description.structure/description/description` |
| Effect of Not Implementing | `instance/effect.not.impl/effect.not.impl` |

### Dropdown Values

**Change Type** (selected via sidebar or radio):
- `emergency` → "Emergency Change"
- `normal` → "Normal Change"
- `standard` → "Standard Change"

**Impact:**
- "1 - Enterprise"
- "2 - Site/Dept"
- "3 - Multiple Users"
- "4 - User"
- "5 - One Single Customer Complaint"

**Urgency:**
- "1 - Critical"
- "2 - High"
- "3 - Average"
- "4 - Low"
- "5 - Very Low"

**Reason for Change:**
- "Maintenance"

**Risk Assessment:**
- "0 - No Risk"
- "1 - Low Risk"
- "2 - Some Risk"
- "3 - Moderate Risk"
- "4 - High Risk"
- "5 - Very High Risk"

### Default Values

| Field | Default |
|-------|---------|
| Service | `CAAS_BM` |
| Coordinator Group | `INFRA-CAAS-L2S` |

### Date Format

All date fields use: **`DD/MM/YY HH:MM:SS`**

Example: `01/03/26 00:00:00` (March 1, 2026, midnight)

> 📖 **Full step-by-step instructions:** See [references/create_change.md](references/create_change.md)

---

## Workflow 3: Plan & Schedule

**Goal:** Open an existing change request by ID and fill out the Plan & Schedule phase fields.

### Search Form

| Field | HPSM `name` Attribute |
|-------|----------------------|
| Change ID | `instance/number` |

### Plan & Schedule Fields (HPSM `name` attributes)

| Field | HPSM `name` Attribute |
|-------|----------------------|
| Risk Assessment | `instance/header/risk.assessment` |
| Planned Start | `instance/header/planned.start` |
| Planned End | `instance/header/planned.end` |
| Downtime Start | `instance/middle/down.start` |
| Downtime End | `instance/middle/down.end` |
| Change Coordinator | `instance/header/coordinator` |
| Change Owner | `instance/change.owner` |
| Change Owner Group | `instance/change.owner.Group` |
| Assignment Group | `instance/header/assign.dept` |
| Implementation Plan | `instance/description.structure/plan/plan` |
| Remediation Plan | `instance/backout.plan/backout.plan` |

> 📖 **Full step-by-step instructions:** See [references/plan_change.md](references/plan_change.md)

---

## HPSM UI Patterns

HPSM is a legacy Java-based web application with a deeply nested iframe architecture. Understanding these patterns is critical for reliable automation.

### Iframe Navigation

HPSM uses multiple layers of iframes. **You do not need to manually switch between iframes** — `playwright-cli snapshot` captures the full page including all frames, and `playwright-cli eval <ref>` automatically resolves the correct iframe for a given snapshot ref.

### Sidebar Navigation

The left sidebar is an ARIA **tree** widget with `treeitem` elements. Key paths:
- **Incident Management** → expands to reveal: Create New Incident, **Incident Queue**, Incident Task Queue, Search Incidents
- **Change Management** → expands to reveal: **New Change**, **Search Changes**

Click `treeitem` refs to expand/collapse. After login, the sidebar shows items like:
```
treeitem " Incident Management" [ref=e345]
treeitem " Change Management" [ref=e341]
```

### ExtJS Grid (Incident Queue)

The incident list is an **ExtJS treegrid** with this DOM structure:
- **Container**: `treegrid "Record List, Grouped by Assignment Group..."`
- **Grid body**: `.x-grid3-body`
- **Group headers**: `.x-grid3-row[aria-level="1"]` — shows "Assignment Group: NAME (N Items)"
- **Data rows**: `.x-grid3-row[aria-level="2"]` — individual incidents
- **Cell values**: `.x-grid3-cell-inner` — ordered by column position

Use `playwright-cli eval` (not `run-code`) to extract data from the grid. Target the
treegrid ref from the snapshot and query `.x-grid3-row[aria-level="2"]` elements.

### Popup Dismissal

HPSM frequently shows modal popups (confirmations, warnings, validation messages). These must be dismissed before continuing. Common popup buttons: "OK", "Yes", "No", "Cancel".

Always check for and dismiss popups after:
- Saving a form
- Navigating between phases
- Changing dropdown values that trigger validation

### Phase Navigation (Change Records)

Change records have phases displayed as tabs or links:
- **Registration** — Initial creation
- **Plan & Schedule** — Planning details
- **Approval** — Approval workflow
- **Implementation** — Execution
- **Review** — Post-implementation

Navigate between phases by clicking the phase name/tab.

### Combo Input Fields

Some HPSM fields (like Service, Assignment Group) are "combo" inputs — they have a text field with a lookup button. For these:
1. Fill the text value into the input field.
2. Press `Tab` to trigger validation/lookup.
3. HPSM may auto-complete or show a popup if the value is ambiguous.

---

## Common `playwright-cli` Patterns for HPSM

### Filling a field by HPSM `name` attribute

Most HPSM form fields have a unique `name` attribute. Use `run-code` to find and fill them across all frames:

```bash
playwright-cli run-code "async page => {
  for (const frame of page.frames()) {
    const el = await frame.$('[name=\"FIELD_NAME\"]');
    if (el) {
      await el.scrollIntoViewIfNeeded();
      await el.click();
      await el.fill('');
      await el.type('VALUE', { delay: 50 });
      await el.press('Tab');
      return 'filled';
    }
  }
  return 'not found';
}"
```

Replace `FIELD_NAME` with the HPSM name attribute (e.g., `instance/header/brief.description`) and `VALUE` with the desired value.

**Why `type()` with delay instead of `fill()`?** HPSM's JavaScript event handlers sometimes don't fire with `fill()`. Using `type()` with a delay simulates real keystrokes and triggers the necessary change/input events. The preceding `fill('')` clears any existing value.

### Filling a hidden textarea (description/plan fields)

Description, implementation plan, and remediation plan fields use hidden `<textarea>` elements paired with `contenteditable` divs. Standard `click` + `type` won't work — use direct DOM manipulation:

```bash
playwright-cli run-code "async page => {
  for (const frame of page.frames()) {
    const result = await frame.evaluate((args) => {
      const ta = document.querySelector('textarea[name=\"' + args.name + '\"]');
      if (!ta) return null;
      ta.value = args.value;
      ta.dispatchEvent(new Event('input', { bubbles: true }));
      ta.dispatchEvent(new Event('change', { bubbles: true }));
      // Also try contenteditable div nearby
      const parent = ta.closest('td') || ta.parentElement;
      if (parent) {
        const editable = parent.querySelector('[contenteditable=\"true\"]');
        if (editable) editable.innerHTML = args.value.replace(/\\n/g, '<br>');
      }
      return 'filled';
    }, { name: 'FIELD_NAME', value: 'VALUE' });
    if (result) return result;
  }
  return 'not found';
}"
```

**Fields that require this pattern:**
- `instance/description.structure/description/description` (Change description)
- `instance/effect.not.impl/effect.not.impl` (Effect of not implementing)
- `instance/description.structure/plan/plan` (Implementation plan)
- `instance/backout.plan/backout.plan` (Remediation/backout plan)

### Dismissing HPSM popups

After saves or navigation, HPSM may show modal popups. Dismiss them:

```bash
playwright-cli run-code "async page => {
  for (const frame of page.frames()) {
    const dismissed = await frame.evaluate(() => {
      const buttons = document.querySelectorAll('button, a, input[type=\"button\"]');
      for (const btn of buttons) {
        const text = btn.textContent?.trim() || btn.value?.trim() || '';
        if (text === 'OK' && btn.offsetWidth > 0) {
          btn.click();
          return 'dismissed';
        }
      }
      return null;
    });
    if (dismissed) return dismissed;
  }
  return 'no popup found';
}"
```

**Tip:** Run this pattern in a loop (2–3 times with short delays) after saves, as HPSM sometimes chains multiple popups.

### Detecting save errors

After clicking Save, check for error messages:

```bash
playwright-cli run-code "async page => {
  const errors = [];
  for (const frame of page.frames()) {
    const msgs = await frame.evaluate(() => {
      const results = [];
      // Check for error divs
      document.querySelectorAll('.errorMessage, .msgBanner, [class*=\"error\"]').forEach(el => {
        if (el.offsetWidth > 0 && el.textContent.trim()) results.push(el.textContent.trim());
      });
      return results;
    });
    errors.push(...msgs);
  }
  return errors.length > 0 ? { status: 'error', messages: errors } : { status: 'ok' };
}"
```

### Taking a snapshot after each action

Always take a snapshot after significant actions to verify the UI state:

```bash
playwright-cli snapshot
```

This captures the current state of all frames and is essential for understanding what HPSM is showing (success messages, error banners, popup dialogs, etc.).

---

## Scripts

| Script | Description |
|--------|-------------|
| [scripts/scrape_incidents.py](scripts/scrape_incidents.py) | Automated incident scraping: login → navigate → extract → JSON output |
| [scripts/create_change.py](scripts/create_change.py) | Automated change creation: login → navigate → fill form → save → return Change ID |

Usage:
```bash
source .env && .venv/bin/python .claude/skills/cloud-hpsm/scripts/scrape_incidents.py [ASSIGNMENT_GROUP]
```

## References

| Document | Description | Status |
|----------|-------------|--------|
| [references/scrape_incidents.md](references/scrape_incidents.md) | Step-by-step guide for scraping the incident queue | ✅ Tested |
| [references/create_change.md](references/create_change.md) | Step-by-step guide for creating a new change request | ✅ Tested (Standard Change) |
| [references/plan_change.md](references/plan_change.md) | Step-by-step guide for the Plan & Schedule workflow | ✅ Tested (C22020) |
| [references/login_workflow.md](references/login_workflow.md) | HPSM login automation with LDAP retry handling | ✅ Tested |
| [references/hpsm_field_reference.md](references/hpsm_field_reference.md) | Complete field name attributes, dropdown values, and format specs | ⚠️ Partially verified |
