# Site and Country Reference

## Country Codes

Use country names or ISO codes with the `--site` parameter:

| Code | Country | Example Sites |
|------|---------|---------------|
| AT | Austria | ATGRAD001, ATSALD001, ATVIED001 |
| SK | Slovakia | SKBRAD003, SKKOSD001 |
| DE | Germany | DEBAMD001, DEFRAD001 |
| CZ | Czechia | CZBRND001, CZPRAD001, CZPRAD002 |
| HU | Hungary | HUBUDD001, HUBUDD002, HUBUDD003 |
| HR | Croatia | HRRIJD001, HRSPID001, HRVARD001, HRZAGD001 |
| PL | Poland | PLKRAD001, PLPOZD001, PLWARD001 |
| MK | N. Macedonia | MKSKOD001, MKSTRD001 |
| ME | Montenegro | MEBJED001, MEPODD001 |
| US | USA | USDALD001 |

## Site Naming Convention

Site codes follow the pattern: `{COUNTRY}{CITY}{TYPE}{NUMBER}`

- **Country**: 2-letter ISO code
- **City**: 3-letter city abbreviation
- **Type**: D = Datacenter
- **Number**: 3-digit sequence (001, 002, etc.)

## Usage Examples

```bash
# Filter by country code
.venv/bin/python ${SKILL_DIR}/scripts/netbox-list-clusters.py --site SK

# Filter by country name
.venv/bin/python ${SKILL_DIR}/scripts/netbox-list-clusters.py --site slovakia

# Filter by exact site
.venv/bin/python ${SKILL_DIR}/scripts/netbox-list-clusters.py --site SKBRAD003
```

## Group Names

Group names are **case-sensitive**:
- Use `CaaS` (not `caas`)
- Use `STaaS` (not `staas`)
