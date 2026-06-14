# XY Charts

For line and bar charts with numerical data.

## Syntax

```
xychart
  title "Sales Data"
  x-axis "Months" [Jan, Feb, Mar, Apr, May]
  y-axis "Revenue" 0 --> 100
  line [25, 45, 60, 80, 72]
  bar [30, 40, 55, 75, 65]
```

**Rules:** Multi-word titles need quotes. x-axis supports categorical `[a, b, c]` or numeric `min --> max`. Can combine `line` and `bar`. Use `xychart horizontal` for horizontal orientation.
