---
name: ai4dev-telekom-archi-cloud-patterns
description: >
  Design cloud infrastructure architectures for AWS, Azure, and GCP. Covers Well-Architected Framework,
  infrastructure-as-code (Terraform, Pulumi), Kubernetes deployment patterns, multi-cloud strategies,
  cost optimization, and cloud-native design patterns. Use this skill when the user asks about cloud
  architecture, infrastructure design, Kubernetes deployment, serverless patterns, auto-scaling,
  cloud networking, IaC, or cloud cost optimization. Also trigger for "deploy this on AWS/Azure/GCP",
  "design the infrastructure", "Terraform module", "Kubernetes manifest", "EKS/AKS/GKE",
  or any cloud provider-specific architecture question.
argument-hint: "[cloud provider or workload]"
allowed-tools: Read, Glob, Grep, Write
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/telekom-archi/skills/cloud-patterns by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Cloud Patterns Skill

You help users design production-ready cloud infrastructure with proper networking, security, scalability, and cost controls. Think infrastructure-as-architecture, not just infrastructure-as-code.

## Design Process

### 1. Cloud Architecture Decision Tree

```mermaid
graph TD
  Start[New Workload] --> Q1{Stateless?}
  Q1 -->|Yes| Q2{Event-driven?}
  Q1 -->|No| Containers[Containers/K8s]

  Q2 -->|Yes| Lambda[Serverless Functions]
  Q2 -->|No| Q3{Traffic pattern?}

  Q3 -->|Steady| ECS[Container Service]
  Q3 -->|Spiky| ASG[Auto-Scaling Group]
  Q3 -->|Unpredictable| Lambda

  Containers --> Q4{Multi-region?}
  Q4 -->|Yes| GlobalK8s[Multi-Cluster K8s]
  Q4 -->|No| SingleK8s[Single K8s Cluster]

  style Lambda fill:#FF9900,color:#fff
  style Containers fill:#326CE5,color:#fff
  style ECS fill:#FF9900,color:#fff
```

### 2. Reference Architectures

**Three-Tier Web Application:**
```mermaid
architecture-beta
  group cloud(cloud)[AWS Cloud]
  group vpc(cloud)[VPC - 10.0.0.0/16] in cloud

  group public(server)[Public Subnets] in vpc
  group private(server)[Private Subnets] in vpc
  group data(database)[Data Subnets] in vpc

  service cdn(internet)[CloudFront CDN]
  service alb(internet)[Application LB] in public
  service nat(internet)[NAT Gateway] in public
  service app1(server)[App Server AZ-a] in private
  service app2(server)[App Server AZ-b] in private
  service rds(database)[RDS Primary] in data
  service replica(database)[RDS Replica] in data
  service cache(database)[ElastiCache] in data
  junction jApp in private

  cdn:R -- L:alb
  alb:R -- L:jApp
  jApp:R -- L:app1
  jApp:B -- T:app2
  app1:R -- L:rds
  app2:R -- L:replica
  app1:B -- T:cache
```

**Event-Driven Microservices:**
```mermaid
C4Container
  title Cloud-Native Event-Driven Architecture

  Person(user, "User", "End user")

  Container_Boundary(frontend, "Frontend") {
    Container(cdn, "CDN", "CloudFront", "Static assets")
    Container(spa, "SPA", "React", "Single Page App")
  }

  Container_Boundary(compute, "Compute Layer") {
    Container(apigw, "API Gateway", "Kong/AWS APIGW", "Request routing")
    Container(orderSvc, "Order Service", "EKS Pod", "Order processing")
    Container(paymentSvc, "Payment Service", "EKS Pod", "Payment handling")
    Container(notifSvc, "Notification Svc", "Lambda", "Email/SMS/Push")
  }

  Container_Boundary(data, "Data Layer") {
    ContainerDb(orderDb, "Orders DB", "RDS PostgreSQL", "Order data")
    ContainerDb(paymentDb, "Payments DB", "DynamoDB", "Payment records")
    ContainerQueue(eventBus, "Event Bus", "Kafka/MSK", "Domain events")
    ContainerDb(cache, "Cache", "ElastiCache", "Session + query cache")
  }

  Rel(user, cdn, "Loads", "HTTPS")
  Rel(cdn, spa, "Serves")
  Rel(spa, apigw, "API calls", "HTTPS/JSON")
  Rel(apigw, orderSvc, "Routes", "gRPC")
  Rel(apigw, paymentSvc, "Routes", "gRPC")
  Rel(orderSvc, orderDb, "Reads/Writes", "JDBC/TLS")
  Rel(paymentSvc, paymentDb, "Reads/Writes", "HTTPS")
  Rel(orderSvc, eventBus, "Publishes events", "Kafka")
  Rel(paymentSvc, eventBus, "Publishes events", "Kafka")
  Rel(eventBus, notifSvc, "Triggers", "Event")
  Rel(orderSvc, cache, "Reads", "Redis Protocol")
```

### 3. Kubernetes Patterns

**Deployment Architecture:**
```mermaid
graph TD
  subgraph Cluster["EKS/AKS/GKE Cluster"]
    subgraph System["System Namespace"]
      Ingress[Ingress Controller]
      Mesh[Service Mesh]
      Monitor[Prometheus + Grafana]
    end
    subgraph App["App Namespace"]
      SvcA[Service A<br/>3 replicas]
      SvcB[Service B<br/>2 replicas]
      SvcC[Service C<br/>2 replicas]
    end
    subgraph Data["Data Namespace"]
      Redis[(Redis)]
      PG[(PostgreSQL)]
    end
  end

  Internet[Internet] --> Ingress
  Ingress --> SvcA
  Ingress --> SvcB
  SvcA --> SvcC
  SvcB --> SvcC
  SvcC --> PG
  SvcA --> Redis

  style System fill:#326CE5,color:#fff
  style App fill:#66bb6a,color:#fff
  style Data fill:#ef5350,color:#fff
```

**Key K8s Patterns:**
- **Sidecar** — proxy, logging, config reload alongside main container
- **Ambassador** — proxy outbound connections (e.g., connection pooling)
- **Adapter** — normalize interfaces between containers
- **Init Container** — setup tasks before main container starts
- **Operator** — custom controller for complex stateful apps

### 4. Infrastructure as Code (Terraform)

**Module Structure:**
```text
infrastructure/
  modules/
    networking/     # VPC, subnets, security groups
    compute/        # EKS, EC2, Lambda
    database/       # RDS, DynamoDB, ElastiCache
    monitoring/     # CloudWatch, Prometheus
    security/       # IAM, KMS, Secrets Manager
  environments/
    dev/
    staging/
    production/
  backend.tf        # State configuration
  variables.tf      # Input variables
  outputs.tf        # Output values
```

**Best Practices:**
- Remote state with locking (S3 + DynamoDB for AWS)
- Separate state per environment
- Use modules for reusable components
- Tag everything for cost allocation
- Use `terraform plan` in CI, `terraform apply` requires approval

### 5. Cost Optimization Patterns

| Pattern | Savings | Effort |
|---------|---------|--------|
| Right-sizing instances | 20-40% | Low |
| Reserved/Savings Plans | 30-60% | Medium |
| Spot instances for stateless | 60-90% | Medium |
| Auto-scaling policies | 20-50% | Medium |
| Storage tiering (S3 lifecycle) | 30-70% | Low |
| Serverless for spiky workloads | Variable | High |
| Multi-region optimization | 10-30% | High |

### 6. Multi-Cloud & Hybrid

```mermaid
graph TB
  subgraph AWS["AWS (Primary)"]
    EKS[EKS Cluster]
    RDS[(RDS)]
    S3[(S3)]
  end
  subgraph Azure["Azure (DR)"]
    AKS[AKS Cluster]
    AzSQL[(Azure SQL)]
    Blob[(Blob Storage)]
  end
  subgraph OnPrem["On-Premises"]
    Legacy[Legacy Systems]
    AD[Active Directory]
  end

  EKS <-->|Cross-cloud replication| AKS
  RDS -->|CDC| AzSQL
  S3 -->|Cross-cloud sync| Blob
  Legacy -->|VPN / ExpressRoute| AWS
  AD -->|Federation| AWS
  AD -->|Federation| Azure

  style AWS fill:#FF9900,color:#fff
  style Azure fill:#0078D4,color:#fff
  style OnPrem fill:#666,color:#fff
```

### 7. Networking Patterns

- **Hub-and-Spoke VPC** — Central hub for shared services, spokes for workloads
- **Transit Gateway** — Simplify multi-VPC and hybrid connectivity
- **PrivateLink** — Access services without internet exposure
- **Service Mesh** — mTLS, traffic management, observability between services

## Output Format

Produce:
1. **Infrastructure topology diagram** (architecture-beta or C4 Deployment)
2. **Network design** with CIDR planning
3. **Compute strategy** rationale
4. **Cost estimate** (rough order of magnitude)
5. **IaC module structure**

Output is saved to `docs/architecture/infrastructure.md` (path set by the invoking agent or command).
