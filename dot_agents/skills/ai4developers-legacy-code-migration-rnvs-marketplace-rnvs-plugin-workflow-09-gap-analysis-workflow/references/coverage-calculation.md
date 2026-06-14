# Coverage Calculation Reference

## Formula

**Standard Coverage Formula**:
```
Coverage % = (Fully Covered + 0.5 × Partially Covered) / (Total - Not Needed) × 100%
```

## Weight Rationale

| Status | Weight | Rationale |
|--------|--------|-----------|
| Fully Covered | 1.0 | 100% of functionality implemented |
| Partially Covered | 0.5 | ~50% average coverage assumed |
| Not Covered | 0.0 | No implementation exists |
| Not Needed | Excluded | Deprecated, shouldn't penalize coverage |

## Rounding Rules

1. Calculate raw percentage with full precision
2. Round to **exactly 2 decimal places**
3. Use standard rounding (0.005 rounds up to 0.01)
4. **Never truncate** - always round

## Examples

### Example 1: Simple Calculation
```
Input:
  Total: 100
  Fully: 80
  Partially: 10
  Not Covered: 10
  Not Needed: 0

Calculation:
  (80 + 0.5 × 10) / (100 - 0) × 100
  = (80 + 5) / 100 × 100
  = 85 / 100 × 100
  = 85.00%

Result: 85.00%
```

### Example 2: With Deprecated Items
```
Input:
  Total: 100
  Fully: 70
  Partially: 15
  Not Covered: 5
  Not Needed: 10

Calculation:
  (70 + 0.5 × 15) / (100 - 10) × 100
  = (70 + 7.5) / 90 × 100
  = 77.5 / 90 × 100
  = 86.1111...%

Result: 86.11%
```

### Example 3: Rounding Edge Case
```
Input:
  Total: 84
  Fully: 76
  Partially: 6
  Not Covered: 2
  Not Needed: 0

Calculation:
  (76 + 0.5 × 6) / (84 - 0) × 100
  = (76 + 3) / 84 × 100
  = 79 / 84 × 100
  = 94.047619...%

Result: 94.05% (NOT 94.0% or 94.1%)
```

## Coverage Grading

| Grade | Range | Description |
|-------|-------|-------------|
| Excellent | ≥95% | Almost complete coverage |
| Good | 85-94% | Strong coverage with minor gaps |
| Needs Improvement | 70-84% | Significant gaps to address |
| Critical | <70% | Major gaps, escalate to architecture |

## Consistency Check

The **same coverage percentage** must appear in:
1. `gap_analysis.md` - Executive Summary
2. `traceability_matrix.json` - `overall_coverage.coverage_percentage`
3. `PHASE9_SUMMARY.md` - Overall Coverage line

If values differ, recalculate using the formula above.

## Validation Script

```javascript
function validateCoverage(data) {
  const { fully_covered, partially_covered, total_rnvs_components, not_needed, coverage_percentage } = data;

  const expected = ((fully_covered + 0.5 * partially_covered) / (total_rnvs_components - not_needed)) * 100;
  const rounded = Math.round(expected * 100) / 100;

  if (Math.abs(coverage_percentage - rounded) > 0.01) {
    throw new Error(`Coverage mismatch: stated ${coverage_percentage}%, calculated ${rounded}%`);
  }

  return true;
}
```
