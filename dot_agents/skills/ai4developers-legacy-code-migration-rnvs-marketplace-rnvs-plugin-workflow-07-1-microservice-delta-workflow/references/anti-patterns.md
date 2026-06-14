# Common Anti-Patterns and Fixes

**Purpose**: Document common mistakes when designing microservice changes and how to fix them.

**Context**: Phase 7.1 delta model design has specific pitfalls that can reduce quality or cause implementation issues.

---

## ❌ Anti-Pattern 1: Treating Phase 7.1 Like Phase 7

**Mistake**: Designing full microservice specifications instead of delta model (changes only).

**Symptoms**:
- Output includes complete API catalog (all endpoints, not just new/modified)
- Full database schema included (all tables, not just new/changed)
- Massive JSON file (30K-50K tokens like Phase 7)

**Why It's Wrong**:
- Delta model should be 5K-10K tokens (focused on changes)
- Reviewers can't easily see what changed
- Implementation teams waste time identifying actual changes

**Fix**:
✅ Output ONLY changes:
- `endpoints_to_add` (not complete endpoint list)
- `tables_to_add` (not full database schema)
- `topics_to_add` (not complete event catalog)

✅ Reference Phase 6 baseline for context:
- "Adding endpoint X to existing service Y (see Phase 6 for current endpoints)"

**Example**:
```json
{
  "api_changes": {
    "endpoints_to_add": [
      {"path": "/new-endpoint", "method": "POST"}
    ]
  }
}
```

NOT:
```json
{
  "api_catalog": {
    "all_endpoints": [
      {"path": "/existing-1", "method": "GET"},
      {"path": "/existing-2", "method": "POST"},
      {"path": "/new-endpoint", "method": "POST"}
    ]
  }
}
```

---

## ❌ Anti-Pattern 2: Writing Entire Delta Model in One Write Operation

**Mistake**: Attempting to write complete microservice-changes-design.json in single Write tool call.

**Symptoms**:
- Token limit failures (output exceeds 10K-20K tokens)
- No progress visibility (all-or-nothing)
- Cannot recover from failures

**Why It's Wrong**:
- Delta model with complete specifications easily exceeds token limits
- No incremental validation possible
- Wasted work if operation fails

**Fix**:
✅ Use progressive building strategy:
1. **Write skeleton** with metadata and empty arrays
2. **Edit to add api_changes** (batch endpoints by type)
3. **Edit to add database_changes** (tables, then columns, then indexes)
4. **Edit to add event_changes** (topics, then subscriptions)
5. **Edit to add state_machine_changes**
6. **Edit to add dependency_changes**

✅ Each Edit operation:
- Stays under 10K tokens
- Provides progress visibility
- Allows incremental validation

See `progressive-building-guide.md` for detailed strategy.

---

## ❌ Anti-Pattern 3: Missing RNVS Source Attribution

**Mistake**: Not providing traceability to RNVS legacy code.

**Symptoms**:
- No `maps_from` or `source` fields in changes
- Cannot verify correctness against legacy system
- Lost context for future maintenance

**Why It's Wrong**:
- Migration teams cannot verify delta matches RNVS functionality
- Business logic may be missed
- No audit trail for compliance

**Fix**:
✅ Every change must have RNVS source attribution:

**API endpoints**:
```json
{
  "maps_from": {
    "rnvs_component": "PortierungsService",
    "rnvs_function": "erstellePortierungsantrag",
    "rnvs_file": "src/de/telekom/rnvs/portierung/PortierungsService.java:234"
  }
}
```

**Database tables**:
```json
{
  "source": {
    "rnvs_table": "PORTIERUNGSANTRAEGE",
    "rnvs_file": "database/schema/rnvs_tables.sql:456",
    "mapping_notes": "RNVS table was denormalized. VNRM version normalizes with FK."
  }
}
```

**Events**:
```json
{
  "source": {
    "rnvs_trigger": "AFTER INSERT ON PORTIERUNGSANTRAEGE",
    "rnvs_file": "triggers/portierung_created_trigger.sql:23"
  }
}
```

---

## ❌ Anti-Pattern 4: Incomplete API Endpoint Specifications

**Mistake**: Adding endpoints without complete OpenAPI 3.0 specifications.

**Symptoms**:
- Missing request/response schemas
- Only success status code (200), no error codes
- No business rule mapping
- Generic descriptions

**Why It's Wrong**:
- Incomplete specs cause implementation ambiguity
- Error handling not defined
- Business rules not enforced

**Fix**:
✅ Every `endpoints_to_add` must include:
- **Path and method**: RESTful resource paths
- **Description**: Clear business purpose
- **Request schema**: All parameters (path, query, body)
- **Response schemas**: ALL status codes (200, 400, 401, 403, 404, 409, 500)
- **Business rules**: Mapped to Phase 3 BR-XXX identifiers
- **Authentication**: Requirements and scopes
- **RNVS source**: Legacy code attribution

See `patterns/api-delta-patterns.md` for complete template.

---

## ❌ Anti-Pattern 5: Missing Resilience Patterns for Dependencies

**Mistake**: Adding service dependencies without resilience patterns.

**Symptoms**:
- No circuit breaker configuration
- No timeout settings
- No retry policy
- No fallback strategy

**Why It's Wrong**:
- Cascading failures when downstream service fails
- Resource exhaustion from hanging requests
- No graceful degradation

**Fix**:
✅ Every REST API dependency must include resilience:

```json
{
  "resilience": {
    "circuit_breaker": {
      "failure_rate_threshold": 50,
      "wait_duration_in_open_state_seconds": 60
    },
    "timeout": {
      "total_timeout_milliseconds": 5000
    },
    "retry": {
      "max_attempts": 3,
      "backoff_strategy": "exponential"
    },
    "fallback": {
      "strategy": "cache",
      "implementation": "Return cached data if available"
    }
  }
}
```

See `patterns/dependency-patterns.md` for complete configuration.

---

## ❌ Anti-Pattern 6: Ignoring Breaking Change Implications

**Mistake**: Modifying/deprecating endpoints without migration planning.

**Symptoms**:
- `endpoints_to_modify` without migration guidance
- `endpoints_to_deprecate` without sunset timeline
- `change_type: BREAKING` but no consumer impact analysis

**Why It's Wrong**:
- API consumers break in production
- No migration path for clients
- Customer-facing failures

**Fix**:
✅ For BREAKING changes, MANDATORY fields:
- **Migration guidance**: How consumers should adapt
- **Versioning strategy**: How to preserve backward compatibility
- **Consumer impact**: Estimate affected clients
- **Timeline**: Deprecation date → Warning period → Removal date
- **Rollback plan**: How to revert if deployment fails

**Example**:
```json
{
  "endpoints_to_modify": [{
    "migration_guidance": {
      "consumer_actions": [
        "Update status parsing to handle enum instead of string"
      ],
      "compatibility_period": "120 days",
      "migration_deadline": "2026-05-01"
    },
    "version_strategy": "Header 'X-API-Version: 1' preserves old format"
  }]
}
```

See `patterns/api-delta-patterns.md` for breaking change handling.

---

## ❌ Anti-Pattern 7: No Validation Before Completion

**Mistake**: Not running validation during delta model design.

**Symptoms**:
- Submitting delta model without quality check
- Discovering issues during Phase 8 (too late)
- Low quality scores on first validation

**Why It's Wrong**:
- Rework is expensive
- Delays downstream phases
- Quality issues compound

**Fix**:
✅ Use microservice-changes-validator skill **iteratively**:

1. Design initial delta model
2. Run validation:
   ```bash
   bash validate-phase7.1.sh ${FEATURE}
   ```
3. Review quality report:
   ```bash
   cat results/${FEATURE}/phase7.1/changes-quality-report.json
   ```
4. Check `recommendations[]` for specific improvements
5. Iterate on delta model (use Edit tool)
6. Re-run validation
7. Repeat until COMPLETE status

**Don't wait until the end** - validate early and often.

---

## ❌ Anti-Pattern 8: Generic or Missing Descriptions

**Mistake**: Using placeholder or generic descriptions.

**Bad Examples**:
- "This endpoint handles requests"
- "Database table for data storage"
- "Event for notifications"

**Why It's Wrong**:
- No business context
- Implementation teams can't understand purpose
- Future maintenance is difficult

**Fix**:
✅ Write specific, business-focused descriptions:

**Good Examples**:
- "Create number portability request. Validates carriers, checks number ownership, initiates porting workflow."
- "Stores portability requests from initial creation through completion. Tracks donor/recipient carriers and desired port date."
- "Published when portability request passes all validations. Triggers carrier notifications and scheduling workflow."

Include:
- **What** the element does
- **When** it's used/triggered
- **Why** it exists (business justification)
- **Who** uses/calls it

---

## ❌ Anti-Pattern 9: Missing Database Constraints

**Mistake**: Creating tables without proper constraints.

**Symptoms**:
- No foreign keys
- No CHECK constraints
- No unique constraints
- No indexes on foreign keys

**Why It's Wrong**:
- Data integrity not enforced at database level
- Application bugs can corrupt data
- Poor query performance

**Fix**:
✅ Every table must include:
- **Primary key**: UUID recommended
- **Foreign keys**: With ON DELETE/UPDATE clauses
- **CHECK constraints**: For business rules
- **Unique constraints**: For business keys
- **Indexes**: On foreign keys and query columns
- **Version column**: For optimistic locking
- **Audit columns**: created_at, updated_at, created_by, updated_by

See `patterns/database-delta-patterns.md` for complete DDL template.

---

## ❌ Anti-Pattern 10: No Idempotency Strategy for Events

**Mistake**: Event subscriptions without duplicate handling.

**Symptoms**:
- No `idempotency_strategy` field
- No event processing log
- Assumes exactly-once delivery

**Why It's Wrong**:
- Kafka guarantees at-least-once delivery (duplicates possible)
- Network retries cause duplicate events
- Business logic executes multiple times

**Fix**:
✅ Every subscription must include idempotency:

```json
{
  "idempotency_strategy": {
    "method": "event_id deduplication",
    "implementation": "event_processing_log table tracks processed event_ids",
    "handling": "If event_id already processed, skip and acknowledge"
  },
  "event_processing_log_table": {
    "ddl": "CREATE TABLE event_processing_log (event_id VARCHAR(36) PRIMARY KEY, consumer_group VARCHAR(200), processed_at TIMESTAMP);"
  }
}
```

See `patterns/event-delta-patterns.md` for idempotency patterns.

---

## Quick Reference: Common Fixes

| Issue | Quick Fix |
|-------|-----------|
| Delta too large | Use progressive building (skeleton → batches via Edit) |
| Missing source | Add `maps_from` or `source` field to every change |
| Incomplete API | Add ALL status codes (200, 400, 401, 403, 404, 409, 500) |
| No resilience | Add circuit breaker + timeout + retry + fallback |
| Breaking change | Add migration guidance + versioning + timeline |
| Generic description | Write specific: what, when, why, who |
| No constraints | Add FK, CHECK, UNIQUE constraints to DDL |
| No idempotency | Add event_id deduplication with processing log |
| Low quality score | Check `recommendations[]` in validation report |
| Token limit error | Split into smaller Edit operations |

---

## Anti-Pattern Detection

**How to identify anti-patterns early**:

1. **Before design**:
   - Read Phase 6 baseline carefully (understand what exists)
   - Review computed delta (understand what's changing)
   - Choose appropriate patterns from skill

2. **During design**:
   - Use progressive building (catch issues early)
   - Validate incrementally (don't wait until end)
   - Reference examples in `../examples/`

3. **After design**:
   - Run validation script
   - Review quality report recommendations
   - Compare against pattern templates
   - Check for missing RNVS attribution

---

## Related References

- See `quality-targets.md` for quality criteria
- See `progressive-building-guide.md` for building strategy
- See `../patterns/` for correct patterns
- See `../examples/` for good examples

---

**Avoid these anti-patterns to ensure high-quality, maintainable, production-ready delta models.**
