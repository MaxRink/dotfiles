# RNVS-Specific Extraction Patterns

RNVS domain-specific patterns for business rule extraction.

---

## PL/SQL Rule Extraction

PL/SQL packages (pack_body_*.sql, p_*.pks) contain most RNVS business logic.

**Common Rule Patterns**:

```sql
-- Validation with error code
IF p_tnb.get_operator(v_tnb_id) IS NULL THEN
  RAISE_APPLICATION_ERROR(-20002, 'RNBFM002: Invalid Operator Reference');
END IF;
```

**Extracted Rule**:
```json
{
  "rule_id": "NBM-BR-015",
  "rule_name": "Operator Validation Before RNB Assignment",
  "rule_description": "Operator must exist in TNB table before number block assignment",
  "source_location": "pack_body_rnb.sql:234",
  "source_evidence": "IF p_tnb.get_operator(v_tnb_id) IS NULL THEN RAISE RNBFM002",
  "error_code": "RNBFM002",
  "confidence_score": 5
}
```

---

## Specialist Skill Triggers

### porting-data-exchange-specialist

Consult when rules mention:
- PDA, Portierung, porting
- KCODE values (2100, 2500, 6000-series)
- AT/KT timing rules
- Carrier coordination

### rnvs-error-code-specialist

Consult when rules mention:
- ECRM codes (ECRMP, ERESP)
- PFM codes (porting workflow)
- RNBFM codes (number block)
- BFM/BHM codes (booking)

---

## RNVS Rule Group Prefixes

| Prefix | Domain | Example |
|--------|--------|---------|
| NBM- | Number Block Management | NBM-BR-001 |
| PDA- | Porting Data Exchange | PDA-BR-001 |
| TNB- | Operator Management | TNB-BR-001 |
| CRM- | CRM Integration | CRM-BR-001 |
| KCODE- | KCODE Processing | KCODE-BR-001 |

---

## Extraction Priority

1. **pack_body_*.sql** - Package bodies with business logic
2. **p_*.pks** - Package specifications (interfaces)
3. ***Manager.cpp** - C++ orchestration
4. ***_processor.tcl** - TCL integration scripts
