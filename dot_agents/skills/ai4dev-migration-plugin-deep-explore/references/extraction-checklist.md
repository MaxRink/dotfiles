# Module Extraction Checklist

> For each module (within tier budget), extract the following by reading the actual source code.
> Skip any category that does not apply to the module. Do not produce empty sections.

## Classes and Components

For EVERY significant class/component:

- Full class name, file path with line number
- Purpose and responsibility (single responsibility principle — what is this class's one job?)
- Constructor parameters and what they inject
- All public properties with types and descriptions
- All public methods with: full signature, purpose, parameters (name, type, description), return type, side effects (DB writes, API calls, events emitted, state mutations), exceptions/errors thrown
- Inheritance chain — parent classes and interfaces implemented
- Design patterns used (Factory, Strategy, Observer, Repository, etc.)
- Lifecycle hooks (init, destroy, beforeEach, etc.)

## Functions

For EVERY exported/public function:

- Full signature with types
- Purpose and when it's called
- Parameters and return values
- Side effects and error conditions
- Closure over external state

## API Endpoints

For EVERY HTTP/gRPC/GraphQL endpoint:

- Method and full path (e.g., `POST /api/v2/orders`)
- Purpose — what business operation does this perform?
- Request: headers, path params, query params, body schema with ALL fields, types, constraints, and examples
- Response: success shape with ALL fields, error shapes with codes and messages
- Authentication requirement (none, JWT, API key, session, OAuth)
- Authorization requirement (roles, permissions, ownership checks)
- Rate limiting or throttling
- Middleware chain applied
- Validation rules on input
- Which service/business logic method is called

## Data Models

For EVERY entity/model/DTO/schema:

- Full class/type definition with ALL fields
- Field types, nullability, default values, constraints (min/max, regex, unique, etc.)
- Relationships to other models (one-to-one, one-to-many, many-to-many) with join columns/foreign keys
- Database table mapping (table name, column names if different from field names)
- Indexes and constraints at the database level
- Validation decorators/annotations
- Serialization rules (JSON field names, excluded fields, computed fields)
- Soft delete, timestamps, versioning patterns

## Business Logic

For EVERY business rule or algorithm:

- What is the rule? (e.g., "Orders over $500 require manager approval")
- Where is it enforced? (file:line)
- What triggers it? (API call, event, scheduled job)
- What are the conditions? (if/else logic, switch cases)
- What are the outcomes? (state changes, notifications, side effects)
- Edge cases and error handling
- Configuration that affects the rule (feature flags, thresholds, constants)

## State Management

For applications with frontend or stateful backends:

- State shape/schema
- Actions/mutations/reducers
- State transitions and their triggers
- Persistence (localStorage, sessionStorage, cookies, URL state)
- State synchronization patterns

## Configuration

For each module:

- Environment variables used (name, purpose, default value, required/optional)
- Config files read
- Feature flags
- Constants and magic numbers with their meaning

## Error Handling

For each module:

- Custom exception/error classes
- Error codes and their meanings
- Retry strategies
- Fallback behavior
- Error reporting (logging, monitoring, alerting)

## Events and Messaging

For each event:

- Event name/type
- Publisher (which module/class emits it)
- Payload shape with all fields
- Subscribers (which modules/classes handle it)
- Ordering guarantees
- Failure handling (dead letter, retry)

## Security

For each module:

- Authentication mechanisms (JWT validation, session checks, API key verification — where and how)
- Authorization model (RBAC roles, ABAC policies, ownership checks, permission guards)
- Input sanitization and validation (XSS prevention, SQL injection prevention, CSRF tokens)
- Secrets handling (where secrets are loaded, how they're injected, any hardcoded credentials found)
- Encryption (at rest, in transit — algorithms, key management)
- CORS configuration
- Security headers and CSP policies
- Audit logging (what actions are logged, where, in what format)

## Database Details

For each database interaction:

- Full schema: tables, columns, types, constraints, indexes, partitions
- Migration files and migration history (what ORM migration tool is used, naming convention)
- Stored procedures, triggers, views, functions
- Query patterns (ORM usage, raw SQL, query builders — with examples)
- Connection pooling configuration
- Transaction boundaries and isolation levels
- Seed data and fixtures

## Testing

For each module:

- Test framework(s) used (JUnit, pytest, Jest, etc.)
- Test types present (unit, integration, e2e, contract, performance)
- Test file locations and naming conventions
- Test coverage (if measurable from config)
- Mocking/stubbing patterns (what's mocked, how)
- Test fixtures, factories, builders
- Test data management (in-memory DB, test containers, seed scripts)
- CI test pipeline configuration

## Concurrency and Threading

When applicable:

- Threading model (single-threaded, thread pool, async/await, actors)
- Locks, mutexes, semaphores — where and why
- Race condition guards
- Async patterns (promises, futures, coroutines, callbacks)
- Queue/worker concurrency configuration
- Connection pool sizes and timeout settings

## Performance Characteristics

When observable:

- Caching strategies (what's cached, TTL, invalidation triggers)
- Connection pooling configuration
- Batch processing patterns
- Pagination strategies
- Lazy loading vs eager loading patterns
- Known N+1 query patterns
- Rate limiting implementation

## Internationalization

When present:

- i18n framework used
- Translation file locations and format
- Locale detection and switching
- Date/number/currency formatting patterns
- RTL support

## Deployment and Infrastructure

Per module or system-wide:

- Dockerfile and container configuration
- Docker Compose services and networking
- Kubernetes manifests (deployments, services, ingress, config maps, secrets)
- Health check and readiness probe endpoints
- Scaling configuration (replicas, HPA, resource limits)
- Environment-specific configuration (dev/staging/prod differences)
- CI/CD pipeline stages and scripts

## Technical Debt and Known Issues

What the code itself reveals:

- TODO/FIXME/HACK/XXX comments with context
- Deprecated code and migration warnings
- Suppressed warnings and lint ignores with reasons
- Workarounds with explanations
- Dead code (unused exports, unreachable branches)
- Coupling issues (god classes, circular imports, tight coupling)
