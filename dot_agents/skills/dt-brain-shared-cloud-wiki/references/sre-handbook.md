# SRE Handbook Structure (CKBSH space)

The SRE handbook lives in the `CKBSH` space. Key page IDs for navigation and creating child pages:

| Page | ID | URL |
|------|----|-----|
| SRE Handbook Home | `2042864578` | [link](https://wiki.telekom.de/pages/viewpage.action?pageId=2042864578) |
| Infrastructure | `2447606961` | [link](https://wiki.telekom.de/pages/viewpage.action?pageId=2447606961) |
| Baremetal | `2042864597` | [link](https://wiki.telekom.de/pages/viewpage.action?pageId=2042864597) |
| Baremetal - converged | `3243936180` | [link](https://wiki.telekom.de/pages/viewpage.action?pageId=3243936180) |
| Openstack | `2042864586` | [link](https://wiki.telekom.de/pages/viewpage.action?pageId=2042864586) |
| General - Runbooks | `2042864585` | [link](https://wiki.telekom.de/pages/viewpage.action?pageId=2042864585) |
| Alerts Handbook | `2042864583` | [link](https://wiki.telekom.de/pages/viewpage.action?pageId=2042864583) |
| Troubleshooting-Incidents-Ops | `2447606964` | [link](https://wiki.telekom.de/pages/viewpage.action?pageId=2447606964) |
| Troubleshooting: Baremetal | `2449278875` | [link](https://wiki.telekom.de/pages/viewpage.action?pageId=2449278875) |
| Customers | `2042864589` | [link](https://wiki.telekom.de/pages/viewpage.action?pageId=2042864589) |
| List of Clusters | `2042864592` | [link](https://wiki.telekom.de/pages/viewpage.action?pageId=2042864592) |

Example — create a page under Baremetal:
```bash
.venv/bin/python ${SKILL_DIR}/scripts/wiki-create-page.py \
  --title "Baremetal: My New Page" \
  --space CKBSH \
  --parent-id 2042864597 \
  --content-file content.html
```
