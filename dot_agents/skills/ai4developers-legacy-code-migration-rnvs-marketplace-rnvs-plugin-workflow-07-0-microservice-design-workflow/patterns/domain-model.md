# Domain Model Patterns

Spring Boot domain model patterns for VNRM microservices.

## Entity Template

```java
package com.telekom.vnrm.${submodule}.${service}.domain;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDateTime;

/**
 * ${EntityName} - ${description}
 *
 * Business Rules:
 * - ${BR-XXX}: ${rule_description}
 */
@Entity
@Table(name = "${table_name}", indexes = {
    @Index(name = "idx_${table_name}_${indexed_field}", columnList = "${indexed_field}"),
    @Index(name = "idx_${table_name}_created_at", columnList = "created_at")
})
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ${EntityName} {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "${field_name}", nullable = false, length = ${length})
    private String ${fieldName};

    @Enumerated(EnumType.STRING)
    @Column(name = "status", nullable = false)
    private ${EntityName}Status status;

    @Version
    private Long version;

    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    @Column(name = "created_by", length = 100)
    private String createdBy;

    @Column(name = "updated_by", length = 100)
    private String updatedBy;
}
```

## Status Enum Template

```java
package com.telekom.vnrm.${submodule}.${service}.domain;

/**
 * Status enumeration for ${EntityName}
 */
public enum ${EntityName}Status {
    PENDING,
    ACTIVE,
    INACTIVE,
    DELETED
}
```

## Value Object Template

```java
package com.telekom.vnrm.${submodule}.${service}.domain;

import jakarta.persistence.Embeddable;
import lombok.*;

/**
 * ${ValueObjectName} - Immutable value object
 */
@Embeddable
@Getter
@NoArgsConstructor
@AllArgsConstructor
@EqualsAndHashCode
public class ${ValueObjectName} {

    private String ${field1};
    private String ${field2};

    public static ${ValueObjectName} of(String ${field1}, String ${field2}) {
        return new ${ValueObjectName}(${field1}, ${field2});
    }
}
```

## Relationship Patterns

### One-to-Many

```java
@OneToMany(mappedBy = "parent", cascade = CascadeType.ALL, orphanRemoval = true)
private List<ChildEntity> children = new ArrayList<>();
```

### Many-to-One

```java
@ManyToOne(fetch = FetchType.LAZY)
@JoinColumn(name = "parent_id", nullable = false)
private ParentEntity parent;
```

### Many-to-Many

```java
@ManyToMany
@JoinTable(
    name = "${join_table_name}",
    joinColumns = @JoinColumn(name = "${entity1}_id"),
    inverseJoinColumns = @JoinColumn(name = "${entity2}_id")
)
private Set<OtherEntity> others = new HashSet<>();
```

## Audit Fields Pattern

All entities should include:
- `version` - Optimistic locking
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp
- `created_by` - User who created
- `updated_by` - User who last updated

## VNRM-Specific Patterns

### Callnumber Entity (NUM submodule)

```java
@Column(name = "callnumber", nullable = false, length = 20)
private String callnumber;

@Column(name = "area_code", length = 10)
private String areaCode;

@Column(name = "subscriber_number", length = 15)
private String subscriberNumber;

@Enumerated(EnumType.STRING)
@Column(name = "number_type")
private CallnumberType numberType;
```

### Porting Entity (PRT submodule)

```java
@Column(name = "porting_id", nullable = false, unique = true)
private String portingId;

@Column(name = "donor_provider", length = 50)
private String donorProvider;

@Column(name = "recipient_provider", length = 50)
private String recipientProvider;

@Column(name = "porting_date")
private LocalDate portingDate;

@Enumerated(EnumType.STRING)
@Column(name = "porting_status")
private PortingStatus portingStatus;
```

## Best Practices

1. **Always use optimistic locking** with `@Version`
2. **Add indexes** for frequently queried columns
3. **Use lazy loading** for relationships
4. **Document business rules** in entity Javadoc
5. **Prefer composition** over inheritance
6. **Use value objects** for composite values
