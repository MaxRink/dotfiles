# HPSM — Create Change Request Workflow

Complete workflow for creating a change request in HPSM using `playwright-cli`.
**Tested and verified** on 2026-03-10 (Standard Change).

---

## 1. Prerequisites

- Must already be logged in to HPSM (see `login_workflow.md`).
- A browser session must be active with `playwright-cli` connected.
- The HPSM dashboard must be visible (post-login landing page).
- Use `--headed` flag with `playwright-cli open` to see the browser during execution.

---

## 2. Required Information

The following information is needed to create a change request:

| Field | Required | Example |
|---|---|---|
| Change Type | Yes | `normal`, `emergency`, or `standard` |
| Title | Yes | `"Upgrade CAAS cluster node firmware"` |
| Requester Group | Yes | `"INFRA-CAAS-L2S"` |
| Coordinator Group | Yes | Default: `INFRA-CAAS-L2S` |
| Requested End Date | Yes | `"01/03/26 00:00:00"` (DD/MM/YY HH:MM:SS) |
| Reason for Change | Yes | `"Maintenance"` |
| Service | Yes | Default: `CAAS_BM` |
| Impact | Yes | e.g. `"4 - User"` |
| Urgency | Yes | e.g. `"4 - Low"` |
| Description | Yes | Free text describing the change |
| Effect of not Implementing | Yes | Free text explaining risk of not doing it |

### Dropdown / Combo-Text Values

**Impact** (combo-text field — use `fill` then `press Tab`, NOT `select`):
- `1 - Enterprise`
- `2 - Site/Dept`
- `3 - Multiple Users`
- `4 - User`
- `5 - One Single Customer Complaint`

**Urgency** (combo-text field — use `fill` then `press Tab`, NOT `select`):
- `1 - Critical`
- `2 - High`
- `3 - Average`
- `4 - Low`
- `5 - Very Low`

**Reason for Change** (combo-text field):
- `Maintenance` (most common for CaaS)

> **IMPORTANT**: Combobox fields are `<input>` elements, NOT `<select>` elements.
> Using `playwright-cli select` will fail with "Element is not a \<select\> element".
> Always use `playwright-cli fill <ref> <value>` followed by `playwright-cli press Tab`.

---

## 3. Navigation (Tested)

### Step 1: Open Change Management

From the HPSM dashboard sidebar, take a snapshot and find the treeitem:

```bash
playwright-cli snapshot
# Find: treeitem " Change Management" [ref=XXX]
playwright-cli click <ref>
```

Wait 2s, then take another snapshot to see the expanded sub-menu.

### Step 2: Click "Create New Change"

```bash
# Find: treeitem "Create New Change" [ref=XXX]
playwright-cli click <ref>
```

Wait 5s for the "Select Change Model" dialog to load.

---

## 4. Selecting Change Type (Tested)

After clicking "Create New Change", a **"Select Change Model"** dialog appears with a grid listing three models. Each model is a link in a gridcell:

```
grid "Change Model":
  row "Emergency Change ...":
    gridcell: link "Emergency Change" [ref=XXX]
  row "Normal Change ...":
    gridcell: link "Normal Change" [ref=XXX]
  row "Standard Change ...":
    gridcell: link "Standard Change" [ref=XXX]
```

Take a snapshot and click the appropriate link ref:

```bash
playwright-cli snapshot
# Find: link "Standard Change" [ref=XXX]
playwright-cli click <ref>
```

Wait 5s for the form to fully render. A Change ID is auto-assigned (e.g., `C22016`).

---

## 5. Filling the Form (Tested — Snapshot-Based Approach)

Use `playwright-cli snapshot` to identify field refs, then `fill` each field by ref.
This is simpler and more reliable than the `run-code` approach.

After filling **each** combo-text field, press Tab to trigger HPSM server-side validation:
```bash
playwright-cli press Tab
```

### Field Reference (from live snapshot)

| UI Label | Snapshot Element | Type |
|---|---|---|
| Title | `textbox "Title"` | text — `fill` |
| Change Requester - Group | `textbox "Change Requester - Group"` | text — `fill` |
| Impact | `combobox "Impact"` | combo — `fill` + Tab |
| Urgency | `combobox "Urgency"` | combo — `fill` + Tab |
| Requested End Date | `textbox "Requested End Date"` | text — `fill` + Tab |
| Reason for Change | `combobox "Reason for Change"` | combo — `fill` + Tab |
| Service | `textbox "Service"` | text — `fill` + Tab |
| Change Coordinator Group | `textbox "Change Coordinator Group"` | text — `fill` + Tab |
| Description | paragraph → `textbox "Description"` | click-to-activate — see below |
| Effect of not Implementing | paragraph → `textbox "Effect of not Implementing"` | click-to-activate — see below |

### Auto-Populated Fields (read-only)

These are filled automatically by HPSM:
- **Change ID**: Auto-assigned (e.g., `C22016`)
- **Change Requester**: Set from logged-in user (e.g., `q831050`)
- **Phase**: Set to `Registration and Categorization`
- **Category**: Set based on change model (e.g., `New Standard Change`)
- **Change Model**: Set from model selection (e.g., `Standard Change`)

### Fill Example (Standard Change)

```bash
# 1. Take snapshot to get field refs
playwright-cli snapshot

# 2. Fill Title
playwright-cli fill <title_ref> "Upgrade CAAS cluster node firmware"
playwright-cli press Tab

# 3. Fill Change Requester - Group
playwright-cli fill <group_ref> "INFRA-CAAS-L2S"
playwright-cli press Tab

# 4. Fill Impact (combobox — NOT select!)
playwright-cli fill <impact_ref> "4 - User"
playwright-cli press Tab

# 5. Fill Urgency (combobox — NOT select!)
playwright-cli fill <urgency_ref> "4 - Low"
playwright-cli press Tab

# 6. Fill Requested End Date
playwright-cli fill <date_ref> "31/03/26 00:00:00"
playwright-cli press Tab

# 7. Fill Reason for Change (combobox)
playwright-cli fill <reason_ref> "Maintenance"
playwright-cli press Tab

# 8. Fill Service
playwright-cli fill <service_ref> "CAAS_BM"
playwright-cli press Tab

# 9. Fill Change Coordinator Group
playwright-cli fill <coord_ref> "INFRA-CAAS-L2S"
playwright-cli press Tab
```

### Dismiss HPSM Popups After Each Field

After pressing Tab on any field, HPSM may show a validation popup. Take a snapshot and look for:
```
dialog "..." → button "OK" or button "Yes"
```
Click the button to dismiss if present.

---

## 6. Handling Description & Effect Fields (Tested — Click-to-Activate)

The **Description** and **Effect of not Implementing** fields initially appear as `paragraph` elements in the snapshot. They are NOT directly editable — you must **click** the paragraph to activate the textbox editor.

### Approach (Verified)

1. Find the `paragraph` ref inside the Description/Effect container
2. Click it — it transforms into a `textbox` with an `[active]` tag
3. Take a new snapshot to get the textbox ref
4. Fill the textbox using `playwright-cli fill`

### Fill Description

```bash
# Snapshot shows:
#   generic "Description":
#     paragraph [ref=XXX]          ← click this
#     img "Required Field"
playwright-cli click <paragraph_ref>

# After clicking, re-snapshot shows:
#   textbox "Description" [active] [ref=YYY]   ← fill this
playwright-cli snapshot
playwright-cli fill <textbox_ref> "Description text here"
```

### Fill Effect of not Implementing

```bash
# Same pattern — click the paragraph, then fill the textbox
playwright-cli click <effect_paragraph_ref>
playwright-cli snapshot
playwright-cli fill <effect_textbox_ref> "Effect text here"
```

> **Key Learning**: Do NOT use `run-code` with hidden textarea JavaScript.
> The click-to-activate approach is simpler and fully works with `playwright-cli fill`.

---

## 7. Saving the Change

### Click Save

The Save button is in the top toolbar (outside the iframe). Take a snapshot and find:
```
button "Save Record (Ctrl+Shift+F4)" [ref=XXX]: Save
```

```bash
playwright-cli snapshot
playwright-cli click <save_ref>
```

Wait 5s for HPSM to process the save.

> **IMPORTANT**: Do NOT click "Save & Exit" (`button "Save Record and Exit (Ctrl+Shift+F2)"`).
> Use the exact "Save" button.

### Cancel Without Saving

To cancel and discard the change:
```
button "Exit Record without Saving (Alt+F3)" [ref=XXX]: Cancel
```

```bash
playwright-cli click <cancel_ref>
```

A **"Question Alert"** dialog appears asking to confirm:
```
dialog "Question Alert":
  heading "Question"
  button "Yes" [ref=XXX]
```

Click "Yes" to confirm the cancellation.

> **WARNING**: HPSM may still create the Change ID and show a "Prompt" screen
> even after cancellation. You may need to click Cancel again on the prompt
> to fully exit.

### Extract Change ID

The Change ID is auto-assigned when the form loads and visible in:
```
textbox "Change ID" [ref=XXX]: C22016
```

Or from the page heading:
```
generic "Change - C22016"
```

---

## 8. After Saving

Once saved successfully:

- The change request is now **open** in HPSM with the returned Change ID (e.g., `C000001234567`).
- The change is in initial status and can proceed to **Plan & Schedule** phase.
- The Change ID can be used to search for and reopen the change later.
- Additional phases (Plan & Schedule, Implement, Review) are separate workflows.

---

## 9. Troubleshooting

### Combobox Fields Failing with "Element is not a \<select\>"

HPSM combobox fields (Impact, Urgency, Reason) are `<input>` elements styled as dropdowns.
Using `playwright-cli select <ref> <value>` will fail. Always use:
```bash
playwright-cli fill <ref> "<value>"
playwright-cli press Tab
```

### Field Not Found in Snapshot

HPSM uses nested iframes. Field refs will have prefixes like `f2e` (iframe content)
vs `e` (top-level page). If a field is not found:
- The form may not have fully loaded — wait and re-snapshot
- The change type dialog may still be open
- Try scrolling with `run-code` to make elements visible

### Description / Effect Fields Not Editable

These fields initially appear as `paragraph` elements, not textboxes.
**Click the paragraph first** to activate the textbox editor, then re-snapshot.

### HPSM Validation Popups

After pressing Tab on any field, HPSM may show a validation popup.
Take a snapshot and look for `dialog` or `button "OK"` / `button "Yes"` elements.

### Cancel Creates a Change Anyway

HPSM may auto-save the Change ID when the form loads. Clicking Cancel may show
a "Prompt" screen with the change still registered. You may need to click Cancel
again on the prompt page.

### Date Format Rejected

HPSM expects dates in **DD/MM/YY HH:MM:SS** format. Examples:
- `01/03/26 00:00:00` → March 1, 2026 at midnight
- `15/06/25 14:30:00` → June 15, 2025 at 2:30 PM

### Using `--headed` for Debugging

Open the browser with `--headed` to see what's happening:
```bash
playwright-cli open --headed "https://ttm.ioss-ttm.in.pan-net.eu:8443/sm/index.do?lang=en"
```
