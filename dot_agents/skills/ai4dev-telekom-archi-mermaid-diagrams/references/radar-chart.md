# Radar Charts

For multi-axis comparison (experimental).

## Syntax

```mermaid
radar-beta
  title Technology Comparison
  axis reliability["Reliability"], perf["Performance"], security["Security"], cost["Cost"], dx["Developer Experience"]
  curve TeamA{85, 90, 75, 60, 80}
  curve TeamB{70, 65, 90, 85, 75}
```

**Config options:** `showLegend` (true/false), `max`/`min` (scale bounds), `ticks` (ring count), `graticule` (`circle` or `polygon`)
**Values:** Positional `{10, 20, 30}` or key-value `{axisId: 10, axisId2: 20}`
