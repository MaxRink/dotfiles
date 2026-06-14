# CID Useful Queries Reference

## By Epic Status
```bash
# Epics currently in implementation
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --labels "B - epic::Doing"

# Epics ready for sprint planning
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --labels "B - epic::ToDo"

# Epics in design/sizing phase
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --labels "B - epic::Refinement"
```

## By Squad
```bash
# DC Infrastructure squad epics
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --labels "A - DC_squad"

# Networks squad epics
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --labels "A - Networks_squad"

# CDM squad epics
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --labels "A - CDM_squad"
```

## By Datacenter/Environment
```bash
# Slovakia deployments (all locations)
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --country SK --verbose --sort-by due_date

# Hungary deployments
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --country Hungary --verbose

# Multiple countries (Slovakia and Hungary)
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --country "SK,HU" --verbose --sort-by due_date

# Specific environment label
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --labels "E - IC-ATVIEF1"

# Search by city name
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --search "Budapest"
```

## By Work Category
```bash
# Design work
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --labels "I - DESIGN"

# Ordering/procurement
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --labels "I - ORDER & PROCURE"

# Hardware installation
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --labels "I - SITE READINESS"
```

## Combining Filters
```bash
# DC squad epics in implementation
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --labels "A - DC_squad,B - epic::Doing"

# High priority epics
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --labels "D - 2 - high"
```

## By Assignee
```bash
# Filter by delivery manager (partial name)
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --assignee "Angel"

# Combine assignee + country
.venv/bin/python ${SKILL_DIR}/scripts/cid-list-epics.py --assignee "Angel" --country SK
```
