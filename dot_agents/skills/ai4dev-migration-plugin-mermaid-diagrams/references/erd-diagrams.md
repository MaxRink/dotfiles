# Entity Relationship Diagrams (ERD)

ERDs model database schemas, showing tables (entities), their columns (attributes), and relationships between tables. Essential for database design and documentation.

## Contents

- [Basic Syntax](#basic-syntax)
- [Entity Attributes](#entity-attributes)
- [Relationships](#relationships)
- [Data Types](#data-types)
- [Complete Example: E-Commerce Database](#complete-example-e-commerce-database)
- [Blog Platform Schema](#blog-platform-schema)
- [Common Patterns](#common-patterns)
- [Best Practices](#best-practices)

## Basic Syntax

```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
```

## Entity Attributes

```mermaid
erDiagram
    CUSTOMER {
        int id PK
        string email UK
        string name
        string phone
        datetime created_at
    }
```

**Attribute format:** `type name constraints`

**Common constraints:**

- `PK` - Primary Key
- `FK` - Foreign Key
- `UK` - Unique Key
- `NN` - Not Null

## Relationships

### Cardinality Symbols

| Symbol | Meaning |
|--------|---------|
| `\|\|` | Exactly one |
| `\|o` | Zero or one |
| `}|` | One or many |
| `}o` | Zero or many |

### Relationship Lines

- `--` Standard relationship
- `..` Identifying relationship

### Common Patterns

```mermaid
erDiagram
    %% One-to-One
    USER ||--|| PROFILE : has

    %% One-to-Many
    CUSTOMER ||--o{ ORDER : places

    %% Many-to-Many (via junction)
    STUDENT ||--o{ ENROLLMENT : has
    COURSE ||--o{ ENROLLMENT : includes

    %% Optional
    EMPLOYEE |o--o{ DEPARTMENT : manages
```

## Data Types

Common database types to use:

- `int`, `bigint`, `smallint`
- `varchar`, `text`, `char`
- `decimal`, `float`, `double`
- `boolean`, `bool`
- `date`, `datetime`, `timestamp`
- `json`, `jsonb`
- `uuid`
- `blob`, `bytea`

## Complete Example: E-Commerce Database

```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
    CUSTOMER ||--o{ REVIEW : writes
    CUSTOMER ||--o{ ADDRESS : has
    ORDER ||--|{ LINE_ITEM : contains
    PRODUCT ||--o{ LINE_ITEM : "ordered in"
    PRODUCT }o--|| CATEGORY : "belongs to"
    PRODUCT ||--o{ REVIEW : receives
    PRODUCT ||--o{ INVENTORY : tracks
    ORDER ||--|| PAYMENT : "paid by"
    ORDER ||--o| SHIPMENT : "shipped via"

    CUSTOMER {
        uuid id PK
        varchar email UK
        varchar name
        varchar phone
        timestamp created_at
        timestamp updated_at
    }

    ADDRESS {
        uuid id PK
        uuid customer_id FK
        varchar street
        varchar city
        varchar state
        varchar postal_code
        varchar country
        boolean is_default
    }

    ORDER {
        uuid id PK
        uuid customer_id FK
        decimal total
        varchar status
        timestamp order_date
        timestamp shipped_date
        timestamp delivered_date
    }

    LINE_ITEM {
        uuid id PK
        uuid order_id FK
        uuid product_id FK
        int quantity
        decimal price_per_unit
        decimal subtotal
    }

    PRODUCT {
        uuid id PK
        varchar sku UK
        varchar name
        text description
        decimal price
        uuid category_id FK
        boolean is_active
        timestamp created_at
    }

    CATEGORY {
        uuid id PK
        varchar name UK
        text description
        uuid parent_category_id FK
    }

    INVENTORY {
        uuid id PK
        uuid product_id FK
        int quantity
        varchar warehouse_location
        timestamp last_updated
    }

    REVIEW {
        uuid id PK
        uuid customer_id FK
        uuid product_id FK
        int rating
        text comment
        timestamp created_at
    }

    PAYMENT {
        uuid id PK
        uuid order_id FK
        varchar payment_method
        decimal amount
        varchar status
        varchar transaction_id UK
        timestamp processed_at
    }

    SHIPMENT {
        uuid id PK
        uuid order_id FK
        varchar carrier
        varchar tracking_number
        timestamp shipped_date
        timestamp estimated_delivery
        timestamp actual_delivery
    }
```

## Blog Platform Schema

```mermaid
erDiagram
    USER ||--o{ POST : creates
    USER ||--o{ COMMENT : writes
    POST ||--o{ COMMENT : receives
    POST ||--o{ POST_TAG : has
    TAG ||--o{ POST_TAG : applied_to
    POST }o--|| CATEGORY : "belongs to"
    USER ||--o{ LIKE : gives
    POST ||--o{ LIKE : receives

    USER {
        bigint id PK
        varchar email UK
        varchar username UK
        varchar password_hash
        varchar display_name
        text bio
        varchar avatar_url
        timestamp created_at
        timestamp last_login
    }

    POST {
        bigint id PK
        bigint user_id FK
        bigint category_id FK
        varchar title
        varchar slug UK
        text content
        text excerpt
        varchar featured_image_url
        varchar status
        int view_count
        timestamp published_at
        timestamp created_at
        timestamp updated_at
    }

    COMMENT {
        bigint id PK
        bigint user_id FK
        bigint post_id FK
        bigint parent_comment_id FK
        text content
        varchar status
        timestamp created_at
    }

    CATEGORY {
        bigint id PK
        varchar name UK
        varchar slug UK
        text description
        bigint parent_id FK
    }

    TAG {
        bigint id PK
        varchar name UK
        varchar slug UK
    }

    POST_TAG {
        bigint post_id FK
        bigint tag_id FK
    }

    LIKE {
        bigint id PK
        bigint user_id FK
        varchar likeable_type
        bigint likeable_id
        timestamp created_at
    }
```

## Common Patterns

### Self-Referencing (Hierarchical)

```mermaid
erDiagram
    CATEGORY ||--o{ CATEGORY : "parent of"

    CATEGORY {
        uuid id PK
        varchar name
        uuid parent_id FK
    }
```

### Junction Table (Many-to-Many)

```mermaid
erDiagram
    STUDENT }o--o{ COURSE : enrolls
    STUDENT ||--o{ ENROLLMENT : has
    COURSE ||--o{ ENROLLMENT : includes

    STUDENT {
        uuid id PK
        varchar name
    }

    ENROLLMENT {
        uuid student_id FK
        uuid course_id FK
        date enrolled_date
        varchar grade
    }

    COURSE {
        uuid id PK
        varchar title
    }
```

### Polymorphic Relationship

```mermaid
erDiagram
    COMMENT {
        uuid id PK
        uuid user_id FK
        varchar commentable_type
        uuid commentable_id
        text content
    }

    POST {
        uuid id PK
        varchar title
    }

    VIDEO {
        uuid id PK
        varchar title
    }
```

### Soft Deletes

```mermaid
erDiagram
    USER {
        uuid id PK
        varchar email UK
        varchar name
        timestamp deleted_at
    }
```

### Audit Trail

```mermaid
erDiagram
    DOCUMENT ||--o{ DOCUMENT_VERSION : has

    DOCUMENT {
        uuid id PK
        varchar title
        int current_version
    }

    DOCUMENT_VERSION {
        uuid id PK
        uuid document_id FK
        int version_number
        text content
        uuid modified_by FK
        timestamp created_at
    }
```

## Direction

Control layout direction:

```mermaid
erDiagram
    direction LR
    CUSTOMER ||--o{ ORDER : places
```

Directions: `TB` (default), `BT`, `LR`, `RL`

## Entity Aliases

```mermaid
erDiagram
    CUSTOMER ["Customer Account"] {
        uuid id PK
        string name
    }
```

## Layout

For complex ERDs, use ELK layout via YAML frontmatter:

```mermaid
---
config:
  layout: elk
---
erDiagram
    CUSTOMER ||--o{ ORDER : places
```

## Best Practices

1. **NEVER use `\n`** — Use `<br>` in labels if multi-line text is needed
2. **UPPERCASE entity names** — Standard convention
3. **Singular names** — `USER` not `USERS`
4. **Define all constraints** — PKs, FKs, UKs, NOT NULL
5. **Show cardinality accurately** — Be precise about relationships
6. **Include timestamps** — `created_at`, `updated_at` for auditing
7. **Document computed columns** — Mark derived values
8. **Consider junction tables** — Explicitly model many-to-many
9. **Use appropriate types** — Match database-specific types
10. **Plan for soft deletes** — Add `deleted_at` columns
11. **Version critical data** — Maintain history for important entities
