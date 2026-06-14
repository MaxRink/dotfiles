# Progressive File Building Strategy

**Purpose**: Step-by-step guide for building microservice-changes-design.json without hitting token limits.

**Context**: Delta models with complete specifications can reach 10K-20K tokens, exceeding Claude's output limits. Progressive building solves this.

---

## Why Progressive Building?

### The Problem

**Single Write Approach** (DON'T DO THIS):
```
Write entire microservice-changes-design.json (15K tokens)
→ Token limit exceeded
→ Operation fails
→ No output, must start over
```

**Consequences**:
- Token limit failures (output > 10K-20K tokens)
- No progress visibility
- All-or-nothing (cannot recover from failures)
- Cannot validate incrementally

### The Solution

**Progressive Building Approach** (DO THIS):
```
1. Write skeleton (500 tokens) ✓
2. Edit to add api_changes (2K tokens) ✓
3. Edit to add database_changes (2K tokens) ✓
4. Edit to add event_changes (1K tokens) ✓
5. Edit to add state_machine_changes (1K tokens) ✓
6. Edit to add dependency_changes (1K tokens) ✓

Total: 7.5K tokens across 6 operations
Each operation < 10K tokens ✓
```

**Benefits**:
- Each operation stays under token limits
- Progress is visible (can see file grow)
- Recoverable (if one Edit fails, previous work preserved)
- Incremental validation possible
- Clear separation of concerns

---

## 6-Step Progressive Building Process

### Step 1: Write Skeleton (Metadata + Empty Arrays)

**Purpose**: Create file structure with metadata and empty change arrays.

**Use**: Write tool

**Content**:
```json
{
  "feature_name": "${FEATURE}",
  "phase": 7.1,
  "timestamp": "[ISO 8601 timestamp]",
  "baseline": {
    "source": "results/${FEATURE}/phase6/analysis.json",
    "service_name": "[from computed-delta.json]",
    "service_version": "[from computed-delta.json]"
  },
  "requirements": {
    "source": "results/${FEATURE}/phase5/control-flow-mapping.json",
    "feature_name": "${FEATURE}"
  },
  "change_type": "[from classification.json]",
  "complexity_score": "[from classification.json]",
  "is_breaking_change": "[from classification.json]",
  "changes": {
    "api_changes": {
      "endpoints_to_add": [],
      "endpoints_to_modify": [],
      "endpoints_to_deprecate": []
    },
    "database_changes": {
      "tables_to_add": [],
      "columns_to_add": [],
      "indexes_to_add": []
    },
    "event_changes": {
      "topics_to_add": [],
      "subscriptions_to_add": []
    },
    "state_machine_changes": {
      "new_states": [],
      "new_transitions": []
    },
    "dependency_changes": {
      "new_internal_dependencies": []
    }
  },
  "validation_report": {
    "overall_status": "PENDING",
    "overall_quality_score": 0,
    "validation_method": "MOCK"
  }
}
```

**Size**: ~500 tokens

**Template**: See `../examples/skeleton-template.json`

---

### Step 2: Populate API Changes

**Purpose**: Add endpoints to add/modify/deprecate.

**Use**: Edit tool

**Read First**:
- `computed-delta.json` (extract api_changes category)
- Phase 5 requirements (for business context)
- Phase 6 baseline (for existing endpoints)

**Strategy**:
Batch endpoints by type to stay under token limits:
1. **First Edit**: Add endpoints_to_add (2-3 endpoints max)
2. **Second Edit**: Add more endpoints_to_add if needed
3. **Third Edit**: Add endpoints_to_modify
4. **Fourth Edit**: Add endpoints_to_deprecate

**Pattern**: See `patterns/api-delta-patterns.md`

**Example Edit Operation**:
```json
{
  "old_string": "\"endpoints_to_add\": []",
  "new_string": "\"endpoints_to_add\": [\n    {\n      \"path\": \"/portability/requests\",\n      \"method\": \"POST\",\n      \"description\": \"...\",\n      \"request\": {...},\n      \"responses\": {...},\n      \"business_rules_enforced\": [...],\n      \"maps_from\": {...}\n    }\n  ]"
}
```

**Size**: ~2K tokens per Edit operation

**Validation**: Ensure every endpoint has:
- Full OpenAPI 3.0 specification
- All status codes (200, 400, 401, 403, 404, 409, 500)
- Business rules mapping
- RNVS source attribution

---

### Step 3: Populate Database Changes

**Purpose**: Add tables/columns/indexes.

**Use**: Edit tool

**Read First**:
- `computed-delta.json` (extract database_changes category)
- Phase 6 baseline (existing database schema)

**Strategy**:
Batch by change type:
1. **First Edit**: Add tables_to_add (1-2 tables with complete DDL)
2. **Second Edit**: Add more tables_to_add if needed
3. **Third Edit**: Add columns_to_add
4. **Fourth Edit**: Add indexes_to_add

**Pattern**: See `patterns/database-delta-patterns.md`

**Example Edit Operation**:
```json
{
  "old_string": "\"tables_to_add\": []",
  "new_string": "\"tables_to_add\": [\n    {\n      \"table_name\": \"portability_requests\",\n      \"purpose\": \"...\",\n      \"ddl\": \"CREATE TABLE ...\",\n      \"indexes\": [...],\n      \"source\": {...}\n    }\n  ]"
}
```

**Size**: ~2K tokens per Edit operation

**Validation**: Ensure every table has:
- Complete PostgreSQL DDL (executable)
- Foreign keys with ON DELETE/UPDATE
- CHECK constraints for business rules
- Optimistic locking (version column)
- Audit columns (created_at, updated_at, etc.)
- RNVS source table mapping

---

### Step 4: Populate Event Changes

**Purpose**: Add Kafka topics and subscriptions.

**Use**: Edit tool

**Read First**:
- `computed-delta.json` (extract event_changes category)
- Phase 6 baseline (existing event flows)

**Strategy**:
1. **First Edit**: Add topics_to_add (1-2 topics with Avro schemas)
2. **Second Edit**: Add subscriptions_to_add

**Pattern**: See `patterns/event-delta-patterns.md`

**Example Edit Operation**:
```json
{
  "old_string": "\"topics_to_add\": []",
  "new_string": "\"topics_to_add\": [\n    {\n      \"topic_name\": \"prt.portability-request.created\",\n      \"description\": \"...\",\n      \"avro_schema\": {...},\n      \"partitioning_key\": \"msisdn\",\n      \"source\": {...}\n    }\n  ]"
}
```

**Size**: ~1K-2K tokens per Edit operation

**Validation**: Ensure every topic has:
- Complete Avro schema with event_id, event_timestamp, correlation_id
- Partitioning strategy
- Retention policy (30 days standard)
- RNVS source attribution

**Validation**: Ensure every subscription has:
- Idempotency strategy (event_id deduplication)
- Error handling (DLQ, retry policy)
- Consumer group naming

---

### Step 5: Populate State Machine Changes

**Purpose**: Add new states and transitions.

**Use**: Edit tool

**Read First**:
- `computed-delta.json` (extract state_machine_changes category)
- Phase 6 baseline (existing state machine)

**Strategy**:
1. **First Edit**: Add new_states
2. **Second Edit**: Add new_transitions

**Pattern**: See `patterns/state-machine-patterns.md`

**Example Edit Operation**:
```json
{
  "old_string": "\"new_states\": []",
  "new_string": "\"new_states\": [\n    {\n      \"state_name\": \"PENDING_VALIDATION\",\n      \"description\": \"...\",\n      \"state_type\": \"initial\",\n      \"allowed_next_states\": [...]\n    }\n  ]"
}
```

**Size**: ~1K tokens per Edit operation

**Validation**: Ensure every state has:
- Clear state name (UPPER_SNAKE_CASE)
- Business description
- State type (initial, intermediate, terminal)
- Allowed transitions

---

### Step 6: Populate Dependency Changes

**Purpose**: Add new service dependencies with resilience.

**Use**: Edit tool

**Read First**:
- `computed-delta.json` (extract dependency_changes category)
- Phase 6 baseline (existing dependencies)

**Strategy**:
1. **Single Edit**: Add all new_internal_dependencies (usually 1-3 dependencies)

**Pattern**: See `patterns/dependency-patterns.md`

**Example Edit Operation**:
```json
{
  "old_string": "\"new_internal_dependencies\": []",
  "new_string": "\"new_internal_dependencies\": [\n    {\n      \"target_service\": \"carrier-registry-service\",\n      \"communication_pattern\": \"REST_API\",\n      \"purpose\": \"...\",\n      \"resilience\": {\n        \"circuit_breaker\": {...},\n        \"timeout\": {...},\n        \"retry\": {...},\n        \"fallback\": {...}\n      }\n    }\n  ]"
}
```

**Size**: ~1K tokens per Edit operation

**Validation**: Ensure every REST dependency has:
- Circuit breaker configuration
- Timeout settings
- Retry policy
- Fallback strategy

---

## Operation Summary

| Step | Tool | Target | Size | Pattern Reference |
|------|------|--------|------|-------------------|
| 1. Skeleton | Write | Full file | 500 tokens | examples/skeleton-template.json |
| 2. API | Edit | changes.api_changes | 2K tokens | patterns/api-delta-patterns.md |
| 3. Database | Edit | changes.database_changes | 2K tokens | patterns/database-delta-patterns.md |
| 4. Events | Edit | changes.event_changes | 1K tokens | patterns/event-delta-patterns.md |
| 5. State Machine | Edit | changes.state_machine_changes | 1K tokens | patterns/state-machine-patterns.md |
| 6. Dependencies | Edit | changes.dependency_changes | 1K tokens | patterns/dependency-patterns.md |

**Total**: ~8K tokens across 6 operations, each under 10K limit

---

## Best Practices

### Before Starting

✅ **DO**:
- Read `computed-delta.json` completely (understand what's changing)
- Read `classification.json` (understand change type and complexity)
- Review Phase 6 baseline (understand current state)
- Choose appropriate patterns from skill

❌ **DON'T**:
- Start writing without reading inputs
- Skip reading existing Phase 6 baseline
- Ignore computed delta categories

### During Progressive Building

✅ **DO**:
- Follow the 6-step sequence (skeleton → API → DB → events → states → deps)
- Batch changes within each category (don't add all endpoints in one Edit)
- Validate JSON syntax after each Edit
- Check file incrementally (use Read tool to verify edits)

❌ **DON'T**:
- Jump around between categories randomly
- Add too many items in single Edit (> 3 endpoints)
- Skip validation until the end
- Assume Edit worked (verify with Read)

### After Completion

✅ **DO**:
- Run validation: `bash validate-phase7.1.sh ${FEATURE}`
- Review quality report recommendations
- Iterate on low-scoring gates
- Re-validate until COMPLETE status

❌ **DON'T**:
- Submit without validation
- Ignore quality score
- Accept INCOMPLETE status without iteration

---

## Troubleshooting

### Issue: Edit operation failed (old_string not found)

**Cause**: File structure changed since last Read
**Fix**: Read file again, copy exact string including whitespace

### Issue: JSON syntax error after Edit

**Cause**: Malformed JSON (missing comma, bracket, quote)
**Fix**: Read file, identify syntax error, fix with another Edit

### Issue: Still hitting token limits in Edit

**Cause**: Too many items in single Edit
**Fix**: Batch smaller (1-2 endpoints instead of 3-4)

### Issue: Validation fails after progressive building

**Cause**: Incomplete specifications or missing fields
**Fix**: Review quality report recommendations, add missing details

---

## Example Timeline

**Feature**: priority-porting (ADDITIVE change, low complexity)

1. **Step 1** (Write skeleton): 30 seconds
2. **Step 2** (API changes): Skip (no new endpoints)
3. **Step 3** (Database changes): 2 minutes (add priority column + index)
4. **Step 4** (Event changes): Skip (no new events)
5. **Step 5** (State changes): Skip (no new states)
6. **Step 6** (Dependencies): Skip (no new dependencies)
7. **Validation**: 10 seconds (run script)
8. **Review & Iterate**: 1 minute (add missing descriptions)
9. **Re-validate**: 10 seconds (COMPLETE)

**Total**: ~4 minutes

**Feature**: async-notifications (ENHANCEMENT change, moderate complexity)

1. **Step 1**: 30 seconds
2. **Step 2**: Skip
3. **Step 3**: 1 minute (add event processing log table)
4. **Step 4**: 5 minutes (add 2 topics with Avro schemas + 2 subscriptions)
5. **Step 5**: Skip
6. **Step 6**: 2 minutes (add notification service dependency with resilience)
7. **Validation**: 10 seconds
8. **Review & Iterate**: 3 minutes (enhance idempotency docs)
9. **Re-validate**: 10 seconds (COMPLETE)

**Total**: ~12 minutes

---

## Related References

- See `quality-targets.md` for quality criteria
- See `anti-patterns.md` for what NOT to do
- See `../patterns/` for detailed design patterns
- See `../examples/` for complete delta model examples

---

**Use this progressive building strategy to efficiently create high-quality delta models without hitting token limits.**
