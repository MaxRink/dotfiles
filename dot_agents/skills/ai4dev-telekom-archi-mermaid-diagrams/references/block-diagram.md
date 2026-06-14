# Block Diagrams

For high-level system block views.

## Syntax

```mermaid
block-beta
  columns 3

  A["Frontend"] B["API Gateway"] C["Backend"]
  D["Database"]:3

  A --> B --> C
  C --> D
```
