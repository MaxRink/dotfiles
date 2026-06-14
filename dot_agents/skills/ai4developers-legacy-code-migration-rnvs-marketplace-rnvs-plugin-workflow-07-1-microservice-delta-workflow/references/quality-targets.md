# Quality Targets by Change Type

**Purpose**: Define quality score thresholds and criteria for different types of microservice changes.

**Context**: Phase 7.1 uses different quality targets based on change complexity and breaking change risk.

---

## Quality Target Matrix

| Change Type | Complexity | Breaking | Quality Target | Status Interpretation |
|-------------|------------|----------|----------------|----------------------|
| **ADDITIVE** | < 10 | No | ≥80/100 | Safe additions, high quality bar |
| **ENHANCEMENT** | 10-29 | No | ≥75/100 | Moderate additions, standard quality |
| **BREAKING** | Any | Yes | ≥70/100 | API changes require migration planning |
| **REFACTORING** | ≥30 | No | ≥70/100 | High complexity, extensive testing needed |

---

## ADDITIVE Changes

**Characteristics**:
- Only new endpoints, tables, events, dependencies
- No modifications or deprecations
- Backward compatible
- Low risk

**Quality Target**: **≥80/100**

**Rationale**: Simple additions should meet high quality standards since there's no migration complexity.

**Focus Areas**:
- **Completeness** (critical): All new elements fully specified
- **Clarity** (critical): Clear documentation and purpose
- **Examples** (important): Comprehensive API examples
- **Testing** (important): Thorough test coverage

**Example**: Adding a new GET endpoint that doesn't modify existing behavior

**Success Criteria**:
- ✅ Full OpenAPI 3.0 specification with all status codes
- ✅ Complete database DDL with constraints
- ✅ RNVS source attribution for all changes
- ✅ Business rules mapped to Phase 3 identifiers
- ✅ No gaps in documentation

---

## ENHANCEMENT Changes

**Characteristics**:
- Multiple additions across categories
- Moderate complexity (10-29 points)
- No breaking changes
- Medium risk

**Quality Target**: **≥75/100**

**Rationale**: More complex than additive but still backward-compatible. Slightly relaxed quality bar.

**Focus Areas**:
- **Integration** (critical): How new changes integrate with existing service
- **Performance** (important): Performance impact analysis
- **Synergies** (important): Highlight value-add of enhancements
- **Rollout** (important): Incremental deployment strategy

**Example**: Adding new event subscriptions + database columns + API endpoints together

**Success Criteria**:
- ✅ Integration points clearly documented
- ✅ Performance considerations addressed
- ✅ Incremental rollout plan provided
- ✅ Monitoring and alerting defined

---

## BREAKING Changes

**Characteristics**:
- Contains `endpoints_to_modify` or `endpoints_to_deprecate`
- Requires consumer migration
- High risk
- Any complexity level

**Quality Target**: **≥70/100**

**Rationale**: Breaking changes require extensive migration planning which takes priority over perfect documentation.

**Focus Areas** (MANDATORY):
- **Migration Path** (CRITICAL): How consumers adapt to changes
- **Versioning Strategy** (CRITICAL): How to preserve backward compatibility during migration
- **Consumer Impact** (CRITICAL): Which clients are affected
- **Rollback Plan** (CRITICAL): How to revert if deployment fails
- **Timeline** (important): Deprecation → Warning → Removal dates

**Example**: Modifying request schema of existing endpoint (breaks existing clients)

**Success Criteria**:
- ✅ **MANDATORY**: Migration guide for each breaking change
- ✅ **MANDATORY**: Versioning strategy (e.g., /v2/ endpoints, API version header)
- ✅ **MANDATORY**: Consumer impact analysis (estimate affected clients)
- ✅ **MANDATORY**: Rollback procedure documented
- ✅ Sunset timeline for deprecated features
- ✅ Replacement endpoint recommendations

---

## REFACTORING Changes

**Characteristics**:
- Large number of changes (complexity ≥30)
- High complexity score
- No breaking external contracts
- Internal improvements only

**Quality Target**: **≥70/100**

**Rationale**: High complexity means extensive testing takes priority. Lower quality bar acceptable if tests are comprehensive.

**Focus Areas**:
- **Testing** (CRITICAL): Extensive test coverage due to complexity
- **Internal Documentation** (important): Document refactoring rationale
- **External Contracts** (important): Prove external APIs unchanged
- **Performance** (important): Benchmark before/after

**Example**: Major database schema normalization without API contract changes

**Success Criteria**:
- ✅ Comprehensive test suite (unit + integration + contract tests)
- ✅ External API contracts verified unchanged
- ✅ Performance benchmarks show no regression
- ✅ Internal improvements clearly documented

---

## Quality Score Calculation

### 5-Gate Validation Framework

**Total Score**: Sum of all gate scores (max 100 points)

| Gate | Weight | Focus | Pass Criteria |
|------|--------|-------|---------------|
| **Completeness** | 30% | All delta categories populated | No empty arrays unless genuinely no changes |
| **API Quality** | 30% | OpenAPI specs, business rules, source attribution | All endpoints have complete specs |
| **Database Quality** | 20% | DDL syntax, constraints, purposes | Executable DDL, business purpose documented |
| **Integration Quality** | 10% | Event schemas, idempotency, resilience | Avro schemas valid, resilience patterns present |
| **Schema Validation** | 10% | JSON structure compliance | Valid against microservice-changes-design.schema.json |

### Status Determination

```
if (score >= quality_target):
    status = "COMPLETE"  # Ready for next phase
elif (score >= quality_target - 15):
    status = "PARTIAL"   # Minor improvements recommended
else:
    status = "INCOMPLETE"  # Significant improvements needed
```

**Example**:
- ADDITIVE target: 80
- Actual score: 82
- Status: COMPLETE ✅

- ADDITIVE target: 80
- Actual score: 68
- Status: PARTIAL ⚠️ (68 >= 80-15)

- ADDITIVE target: 80
- Actual score: 60
- Status: INCOMPLETE ❌ (60 < 80-15)

---

## Quality Improvement Strategies

### For Completeness Gate (<30)

**Symptoms**:
- Empty arrays in delta categories
- Missing descriptions
- No RNVS source attribution

**Fixes**:
- Populate all relevant delta categories (even if empty, explain why)
- Add business purpose for every change
- Include RNVS source file:line references

### For API Quality Gate (<30)

**Symptoms**:
- Missing request/response schemas
- Incomplete status code coverage
- No business rule mapping

**Fixes**:
- Add full OpenAPI 3.0 specifications
- Include ALL status codes (200, 400, 401, 403, 404, 409, 500)
- Map endpoints to Phase 3 business rules (BR-XXX)
- Add RNVS source attribution (maps_from field)

### For Database Quality Gate (<20)

**Symptoms**:
- Non-executable DDL
- Missing constraints
- No table purposes

**Fixes**:
- Provide complete CREATE TABLE / ALTER TABLE statements
- Add foreign keys, CHECK constraints
- Document business purpose for tables/columns
- Include RNVS source table mapping

### For Integration Quality Gate (<10)

**Symptoms**:
- No Avro schemas for events
- Missing idempotency strategies
- No resilience patterns for dependencies

**Fixes**:
- Add complete Avro schemas with event_id, event_timestamp, correlation_id
- Document idempotency (event_id deduplication, processing log)
- Add resilience for REST deps (circuit breaker, timeout, retry, fallback)

### For Schema Validation Gate (<10)

**Symptoms**:
- JSON structure doesn't match schema
- Missing required fields
- Invalid data types

**Fixes**:
- Validate against `microservice-changes-design.schema.json`
- Ensure all required fields present (feature_name, phase, timestamp, baseline, requirements, change_type, changes)
- Use correct data types (arrays, objects, strings, integers, booleans)

---

## Iteration Strategy

### First Iteration
- Focus on completeness (fill all delta categories)
- Add basic descriptions
- Include minimal RNVS attribution

### Second Iteration
- Enhance API specifications (full OpenAPI)
- Add database constraints and indexes
- Document business justification

### Third Iteration
- Add resilience patterns
- Complete source attribution
- Polish documentation

### Validation
- Run validation after each iteration
- Review `recommendations[]` in quality report
- Iterate until COMPLETE status

---

## Related References

- See `anti-patterns.md` for common mistakes to avoid
- See `progressive-building-guide.md` for file building strategy
- See `../patterns/` for detailed design patterns
- See `../examples/` for quality score examples

---

**Use these quality targets to ensure production-ready delta models that meet enterprise standards.**
