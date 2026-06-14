# Mindmaps

For architecture decision exploration and capability mapping.

## Syntax

```mermaid
mindmap
  root((Architecture))
    Frontend
      React SPA
      Mobile App
    Backend
      API Gateway
      Microservices
        Order Service
        Catalog Service
    Data
      PostgreSQL
      Redis Cache
      Kafka
    Infrastructure
      AWS
        EKS
        RDS
        S3
```

**Node shapes:** `((Circle))`, `(Rounded)`, `[Square]`, `{{Hexagon}}`, `)Cloud(`, default (no brackets).
Indentation defines hierarchy.
