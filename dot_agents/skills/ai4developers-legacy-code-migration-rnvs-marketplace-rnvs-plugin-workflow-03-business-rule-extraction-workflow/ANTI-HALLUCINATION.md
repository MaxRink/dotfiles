# Anti-Hallucination Checklist

Before finalizing ruletable.json:

- Every rule has verifiable `source_location` (file:line or flow:step)
- `source_evidence` directly quotes or accurately paraphrases source
- `confidence_score` based on evidence clarity, not assumptions
- No rules added based on "logical assumptions" or "should exist"
- All specialist skill references in `specialist_skills_consulted` actually consulted
- `validation_status` reflects actual user confirmation

**Red Flags** (DO NOT DO):
- Adding rules "because they logically should exist"
- Inflating confidence_score without source evidence
- Citing specialist skills not actually consulted
- Creating rules without source_location
- Marking "user_confirmed" without actual confirmation
