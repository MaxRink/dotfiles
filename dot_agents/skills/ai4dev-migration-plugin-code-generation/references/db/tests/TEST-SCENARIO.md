# Test Scenarios for db-codegen

Validation scenarios for the database schema design skill within the code-generation workflow.

## Test Case 1: E-commerce Platform (PostgreSQL + Java Spring Boot)

### Input Context

Spec artifacts contain:

**contracts.md section 3:**

```text
## 3. Database Contracts
- Database Type: PostgreSQL 15
- Connection: JDBC via HikariCP connection pool
- Schema: public schema, application user with READ/WRITE
- Transactions: ACID required, @Transactional on service layer
```

**technical-plan.md section 4:**

```text
## 4. Data Implementation
Entities: User, Product, Category, Order, OrderItem, Review
Relationships:
  - User 1:N Orders
  - Order 1:N OrderItems
  - Product N:M Orders (via OrderItems)
  - Category 1:N Products (hierarchical, self-referencing)
  - User 1:N Reviews, Product 1:N Reviews
Expected volume: 100K users, 10K products
Read/write pattern: Read-heavy
```

### Expected Output

```text
database/
├── schema.sql                        # ~300-400 lines
├── migrations/
│   ├── 001_initial_schema.up.sql
│   └── 001_initial_schema.down.sql
├── seeds/
│   └── sample_data.sql
└── docs/
    ├── ERD.md                        # Mermaid ERD with all 6 entities
    └── SCHEMA.md

src/main/resources/db/migration/
└── V1__initial_schema.sql            # Flyway format (duplicate of canonical)
```

### Validation Checklist

- [ ] `database/schema.sql` is valid PostgreSQL DDL
- [ ] Uses `gen_random_uuid()` for UUIDs
- [ ] Uses `TIMESTAMPTZ` for timestamps
- [ ] All FK columns have indexes
- [ ] Composite index on (category_id, price) for read-heavy product browsing
- [ ] CHECK constraints: price >= 0, rating BETWEEN 1 AND 5
- [ ] `update_updated_at_column()` trigger function created
- [ ] Junction table `order_items` for Order-Product N:M
- [ ] Self-referencing `parent_id` on categories
- [ ] Flyway migration in `src/main/resources/db/migration/V1__initial_schema.sql`
- [ ] ERD.md shows all entities with PK/FK/UK markers
- [ ] Seed data references valid FK values

## Test Case 2: Blog Platform (MySQL + Python FastAPI)

### Input Context

**contracts.md section 3:**

```text
## 3. Database Contracts
- Database Type: MySQL 8.0
- Connection: SQLAlchemy async via aiomysql
- Schema: blog_db, application user with CRUD permissions
```

**technical-plan.md section 4:**

```text
## 4. Data Implementation
Entities: User, Post, Comment, Tag
Relationships:
  - User 1:N Posts
  - Post 1:N Comments (nested, self-referencing parent_comment_id)
  - Post N:M Tags (junction table post_tags)
Write-heavy workload
```

### Expected Output

```text
database/
├── schema.sql                        # MySQL DDL
├── migrations/
│   ├── 001_initial_schema.up.sql
│   └── 001_initial_schema.down.sql
├── seeds/
│   └── sample_data.sql
└── docs/
    ├── ERD.md
    └── SCHEMA.md

alembic/versions/
└── 001_initial_schema.py             # Alembic format
```

### Validation Checklist

- [ ] Uses `ENGINE=InnoDB`, `CHARACTER SET utf8mb4`
- [ ] Uses `CHAR(36)` for UUIDs or `BIGINT AUTO_INCREMENT`
- [ ] Uses `DATETIME(6)` for timestamps
- [ ] `ON UPDATE CURRENT_TIMESTAMP(6)` for auto-update
- [ ] Junction table `post_tags` for Post-Tag N:M
- [ ] Self-referencing `parent_comment_id` on comments
- [ ] Alembic migration in `alembic/versions/001_initial_schema.py`
- [ ] Write-heavy: full normalization, minimal indexes

## Test Case 3: No Database Contracts (No DB Tasks Generated)

### Input Context

Spec artifacts have NO database section:

- `contracts.md` has only REST and Messaging contracts (sections 1, 2)
- `technical-plan.md` section 4 says "No database — uses external API"

### Expected Behavior

- NO `database/` directory created
- NO DB setup tasks in Step 3
- Code generation proceeds normally without DB tasks
- Zero regression from existing behavior

## Quick Validation

After code generation completes with DB tasks:

```bash
# Verify structure
ls -R <output-dir>/database/

# Count tables in schema
grep -c "CREATE TABLE" <output-dir>/database/schema.sql

# Verify ERD has mermaid diagram
grep "erDiagram" <output-dir>/database/docs/ERD.md

# Verify migrations are reversible
test -f <output-dir>/database/migrations/001_initial_schema.down.sql

# Verify seed data
grep -c "INSERT INTO" <output-dir>/database/seeds/sample_data.sql
```

## Success Criteria

1. All output files generated in correct structure
2. ERD.md contains complete Mermaid diagram with all entities and relationships
3. schema.sql is valid DDL for the target database type
4. Migrations are transactional (BEGIN/COMMIT) and reversible
5. Framework-specific migration generated in correct path (Flyway/Alembic)
6. Seed data is realistic with valid FK references
7. SCHEMA.md explains design decisions
8. Indexes optimized for workload pattern (read-heavy vs write-heavy)
9. No DB artifacts when contracts.md has no database section
