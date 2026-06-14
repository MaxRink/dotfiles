# Plan & Schedule Change — HPSM Workflow Reference

This document describes how to plan and schedule an existing HPSM change using `playwright-cli`.
**Verified** on 2026-03-11 (full workflow tested on C22020 — all fields filled and saved successfully).

There are two entry points:

- **Workflow A (Standalone)**: Search for an existing change by ID → Request Plan and Schedule → Fill form → Save
- **Workflow B (Combined)**: After creating a new change (detail page still open) → Click "Request Plan and Schedule" directly → Fill form → Save

---

## 1. Prerequisites

- HPSM must be open in the browser and the user must be logged in
- `playwright-cli` must be connected to the browser session
- The change must already exist (created beforehand)
- For Workflow A: you need the Change ID (e.g., `C22020`)

---

## 2. Required Information

All fields the user must provide (or that must be set to defaults):

| Field | Required | Example Value | Location |
|-------|----------|---------------|----------|
| Risk Assessment | Yes | `1 - Low Risk` | Main form (combobox) |
| Change Coordinator | Yes | `q831050` | Main form (text) |
| Change Owner | Yes | `q831050` | Main form (text) |
| Change Owner Group | Yes | `INFRA-CAAS-L2S` | Main form (text) |
| Assignment Group | Yes | `INFRA-CAAS-L2S` | Main form (text) |
| Assignee | Yes | `q831050` | Main form (text) |
| Scheduled Implementation Start | Yes | `01/03/26 00:00:00` | "Change Details" tab |
| Scheduled Implementation End | Yes | `01/03/26 06:00:00` | "Change Details" tab |
| Scheduled Downtime Start | No | `01/03/26 01:00:00` | "Change Details" tab |
| Scheduled Downtime End | No | `01/03/26 05:00:00` | "Change Details" tab |
| Implementation Plan | Yes | Multi-line text | "Change Details" tab (click-to-activate) |
| Remediation Plan | Yes | Multi-line text | "Change Details" tab (click-to-activate) |

### Snapshot Element Names (Tested)

From a live snapshot of the Plan and Schedule phase:

```
# Main form fields
combobox "Risk Assessment" [ref=XXX]
textbox "Change Coordinator" [ref=XXX]
textbox "Change Owner" [ref=XXX]
textbox "Change Owner Group" [ref=XXX]
textbox "Assignment Group" [ref=XXX]
textbox "Assignee" [ref=XXX]
checkbox "Review Required" [ref=XXX]

# "Change Details" tab fields
textbox "Scheduled Implementation Start" [ref=XXX]
textbox "Scheduled Implementation End" [ref=XXX]
textbox "Scheduled Downtime Start" [ref=XXX]
textbox "Scheduled Downtime End" [ref=XXX]
generic "Implementation Plan" → paragraph [ref=XXX]   ← click-to-activate
generic "Remediation Plan" → paragraph [ref=XXX]       ← click-to-activate
```

### Date Format

HPSM expects: **DD/MM/YY HH:MM:SS**

| ISO Input | HPSM Format |
|-----------|-------------|
| 2026-03-01 | 01/03/26 00:00:00 |
| 2026-03-01T14:30:00 | 01/03/26 14:30:00 |

### Risk Assessment Options

| Value |
|-------|
| 0 - No Risk |
| 1 - Low Risk |
| 2 - Some Risk |
| 3 - Moderate Risk |
| 4 - High Risk |
| 5 - Very High Risk |

---

## 3. Workflow A: Plan an Existing Change

Full flow: Navigate to search → Find change → Open it → Click Plan and Schedule → Fill form → Save.

### Step 1: Search for the Change

See [Section 5: Searching for a Change](#5-searching-for-a-change).

### Step 2: Click Plan and Schedule

See [Section 6: Clicking Plan and Schedule](#6-clicking-plan-and-schedule).

### Step 3: Fill the Plan Form

See [Section 7: Filling the Plan Form](#7-filling-the-plan-form).

### Step 4: Save

See [Section 9: Saving the Plan](#9-saving-the-plan).

---

## 4. Workflow B: Plan After Creating a Change

When a change was just created and the detail page is still open, skip the search step.

### Step 1: Click Plan and Schedule

The change detail page should already be showing. Click "Plan and Schedule" directly.

See [Section 6: Clicking Plan and Schedule](#6-clicking-plan-and-schedule).

### Step 2: Fill the Plan Form

See [Section 7: Filling the Plan Form](#7-filling-the-plan-form).

### Step 3: Save

See [Section 9: Saving the Plan](#9-saving-the-plan).

---

## 5. Searching for a Change (Tested)

### Navigate to Search Changes

```bash
# Take snapshot, find and click "Change Management" treeitem
playwright-cli snapshot
playwright-cli click <change_mgmt_ref>

# Wait 2s, take snapshot, find and click "Search Changes" treeitem
playwright-cli snapshot
playwright-cli click <search_changes_ref>
```

Wait 5s for the search form to load, then take a snapshot.

### Fill the Change ID and Search

In the snapshot, find `textbox "Change ID"` and fill it:

```bash
playwright-cli snapshot
# Find: textbox "Change ID" [ref=XXX]
playwright-cli fill <ref> "C22020"
playwright-cli press Enter
```

Wait 5s for the change detail to load.

### Verify Change Loaded

Take a snapshot and check for:
- Page title: `Change CXXXXX - Prompt | TDI Trouble Ticket`
- `textbox "Phase"` showing the current phase
- `textbox "Title"` showing the change title

---

## 6. Clicking "Request Plan and Schedule" (Tested)

The button text is **"Request Plan and Schedule"** (not just "Plan and Schedule").
It's a `button` element in the top toolbar (outside the iframe).

```bash
playwright-cli snapshot
# Find: button "Request Plan and Schedule" [ref=XXX]
playwright-cli click <ref>
```

Wait 5s for the phase transition. The Phase field changes from
`Registration and Categorization` to `Plan and Schedule`.

**After clicking**, the form now shows:
- New required fields: Change Coordinator, Change Owner, Assignment Group, Assignee, Risk Assessment
- The toolbar button changes to **"Deployment confirmation"**
- A **"Change Details"** tab appears with schedule and plan fields

Take a new snapshot to see the updated form.

---

## 7. Filling the Plan Form (Tested Approach)

The plan form has fields in **two areas**:
1. **Main form** (visible immediately): Change Coordinator, Owner, Groups, Assignee, Risk Assessment
2. **"Change Details" tab**: Schedule dates, Implementation Plan, Remediation Plan

### Step 1: Fill Main Form Fields

Take a snapshot and fill the text fields using refs:

```bash
playwright-cli snapshot

# Fill Change Coordinator (textbox)
playwright-cli fill <coordinator_ref> "q831050"
playwright-cli press Tab

# Fill Change Owner (textbox)
playwright-cli fill <owner_ref> "q831050"
playwright-cli press Tab

# Fill Change Owner Group (textbox) — if visible
playwright-cli fill <owner_group_ref> "INFRA-CAAS-L2S"
playwright-cli press Tab

# Fill Assignment Group (textbox)
playwright-cli fill <assignment_group_ref> "INFRA-CAAS-L2S"
playwright-cli press Tab

# Fill Assignee (textbox)
playwright-cli fill <assignee_ref> "q831050"
playwright-cli press Tab

# Fill Risk Assessment (combobox — use fill + Tab)
playwright-cli fill <risk_ref> "1 - Low Risk"
playwright-cli press Tab
```

### Step 2: Click "Change Details" Tab

The schedule and plan fields are on the "Change Details" tab.

```bash
playwright-cli snapshot
# Find: tab "Change Details" [ref=XXX]
playwright-cli click <ref>
```

Wait 2s and take a new snapshot.

### Step 3: Fill Date Fields

Date fields are textboxes with calendar icons. Use `fill` + `Tab`:

```bash
playwright-cli snapshot

# Scheduled Implementation Start (required)
playwright-cli fill <impl_start_ref> "01/03/26 00:00:00"
playwright-cli press Tab

# Scheduled Implementation End (required)
playwright-cli fill <impl_end_ref> "01/03/26 06:00:00"
playwright-cli press Tab

# Scheduled Downtime Start (optional)
playwright-cli fill <downtime_start_ref> "01/03/26 01:00:00"
playwright-cli press Tab

# Scheduled Downtime End (optional)
playwright-cli fill <downtime_end_ref> "01/03/26 05:00:00"
playwright-cli press Tab
```

**Important**: After filling date fields, HPSM may show validation popups. If a popup appears, dismiss it by clicking OK.

### Step 4: Fill Implementation Plan (Click-to-Activate)

Implementation Plan uses the same click-to-activate pattern as Description:

```bash
playwright-cli snapshot
# Find: paragraph [ref=XXX] under "Implementation Plan" label
# Click the paragraph to activate it:
playwright-cli click <paragraph_ref>
# Wait 1s, then snapshot — it should now be a textbox:
playwright-cli snapshot
# Find: textbox [ref=XXX] (the activated field)
playwright-cli fill <textbox_ref> "Step 1: Prepare environment\nStep 2: Execute change\nStep 3: Verify"
playwright-cli press Tab
```

### Step 5: Fill Remediation Plan (Click-to-Activate)

Same pattern as Implementation Plan:

```bash
playwright-cli snapshot
# Find: paragraph [ref=XXX] under "Remediation Plan" label
playwright-cli click <paragraph_ref>
playwright-cli snapshot
# Find: textbox [ref=XXX]
playwright-cli fill <textbox_ref> "Step 1: Revert changes\nStep 2: Restore previous state\nStep 3: Verify rollback"
playwright-cli press Tab
```

---

## 8. Saving the Plan

### Click Save

The Save button is in the top toolbar (outside the iframe):

```bash
playwright-cli snapshot
# Find: button "Save" [ref=XXX]  (NOT "Save & Exit")
playwright-cli click <save_ref>
```

Wait 5s and take a snapshot to verify.

### Check for Validation Errors

If HPSM shows an alert or error banner, the snapshot will show it. Common issues:
- Missing required fields
- Invalid date range (end before start)
- Invalid user ID

### Verify Save Succeeded

Take a snapshot and confirm:
- No error banners visible
- Phase still shows "Plan and Schedule"
- The toolbar now shows **"Deployment confirmation"** button (next phase)

---

## 9. Next Phase: Deployment Confirmation

After saving the Plan and Schedule, the next toolbar button is **"Deployment confirmation"**.
This advances the change to the next phase in the HPSM workflow.

**This step has NOT been tested yet.** Use with caution.

---

## 10. Key Learnings (from C22020 test)

1. **Remediation Plan auto-activates**: After filling Implementation Plan and pressing Tab, the Remediation Plan field may already be an active `textbox` — no need to click the `paragraph` first.
2. **After save, the form refreshes**: All element refs change after save. Take a new snapshot if you need to interact further.
3. **Save keeps the form open**: The `Save` button (not `Save & Exit`) keeps the change detail page visible for further actions.
4. **"Deployment confirmation" persists**: The button remains available after save — it doesn't auto-advance.
5. **Change Coordinator Group auto-fills**: When you fill Change Coordinator, the Coordinator Group may auto-populate from the user's profile. Check before filling manually.
6. **Field fill order matters**: Fill text fields (Coordinator, Owner, Groups, Assignee) before Risk Assessment. Fill main form fields before switching to Change Details tab.

---

## 10. Troubleshooting

### "Request Plan and Schedule" Button Not Found

**Possible causes:**
1. Change is already in Plan and Schedule phase — check the Phase field
2. Change is in a state that doesn't allow planning (closed, cancelled)
3. Try taking a fresh snapshot and searching for `button` elements with "plan" or "schedule" text

### Date Validation Popup

After filling date fields, HPSM may show a popup. Take a snapshot — if a dialog or alert is visible, click OK or Close.

### Implementation/Remediation Plan Won't Activate

If clicking the `paragraph` element doesn't convert it to a `textbox`, try:
1. Wait longer (2-3s) before taking the follow-up snapshot
2. Click the generic container above the paragraph, then click the paragraph itself
3. As fallback, use `run-code` with DOM manipulation (see `create_change.md` for the Description field pattern)

### Field Not Found After Phase Transition

After clicking "Request Plan and Schedule", some fields may not appear immediately. Wait 3-5s and take a fresh snapshot. If still missing, click "Change Details" tab.

### Save Fails with Validation Error

Common missing fields in Plan and Schedule:
- Change Coordinator
- Change Owner / Change Owner Group
- Assignment Group / Assignee
- Risk Assessment
- Implementation Plan
- Remediation Plan
- Scheduled Implementation Start / End

All fields marked with red `*` are required. Take a snapshot to identify which fields are empty.
