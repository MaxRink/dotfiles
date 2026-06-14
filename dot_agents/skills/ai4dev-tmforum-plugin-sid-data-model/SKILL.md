---
name: ai4dev-tmforum-plugin-sid-data-model
description: TM Forum Shared Information/Data Model (SID) for telecommunications data entities. Use this skill when designing data models, mapping entities to SID domains, ensuring data consistency across systems, or aligning database schemas with TM Forum standards.
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/tmforum-plugin/skills/sid-data-model by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# SID Data Model

## Overview

This skill provides guidance on TM Forum SID (Shared Information/Data Model) - a common data model for telecommunications that ensures semantic consistency and interoperability across systems.

## When to Use This Skill

Use when designing data models, creating database schemas, mapping business entities to standard models, or ensuring data consistency across telecommunications systems.

## SID Domain Structure

### 1. Product Domain

Entities related to products and offerings.

**Core Entities**:

- **ProductOffering**: Commercialized products available for sale
- **ProductSpecification**: Product characteristics and attributes
- **Product**: Instantiated product for a customer
- **ProductOfferingPrice**: Pricing information
- **BundledProductOffering**: Product bundles

**TMF API Mapping**: TMF620, TMF622, TMF637

### 2. Customer Domain

Entities related to customers and parties.

**Core Entities**:

- **Customer**: Business abstraction of individuals/organizations
- **Party**: Individual or Organization
- **PartyRole**: Roles that parties play
- **Account**: Customer accounts
- **Agreement**: Contracts and agreements

**TMF API Mapping**: TMF629, TMF632, TMF666

### 3. Service Domain

Entities related to services.

**Core Entities**:

- **ServiceSpecification**: Service characteristics
- **Service**: Instantiated service
- **ServiceCandidate**: Marketable services
- **CustomerFacingService**: Services visible to customers
- **ResourceFacingService**: Internal services

**TMF API Mapping**: TMF633, TMF638, TMF640, TMF641

### 4. Resource Domain

Entities related to resources.

**Core Entities**:

- **Resource**: Physical and logical resources
- **ResourceSpecification**: Resource characteristics
- **PhysicalResource**: Tangible resources
- **LogicalResource**: Intangible resources
- **CompoundResource**: Composite resources

**TMF API Mapping**: TMF634, TMF639

### 5. Common Business Entities Domain

Cross-cutting entities.

**Core Entities**:

- **Note**: Comments and annotations
- **Attachment**: Documents and files
- **RelatedParty**: Party relationships
- **ContactMedium**: Communication channels
- **TimePeriod**: Time ranges
- **Money**: Monetary values

## Entity Relationships

### Product-Customer Relationship

```text
Customer (1) ─── places ─── (0..*) ProductOrder
ProductOrder (1) ─── orderItem ─── (1..*) ProductOrderItem
ProductOrderItem (1) ─── references ─── (1) ProductOffering
ProductOrder (1) ─── results in ─── (0..*) Product
```

### Service-Resource Relationship

```text
Service (1) ─── supportedBy ─── (0..*) Resource
CustomerFacingService (1) ─── supportedBy ─── (0..*) ResourceFacingService
ResourceFacingService (1) ─── uses ─── (0..*) Resource
```

## Data Modeling Principles

1. **SID Alignment**: Map entities to SID model
2. **Attribute Consistency**: Use SID attribute names and types
3. **Relationship Integrity**: Model associations correctly
4. **Extensibility**: Support custom attributes via `characteristic` arrays
5. **Versioning**: Track entity versions for audit
6. **Lifecycle States**: Model entity state machines
7. **Temporal Data**: Support time-based queries

## Entity Lifecycle States

**ProductOffering**: InStudy, InDesign, InTest, Active, Launched, Retired, Obsolete

**Product**: created, pendingActive, cancelled, active, pendingTerminate, terminated, suspended

**Service**: feasibilityChecked, designed, reserved, inactive, active, terminated

**Resource**: planning, installing, active, standby, terminated, suspended

## Database Schema Patterns

### Pattern 1: Entity Table

```sql
CREATE TABLE product_offering (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    lifecycle_status VARCHAR(50),
    valid_for_start_date TIMESTAMP,
    valid_for_end_date TIMESTAMP,
    product_spec_id VARCHAR(255),
    FOREIGN KEY (product_spec_id) REFERENCES product_specification(id)
);
```

### Pattern 2: Relationship Table (1:N)

```sql
CREATE TABLE product_offering_price (
    id VARCHAR(255) PRIMARY KEY,
    product_offering_id VARCHAR(255) NOT NULL,
    price_type VARCHAR(50),
    price_amount DECIMAL(15,2),
    FOREIGN KEY (product_offering_id) REFERENCES product_offering(id)
);
```

### Pattern 3: Extensibility (Characteristics)

```sql
CREATE TABLE product_characteristic (
    id VARCHAR(255) PRIMARY KEY,
    product_id VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    value TEXT,
    FOREIGN KEY (product_id) REFERENCES product(id)
);
```

## API Payload Alignment

Ensure data models match TMF API JSON structures:

```json
{
  "id": "PROD-123",
  "href": "/product/PROD-123",
  "name": "5G Mobile Plan",
  "status": "active",
  "productOffering": {
    "id": "OFFER-5G",
    "href": "/productOffering/OFFER-5G"
  },
  "relatedParty": [
    {
      "id": "CUST-789",
      "role": "customer",
      "@referredType": "Customer"
    }
  ]
}
```
