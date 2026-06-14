# Packet Diagrams

For network packet structure visualization.

## Syntax

```mermaid
packet
  0-15: "Source Port"
  16-31: "Destination Port"
  32-63: "Sequence Number"
  64-95: "Acknowledgment Number"
```

**Bits syntax (v11.7.0+):** `+8: "Field"` auto-increments bit position.
**Config:** `bitsperrow` (default 32), `bitwidth`, `showbits` (true/false).
