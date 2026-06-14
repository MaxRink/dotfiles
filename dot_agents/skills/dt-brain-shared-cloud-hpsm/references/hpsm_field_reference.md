# HPSM Field Reference

## Change Form Fields

| Field | HPSM `name` Attribute | Type | Required | Default |
|-------|----------------------|------|----------|---------|
| Title | `instance/header/brief.description` | text input | Yes | — |
| Change Requester - Group | `instance/panip.requested.by.group` | text input | Yes | — |
| Change Coordinator - Group | `instance/panip.change.coord.group` | text input | Yes | INFRA-CAAS-L2S |
| Requested End Date | `instance/requestedDate` | date input | Yes | — |
| Reason for Change | `instance/header/reason` | combo-text | Yes | — |
| Service | `instance/affected.item` | text input | Yes | CAAS_BM |
| Impact | `instance/initial.impact` | combo-text | Yes | — |
| Urgency | `instance/severity` | combo-text | Yes | — |
| Risk Assessment | `instance/header/risk.assessment` | combo-text | No (change form) | — |
| Description | `instance/description.structure/description/description` | hidden textarea | Yes | — |
| Effect of not Implementing | `instance/effect.not.impl/effect.not.impl` | hidden textarea | Yes | — |

## Plan & Schedule Form Fields

| Field | HPSM `name` Attribute | Type | Required | Default |
|-------|----------------------|------|----------|---------|
| Risk Assessment | `instance/header/risk.assessment` | combo-text | Yes | — |
| Scheduled Implementation Start | `instance/header/planned.start` | date input | Optional | — |
| Scheduled Implementation End | `instance/header/planned.end` | date input | Optional | — |
| Scheduled Downtime Start | `instance/middle/down.start` | date input | Optional | — |
| Scheduled Downtime End | `instance/middle/down.end` | date input | Optional | — |
| Change Coordinator | `instance/header/coordinator` | text input | Yes | — |
| Change Owner | `instance/change.owner` | text input | Yes | — |
| Change Owner Group | `instance/change.owner.Group` | text input | Yes | INFRA-CAAS-L2S |
| Assignment Group | `instance/header/assign.dept` | text input | Yes | INFRA-CAAS-L2S |
| Implementation Plan | `instance/description.structure/plan/plan` | hidden textarea | Yes | — |
| Remediation Plan | `instance/backout.plan/backout.plan` | hidden textarea | Yes | — |

## Search Form Fields

| Field | HPSM `name` Attribute | Type |
|-------|----------------------|------|
| Change ID | `instance/number` | text input |

Alternative name attributes (tried in order): `instance/header/number`, `header/number`, `number`

## Dropdown / Combo-Text Values

### Change Type

| CLI Value | HPSM Label |
|-----------|-----------|
| emergency | Emergency Change |
| normal | Normal Change |
| standard | Standard Change |

### Impact

| Value |
|-------|
| 1 - Enterprise |
| 2 - Site/Dept |
| 3 - Multiple Users |
| 4 - User |
| 5 - One Single Customer Complaint |

### Urgency

| Value |
|-------|
| 1 - Critical |
| 2 - High |
| 3 - Average |
| 4 - Low |
| 5 - Very Low |

### Reason for Change

| Value |
|-------|
| Maintenance |

### Risk Assessment

| Value |
|-------|
| 0 - No Risk |
| 1 - Low Risk |
| 2 - Some Risk |
| 3 - Moderate Risk |
| 4 - High Risk |
| 5 - Very High Risk |

## Date Format

HPSM expects dates in format: **DD/MM/YY HH:MM:SS**

Examples:
- `01/03/26 00:00:00` (March 1, 2026, midnight)
- `15/06/26 14:30:00` (June 15, 2026, 2:30 PM)

### Date Conversion from ISO

| ISO Input | HPSM Format |
|-----------|-------------|
| 2026-03-01 | 01/03/26 00:00:00 |
| 2026-03-01T14:30:00 | 01/03/26 14:30:00 |
| 01/03/26 | 01/03/26 00:00:00 |

## Field Types

### Text Input

Regular visible `<input>` elements. Fill using:

```bash
playwright-cli run-code "async page => {
  for (const frame of page.frames()) {
    const el = await frame.\$('[name=\"FIELD_NAME\"]');
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

### Combo-Text Input

Text inputs that also function as dropdown selectors (Reason, Impact, Urgency, Risk). Fill the same way as text inputs — type the exact value string.

### Hidden Textarea

Description-like fields behind rich-text editors. The underlying `<textarea>` is hidden. Fill via DOM manipulation:

```bash
playwright-cli run-code "async page => {
  for (const frame of page.frames()) {
    const result = await frame.evaluate((args) => {
      const ta = document.querySelector('textarea[name=\"' + args.name + '\"]');
      if (!ta) return null;
      ta.value = args.value;
      ta.dispatchEvent(new Event('input', { bubbles: true }));
      ta.dispatchEvent(new Event('change', { bubbles: true }));
      const parent = ta.closest('td') || ta.parentElement;
      if (parent) {
        const editable = parent.querySelector('[contenteditable=\"true\"]');
        if (editable) editable.innerHTML = args.value.replace(/\\n/g, '<br>');
        const iframe = parent.querySelector('iframe');
        if (iframe?.contentDocument?.body) iframe.contentDocument.body.innerHTML = args.value.replace(/\\n/g, '<br>');
      }
      return 'filled';
    }, { name: 'FIELD_NAME', value: 'VALUE' });
    if (result) return result;
  }
  return 'not found';
}"
```

### Date Input

Same as text input, but value must be in DD/MM/YY HH:MM:SS format. Wait 2-3 seconds after filling (HPSM date validation may trigger popups).

## Constants

| Constant | Value | Description |
|----------|-------|-------------|
| HPSM URL | `https://ttm.ioss-ttm.in.pan-net.eu:8443/sm/index.do?lang=en` | HPSM login page |
| Default Service | `CAAS_BM` | Default service for changes |
| Default Coordinator Group | `INFRA-CAAS-L2S` | Default change coordinator group |
| Target Assignment Group | `INFRA-CAAS-L2S` | Target group for incident scraping |
| Default Timeout | 60000 ms | Navigation timeout |
| Navigation Timeout | 90000 ms | Extended timeout for page loads |
| Viewport | 1920 × 1080 | Recommended browser viewport |

## Incident Table Columns

When scraping incidents, data is extracted in this column order (relative to the Incident ID column):

| Offset | Field |
|--------|-------|
| 0 | Incident ID (pattern: `IM\d+`) |
| +1 | Category |
| +2 | Alert Status |
| +3 | Status |
| +4 | Assignment Group |
| +5 | Assignee |
| +6 | Title |
| +7 | Description |
| +8 | Priority |
| +9 | Impact |
| +10 | Urgency |
| +11 | Parent Incident |
