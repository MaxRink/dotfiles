# RNVS-Specific Enrichment Patterns

Domain-specific skill triggers and enrichment patterns for Phase 4 business documentation.

---

## Specialist Skill Triggers

### porting-data-exchange-specialist

**Consult when rule mentions**:
- PDA, Portierung, porting
- KCODE values (20, 2100, 2500, 6000-series)
- AT/KT timing rules
- Carrier coordination, TNB

**Business context provided**:
- KCODE business meanings and BNetzA compliance rationale
- Porting timeline business requirements (8-day window, AT deadlines)
- PDA regulatory framework from BNetzA

### rnvs-error-code-specialist

**Consult when rule mentions**:
- ECRM codes (ECRMP, ERESP)
- PFM codes (porting workflow)
- RNBFM codes (number block)
- BFM/BHM codes (booking)

**Business context provided**:
- Error code business impact
- Recovery workflow business rationale
- Stakeholder responsibility for error resolution

### german-glossary

**Consult when rule mentions**:
- Rufnummernblock (Number Block)
- Eigentuemerwechsel (Ownership Transfer)
- Bereichsinformation (Area Information)
- Kontingent (Contingent/Quota)

**Business context provided**:
- German-English translation
- Business terminology for stakeholders
- Domain-specific context

---

## Stakeholder Derivation from RNVS Domains

| Rule Domain | Business Owner | Technical Owner | Regulatory Authority |
|-------------|---------------|-----------------|---------------------|
| Number Block (NBM-, RNB-) | Number Resource Management | RNVS RNB Team | BNetzA |
| Porting (PDA-, PORT-) | Porting Operations | Porting Development | BNetzA |
| CRM Integration (CRM-, ECRM-) | Customer Relations | CRM Integration Team | - |
| Booking (BFM-, BHM-) | Billing/Finance | Booking Development | - |
| Validation (VAL-) | Quality Assurance | Development Team | - |

---

## RNVS Business Process Templates

### Number Block Assignment (KCODE 20-26)

**Business Objective Pattern**:
"Ensure number block assignments from BNetzA comply with regulatory requirements and prevent allocation conflicts"

**Regulatory Rationale Pattern**:
"BNetzA regulatory requirement for number block management. KCODE ${CODE} is the official message type for ${PURPOSE} as defined in PDA specification section ${SECTION}"

### Porting Workflow (PDA)

**Business Objective Pattern**:
"Enable customers to transfer telephone numbers between carriers while maintaining regulatory compliance with BNetzA porting requirements"

**Regulatory Rationale Pattern**:
"BNetzA number portability regulation. ${TIMING} deadline ensures carrier coordination within regulatory timeframe"

---

## When Skill Provides No Context

If specialist skill cannot provide business context:

1. Mark as: `"Requires stakeholder clarification"`
2. Use rule category default stakeholder (see table above)
3. Flag for user validation in Step 6
