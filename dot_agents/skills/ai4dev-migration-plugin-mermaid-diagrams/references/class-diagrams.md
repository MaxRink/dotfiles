# Class Diagrams

Class diagrams visualize object-oriented systems, showing entities, their properties, methods, and relationships.

## Contents

- [Basic Syntax](#basic-syntax)
- [Visibility Modifiers](#visibility-modifiers)
- [Relationships](#relationships)
- [Multiplicity](#multiplicity)
- [Annotations](#annotations)
- [Complete Example: E-Commerce Domain](#complete-example-e-commerce-domain)
- [Design Patterns](#design-patterns)
- [Best Practices](#best-practices)

## Basic Syntax

```mermaid
classDiagram
    class ClassName {
        +String publicAttribute
        -int privateAttribute
        #bool protectedAttribute
        ~float packageAttribute
        +publicMethod()
        -privateMethod()
    }
```

## Visibility Modifiers

| Symbol | Visibility |
|--------|------------|
| `+` | Public |
| `-` | Private |
| `#` | Protected |
| `~` | Package/Internal |

## Relationships

### Association (loose connection)

```mermaid
classDiagram
    ClassA -- ClassB
```

### Composition (strong ownership - child cannot exist without parent)

```mermaid
classDiagram
    Parent *-- Child
```

### Aggregation (weak ownership - child can exist independently)

```mermaid
classDiagram
    Container o-- Element
```

### Inheritance

```mermaid
classDiagram
    Parent <|-- Child
```

### Dependency

```mermaid
classDiagram
    ClassA <.. ClassB
```

### Implementation (interface)

```mermaid
classDiagram
    Interface <|.. Implementation
```

## Multiplicity

```mermaid
classDiagram
    Customer "1" --> "*" Order : places
    Order "1" --> "1..*" LineItem : contains
```

| Notation | Meaning |
|----------|---------|
| `1` | Exactly one |
| `0..1` | Zero or one |
| `*` | Many (zero or more) |
| `1..*` | One or more |
| `n..m` | Range from n to m |

## Annotations

```mermaid
classDiagram
    class Shape {
        <<abstract>>
        +draw()
    }
    class IDrawable {
        <<interface>>
        +render()
    }
    class PaymentType {
        <<enumeration>>
        CREDIT
        DEBIT
        CASH
    }
```

## Complete Example: E-Commerce Domain

```mermaid
classDiagram
    class Customer {
        +UUID id
        +String email
        +String name
        +register()
        +login()
        +placeOrder()
    }

    class Order {
        +UUID id
        +Date orderDate
        +OrderStatus status
        +Decimal total
        +submit()
        +cancel()
        +calculateTotal()
    }

    class LineItem {
        +int quantity
        +Decimal unitPrice
        +getSubtotal()
    }

    class Product {
        +UUID id
        +String name
        +Decimal price
        +int stockQuantity
        +isAvailable()
    }

    class Payment {
        <<abstract>>
        +Decimal amount
        +process()
    }

    class CreditCardPayment {
        +String cardNumber
        +Date expiry
        +process()
    }

    class PayPalPayment {
        +String email
        +process()
    }

    Customer "1" --> "*" Order : places
    Order "1" *-- "1..*" LineItem : contains
    LineItem "*" --> "1" Product : references
    Order "1" --> "0..1" Payment : paidWith
    Payment <|-- CreditCardPayment
    Payment <|-- PayPalPayment
```

## Design Patterns

### Repository Pattern

```mermaid
classDiagram
    class IRepository~T~ {
        <<interface>>
        +findById(id) T
        +findAll() List~T~
        +save(entity)
        +delete(entity)
    }
    class UserRepository {
        +findById(id) User
        +findByEmail(email) User
    }
    IRepository~T~ <|.. UserRepository
```

### Factory Pattern

```mermaid
classDiagram
    class PaymentFactory {
        +createPayment(type) Payment
    }
    class Payment {
        <<abstract>>
        +process()
    }
    class CreditCard
    class PayPal
    class BankTransfer

    PaymentFactory ..> Payment : creates
    Payment <|-- CreditCard
    Payment <|-- PayPal
    Payment <|-- BankTransfer
```

### Strategy Pattern

```mermaid
classDiagram
    class ShippingStrategy {
        <<interface>>
        +calculateCost(order) Decimal
    }
    class StandardShipping {
        +calculateCost(order) Decimal
    }
    class ExpressShipping {
        +calculateCost(order) Decimal
    }
    class Order {
        -ShippingStrategy strategy
        +setShippingStrategy(strategy)
        +getShippingCost() Decimal
    }

    ShippingStrategy <|.. StandardShipping
    ShippingStrategy <|.. ExpressShipping
    Order o-- ShippingStrategy
```

## Namespaces

Group related classes:

```mermaid
classDiagram
    namespace Domain {
        class User {
            +String email
        }
        class Order {
            +UUID id
        }
    }
    namespace Infrastructure {
        class UserRepository
        class OrderRepository
    }
```

## Notes

```mermaid
classDiagram
    class User {
        +String email
    }
    note "Domain aggregate root"
    note for User "Immutable after creation"
```

## Lollipop Interface

```mermaid
classDiagram
    class UserService
    class IRepository
    UserService ()-- IRepository
```

## Direction

Control layout direction:

```mermaid
classDiagram
    direction LR
    class A
    class B
    A --> B
```

Directions: `TB` (top-bottom, default), `BT`, `LR`, `RL`

## Styling

```mermaid
classDiagram
    class User:::highlight {
        +String email
    }
    classDef highlight fill:#f9f,stroke:#333
    style User fill:#bbf,stroke:#333
```

## Best Practices

1. **NEVER use `\n`** — Use `<br>` in labels if multi-line text is needed
2. **Focus on core entities** — Omit trivial details
3. **Choose appropriate relationships** — Use composition vs aggregation correctly
4. **Show multiplicity** — Document cardinality explicitly
5. **Use annotations** — Mark interfaces, abstracts, enums
6. **Use namespaces** — Group related classes logically
7. **Document business rules** — Add notes for important constraints
