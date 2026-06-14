# Scraping Incidents from HPSM Incident Queue

Workflow for scraping incidents assigned to an assignment group (default: **INFRA-CAAS-L2S**)
from the HPSM Incident Queue using `playwright-cli`.

## Automated Script

A Python script automates the full workflow (login → navigate → extract → output):

```bash
source .env && .venv/bin/python .claude/skills/cloud-hpsm/scripts/scrape_incidents.py [ASSIGNMENT_GROUP]
```

Options:
- `--format json` (default) — JSON array to stdout
- `--format table` — formatted table to stdout

Default assignment group: `INFRA-CAAS-L2S`.

## Prerequisites

- **VPN active** — HPSM is only accessible on the corporate network.
- **Logged in** — A `playwright-cli` browser session must already be authenticated
  to HPSM. Use the login workflow before running these steps.
- **Browser session open** — `playwright-cli` must have an active page pointing at the
  HPSM dashboard.

## Navigation Steps

Navigate from the HPSM dashboard to the Incident Queue through the sidebar.

The sidebar renders as an ARIA **tree** widget with `treeitem` elements. `playwright-cli snapshot`
flattens iframe boundaries, so sidebar items appear directly in the snapshot output.

```bash
# 1. Take a snapshot to see the navigation tree
playwright-cli snapshot
# Look for:
#   - treeitem " Incident Management" [ref=e345]

# 2. Click "Incident Management" to expand its sub-menu
playwright-cli click <ref>

# 3. Snapshot again to see the expanded sub-menu
playwright-cli snapshot
# Look for:
#   - treeitem "Incident Queue" [ref=e394]

# 4. Click "Incident Queue"
playwright-cli click <ref>

# 5. Wait for the queue to load (~8 seconds), then snapshot to confirm
#    The table takes time to populate — wait for "Record List" in snapshot
sleep 8
playwright-cli snapshot
```

> **Key insight**: Sidebar items are `treeitem` elements (not links). They expand/collapse
> on click and reveal nested items. The snapshot shows their state (e.g., `[expanded]`).

## Incident Queue Structure

The incident list is an **ExtJS treegrid** inside an iframe. The snapshot shows it as:

```
treegrid "Record List, Grouped by Assignment Group, Sorted by Incident ID Descending"
```

Incidents are grouped by assignment group. Each group header is a `level=1` row:
```
row "Level 1 Group, Assignment Group, INFRA-CAAS-L2S, 17 Items" [level=1] [ref=f2e106]
  gridcell "Level 1 Group, Assignment Group, INFRA-CAAS-L2S, 17 Items" [ref=f2e107]
```

Individual incidents are `level=2` rows under the expanded group.

## Expanding the Assignment Group

The group must be expanded to reveal individual incident rows.

```bash
# Find the group gridcell in the snapshot and click it
# Look for: gridcell "Level 1 Group, Assignment Group, INFRA-CAAS-L2S, N Items"
playwright-cli click <gridcell-ref>

# Wait for rows to render (~4 seconds)
sleep 4
playwright-cli snapshot
```

After expanding, the snapshot shows individual incident rows with full details.

## Extracting Incident Data

Data extraction uses `playwright-cli eval` on the treegrid element. This is more reliable
than `run-code` because the `eval` command automatically resolves the correct iframe.

### DOM Structure (ExtJS Grid)

The incident table is an ExtJS grid with this structure:
- **Grid body**: `.x-grid3-body`
- **Data rows**: `.x-grid3-row[aria-level="2"]` (level 1 = group headers, level 2 = data)
- **Cell values**: `.x-grid3-cell-inner` (ordered by column position)

### Column mapping (cell index)

| Index | Field            |
|-------|------------------|
| 0     | Checkbox         |
| 1     | Incident ID      |
| 2     | Category         |
| 3     | Alert Status     |
| 4     | Status           |
| 5     | Assignment Group |
| 6     | Assignee         |
| 7     | Title            |
| 8     | Description      |
| 9     | Priority         |
| 10    | Impact           |
| 11    | Urgency          |
| 12    | Parent           |
| 13    | Parent Incident  |
| 14    | Open Time        |
| 15    | VIP Flag         |

### Extraction command

```bash
# Find the treegrid ref in the snapshot (e.g., ref=f2e22)
# Then use eval to extract all level-2 rows:
playwright-cli eval 'el => {
  const body = el.querySelector(".x-grid3-body");
  if (!body) return JSON.stringify({ error: "No grid body found" });
  const rows = body.querySelectorAll(".x-grid3-row[aria-level=\"2\"]");
  const results = [];
  rows.forEach(r => {
    const cells = r.querySelectorAll(".x-grid3-cell-inner");
    if (cells.length > 14) {
      results.push({
        incidentId: cells[1]?.textContent?.trim() || "",
        category: cells[2]?.textContent?.trim() || "",
        alertStatus: cells[3]?.textContent?.trim() || "",
        status: cells[4]?.textContent?.trim() || "",
        assignmentGroup: cells[5]?.textContent?.trim() || "",
        assignee: cells[6]?.textContent?.trim() || "",
        title: cells[7]?.textContent?.trim() || "",
        description: cells[8]?.textContent?.trim() || "",
        priority: cells[9]?.textContent?.trim() || "",
        impact: cells[10]?.textContent?.trim() || "",
        urgency: cells[11]?.textContent?.trim() || "",
        parent: cells[12]?.textContent?.trim() || "",
        parentIncident: cells[13]?.textContent?.trim() || "",
        openTime: cells[14]?.textContent?.trim() || ""
      });
    }
  });
  return JSON.stringify(results, null, 2);
}' <treegrid-ref>
```

> **Why `eval` not `run-code`?** The `eval` command targets a specific snapshot ref, and
> playwright-cli automatically resolves the iframe containing that element. This avoids
> the need to manually iterate over `page.frames()` to find the right iframe.

## Output

The extraction returns a JSON array. Each element:

```json
{
  "incidentId": "IM145347",
  "category": "incident",
  "alertStatus": "Open",
  "status": "Work In Progress",
  "assignmentGroup": "INFRA-CAAS-L2S",
  "assignee": "v725309",
  "title": "[IC-HUBUDB3] openstack:ioss-mgmt-hubudb3:HeartBeat:missing",
  "description": "SOC received the following alarms...",
  "priority": "3 - Average",
  "impact": "3 - Multiple Users",
  "urgency": "3 - Average",
  "parent": "",
  "parentIncident": "",
  "openTime": "09/03/26 19:54:05"
}
```

Present the data as a table:

| Incident ID | Status | Assignee | Title | Priority | Open Time |
|-------------|--------|----------|-------|----------|-----------|

## Troubleshooting

### Group not visible in snapshot

The incident queue groups are lazy-loaded. If the target group doesn't appear:
- Wait longer (up to 15 seconds) after clicking Incident Queue
- The "Loading..." indicator appears while data is being fetched
- Snapshot again after the loading indicator disappears

### Group header shows 0 items

The assignment group has no open incidents. This is a valid state.

### eval returns empty array after expanding group

- Verify the group is actually expanded (snapshot shows `[expanded]` on the row)
- Wait 4+ seconds after clicking the group header — rows render asynchronously
- If the group collapsed (toggle behavior), click again to re-expand

### "No grid body found" error

The ExtJS grid hasn't fully rendered yet. Wait a few more seconds and retry.

### Sidebar items not visible

After login, the page title should show "CaaS | TDI Trouble Ticket" and the sidebar
should contain a tree with "Incident Management", "Change Management", etc.
If the sidebar is empty:
```bash
playwright-cli reload
sleep 5
playwright-cli snapshot
```

### Stale data

HPSM caches aggressively. To refresh:
```bash
playwright-cli reload
sleep 8
playwright-cli snapshot
# Re-navigate to Incident Queue
```
