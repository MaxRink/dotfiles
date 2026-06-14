# Architecture Diagrams

Architecture diagrams (Mermaid v11.1.0+) visualize cloud infrastructure, deployment relationships, and system topology.

## Contents

- [Basic Syntax](#basic-syntax)
- [Groups](#groups)
- [Services](#services)
- [Default Icons](#default-icons)
- [Connections](#connections)
- [Junctions](#junctions)
- [Complete Example: Web Application Infrastructure](#complete-example-web-application-infrastructure)
- [Microservices Architecture](#microservices-architecture)
- [Multi-Region Deployment](#multi-region-deployment)
- [CI/CD Pipeline Infrastructure](#ci-cd-pipeline-infrastructure)
- [Data Pipeline](#data-pipeline)
- [Best Practices](#best-practices)

## Basic Syntax

```mermaid
architecture-beta
    group api(cloud)[API]

    service db(database)[Database] in api
    service server(server)[Server] in api

    db:L -- R:server
```

## Groups

Groups organize related services (like VPCs, regions, or logical groupings):

```mermaid
architecture-beta
    group vpc(cloud)[AWS VPC]
    group public_subnet(cloud)[Public Subnet] in vpc
    group private_subnet(cloud)[Private Subnet] in vpc

    service lb(internet)[Load Balancer] in public_subnet
    service app(server)[App Server] in private_subnet
    service db(database)[Database] in private_subnet

    lb:R -- L:app
    app:R -- L:db
```

## Services

Services represent individual nodes:

```mermaid
architecture-beta
    service web(server)[Web Server]
    service api(server)[API Server]
    service cache(database)[Redis Cache]
    service db(database)[PostgreSQL]
    service storage(disk)[S3 Storage]
    service cdn(internet)[CloudFront CDN]
```

## Default Icons

Built-in icons:

- `cloud` - Cloud/group boundary
- `database` - Database systems
- `disk` - Storage
- `internet` - External/internet-facing
- `server` - Application servers

## Connections

### Basic Connection

```mermaid
architecture-beta
    service a(server)[Service A]
    service b(server)[Service B]

    a:R -- L:b
```

### Directional Arrows

```mermaid
architecture-beta
    service client(internet)[Client]
    service server(server)[Server]
    service db(database)[Database]

    client:R --> L:server
    server:R --> L:db
```

### Connection Points

Use compass directions: `T` (Top), `B` (Bottom), `L` (Left), `R` (Right)

```mermaid
architecture-beta
    service a(server)[A]
    service b(server)[B]
    service c(server)[C]

    a:B -- T:b
    b:R -- L:c
```

## Junctions

Junctions enable branching patterns (load balancing, fan-out):

```mermaid
architecture-beta
    service lb(internet)[Load Balancer]
    junction junc
    service app1(server)[App 1]
    service app2(server)[App 2]
    service app3(server)[App 3]

    lb:R -- L:junc
    junc:R -- L:app1
    junc:R -- L:app2
    junc:R -- L:app3
```

## Complete Example: Web Application Infrastructure

```mermaid
architecture-beta
    group aws(cloud)[AWS Cloud]

    group vpc(cloud)[VPC] in aws
    group public(cloud)[Public Subnet] in vpc
    group private(cloud)[Private Subnet] in vpc

    service users(internet)[Users]
    service cdn(internet)[CloudFront] in aws
    service alb(internet)[ALB] in public

    service web1(server)[Web 1] in private
    service web2(server)[Web 2] in private

    service rds(database)[RDS Primary] in private
    service replica(database)[RDS Replica] in private
    service redis(database)[ElastiCache] in private
    service s3(disk)[S3 Bucket] in aws

    users:R --> L:cdn
    cdn:R --> L:alb
    alb:R --> L:web1
    alb:R --> L:web2
    web1:R --> L:rds
    web2:R --> L:rds
    rds:R --> L:replica
    web1:B --> T:redis
    web2:B --> T:redis
    web1:T --> B:s3
```

## Microservices Architecture

```mermaid
architecture-beta
    group cluster(cloud)[Kubernetes Cluster]

    group ingress(cloud)[Ingress] in cluster
    group services(cloud)[Services] in cluster
    group data(cloud)[Data Layer] in cluster

    service gateway(internet)[API Gateway] in ingress

    service auth(server)[Auth Service] in services
    service users(server)[User Service] in services
    service orders(server)[Order Service] in services
    service products(server)[Product Service] in services

    service postgres(database)[PostgreSQL] in data
    service mongo(database)[MongoDB] in data
    service redis(database)[Redis] in data
    service kafka(server)[Kafka] in data

    gateway:B --> T:auth
    gateway:B --> T:users
    gateway:B --> T:orders
    gateway:B --> T:products

    auth:B --> T:redis
    users:B --> T:postgres
    orders:B --> T:postgres
    orders:R --> L:kafka
    products:B --> T:mongo
```

## Multi-Region Deployment

```mermaid
architecture-beta
    group global(cloud)[Global Infrastructure]

    group us_east(cloud)[US East] in global
    group eu_west(cloud)[EU West] in global

    service route53(internet)[Route 53] in global

    service alb_us(internet)[ALB] in us_east
    service app_us(server)[App Servers] in us_east
    service rds_us(database)[RDS Primary] in us_east

    service alb_eu(internet)[ALB] in eu_west
    service app_eu(server)[App Servers] in eu_west
    service rds_eu(database)[RDS Replica] in eu_west

    route53:B --> T:alb_us
    route53:B --> T:alb_eu
    alb_us:R --> L:app_us
    alb_eu:R --> L:app_eu
    app_us:R --> L:rds_us
    app_eu:R --> L:rds_eu
    rds_us:B -- T:rds_eu
```

## CI CD Pipeline Infrastructure

```mermaid
architecture-beta
    group cicd(cloud)[CICD Pipeline]

    group source(cloud)[Source] in cicd
    group build(cloud)[Build] in cicd
    group deploy(cloud)[Deploy] in cicd

    service github(internet)[GitHub] in source
    service jenkins(server)[Jenkins] in build
    service docker(server)[Docker Registry] in build
    service k8s(server)[Kubernetes] in deploy
    service monitoring(server)[Prometheus] in deploy

    github:R --> L:jenkins
    jenkins:R --> L:docker
    docker:R --> L:k8s
    k8s:B -- T:monitoring
```

## Data Pipeline

```mermaid
architecture-beta
    group pipeline(cloud)[Data Pipeline]

    group ingest(cloud)[Ingestion] in pipeline
    group process(cloud)[Processing] in pipeline
    group storage(cloud)[Storage] in pipeline
    group serve(cloud)[Serving] in pipeline

    service api(internet)[API Events] in ingest
    service kafka(server)[Kafka] in ingest

    service spark(server)[Spark] in process
    service airflow(server)[Airflow] in process

    service s3(disk)[S3 Data Lake] in storage
    service redshift(database)[Redshift] in storage

    service tableau(server)[Tableau] in serve
    service api_out(internet)[Data API] in serve

    api:R --> L:kafka
    kafka:R --> L:spark
    spark:B --> T:airflow
    spark:R --> L:s3
    s3:R --> L:redshift
    redshift:R --> L:tableau
    redshift:R --> L:api_out
```

## Bidirectional Connections

```mermaid
architecture-beta
    service a(server)[Service A]
    service b(server)[Service B]

    a:R <--> L:b
```

## External Icons

Icons from iconify.design (200k+ icons) can be registered and used:

```mermaid
architecture-beta
    service aws(cloud)[AWS]
    service k8s(server)[Kubernetes]
```

Built-in icons: `cloud`, `database`, `disk`, `internet`, `server`

## Best Practices

1. **NEVER use `\n`** — Use `<br>` in labels if multi-line text is needed
2. **Group by logical boundary** — VPCs, subnets, services
3. **Use consistent icons** — Same icon types for same service categories
4. **Show data flow direction** — Use arrows to indicate request/response flow
5. **Include external services** — Show internet-facing components
6. **Label clearly** — Meaningful names for all services
7. **Use junctions for fan-out** — Load balancers, message distribution
8. **Layer your groups** — Nest groups to show hierarchy
9. **Keep it focused** — One architectural view per diagram
10. **Split complex diagrams** — Multiple focused diagrams over one cluttered diagram
