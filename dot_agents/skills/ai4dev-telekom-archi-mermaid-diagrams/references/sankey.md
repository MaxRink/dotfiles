# Sankey Diagrams

For data flow volume visualization (e.g., request routing, data pipelines).

## Syntax

```mermaid
sankey-beta
Source,Target,Value
API Gateway,Auth Service,1000
API Gateway,Order Service,3000
API Gateway,Catalog Service,5000
Order Service,Database,3000
Order Service,Payment,2500
Catalog Service,Cache,4000
Catalog Service,Database,1000
```

CSV format: `Source,Target,Value`. Values must be positive numbers. No quotes needed unless names contain commas.
