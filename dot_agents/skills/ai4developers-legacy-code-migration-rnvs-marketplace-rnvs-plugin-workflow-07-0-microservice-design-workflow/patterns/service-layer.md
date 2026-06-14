# Service Layer Patterns

Spring Boot service layer patterns for VNRM microservices.

## Service Template

```java
package com.telekom.vnrm.${submodule}.${service}.service;

import com.telekom.vnrm.${submodule}.${service}.domain.${EntityName};
import com.telekom.vnrm.${submodule}.${service}.domain.${EntityName}Status;
import com.telekom.vnrm.${submodule}.${service}.dto.${EntityName}CreateRequest;
import com.telekom.vnrm.${submodule}.${service}.dto.${EntityName}UpdateRequest;
import com.telekom.vnrm.${submodule}.${service}.dto.${EntityName}Response;
import com.telekom.vnrm.${submodule}.${service}.exception.${EntityName}NotFoundException;
import com.telekom.vnrm.${submodule}.${service}.exception.BusinessRuleViolationException;
import com.telekom.vnrm.${submodule}.${service}.mapper.${EntityName}Mapper;
import com.telekom.vnrm.${submodule}.${service}.repository.${EntityName}Repository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

/**
 * Service for ${EntityName} business operations
 *
 * Business Rules:
 * - ${BR-XXX}: ${rule_description}
 */
@Service
@RequiredArgsConstructor
@Slf4j
@Transactional(readOnly = true)
public class ${EntityName}Service {

    private final ${EntityName}Repository repository;
    private final ${EntityName}Mapper mapper;
    private final ${EntityName}Validator validator;

    /**
     * Create new ${EntityName}
     * Enforces: ${BR-XXX}
     */
    @Transactional
    public ${EntityName}Response create(${EntityName}CreateRequest request) {
        log.info("Creating ${EntityName}: {}", request);

        // Validate business rules
        validator.validateCreate(request);

        // Check uniqueness
        if (repository.existsBy${UniqueField}(request.get${UniqueField}())) {
            throw new BusinessRuleViolationException("BR-XXX",
                "${EntityName} with ${uniqueField} already exists");
        }

        // Map and save
        ${EntityName} entity = mapper.toEntity(request);
        entity.setStatus(${EntityName}Status.PENDING);

        ${EntityName} saved = repository.save(entity);
        log.info("Created ${EntityName} with id: {}", saved.getId());

        return mapper.toResponse(saved);
    }

    /**
     * Get ${EntityName} by ID
     */
    public ${EntityName}Response getById(Long id) {
        return repository.findById(id)
            .map(mapper::toResponse)
            .orElseThrow(() -> new ${EntityName}NotFoundException(id));
    }

    /**
     * Get ${EntityName} by unique field
     */
    public ${EntityName}Response getBy${UniqueField}(String ${uniqueField}) {
        return repository.findBy${UniqueField}(${uniqueField})
            .map(mapper::toResponse)
            .orElseThrow(() -> new ${EntityName}NotFoundException(${uniqueField}));
    }

    /**
     * Get all ${EntityName}s with pagination
     */
    public Page<${EntityName}Response> getAll(Pageable pageable) {
        return repository.findAll(pageable)
            .map(mapper::toResponse);
    }

    /**
     * Get ${EntityName}s by status
     */
    public List<${EntityName}Response> getByStatus(${EntityName}Status status) {
        return repository.findByStatus(status).stream()
            .map(mapper::toResponse)
            .toList();
    }

    /**
     * Update ${EntityName}
     * Enforces: ${BR-XXX}
     */
    @Transactional
    public ${EntityName}Response update(Long id, ${EntityName}UpdateRequest request) {
        log.info("Updating ${EntityName} id={}: {}", id, request);

        ${EntityName} entity = repository.findById(id)
            .orElseThrow(() -> new ${EntityName}NotFoundException(id));

        // Validate business rules
        validator.validateUpdate(entity, request);

        // Apply updates
        mapper.updateEntity(entity, request);

        ${EntityName} saved = repository.save(entity);
        log.info("Updated ${EntityName} id={}", id);

        return mapper.toResponse(saved);
    }

    /**
     * Delete ${EntityName} (soft delete)
     */
    @Transactional
    public void delete(Long id) {
        log.info("Deleting ${EntityName} id={}", id);

        ${EntityName} entity = repository.findById(id)
            .orElseThrow(() -> new ${EntityName}NotFoundException(id));

        // Soft delete
        entity.setStatus(${EntityName}Status.DELETED);
        repository.save(entity);

        log.info("Deleted ${EntityName} id={}", id);
    }
}
```

## Validator Template

```java
package com.telekom.vnrm.${submodule}.${service}.service;

import com.telekom.vnrm.${submodule}.${service}.dto.${EntityName}CreateRequest;
import com.telekom.vnrm.${submodule}.${service}.dto.${EntityName}UpdateRequest;
import com.telekom.vnrm.${submodule}.${service}.domain.${EntityName};
import com.telekom.vnrm.${submodule}.${service}.exception.BusinessRuleViolationException;
import org.springframework.stereotype.Component;

/**
 * Business rule validator for ${EntityName}
 */
@Component
public class ${EntityName}Validator {

    /**
     * Validate creation request
     * @throws BusinessRuleViolationException if validation fails
     */
    public void validateCreate(${EntityName}CreateRequest request) {
        // BR-XXX: ${rule_description}
        if (/* condition */) {
            throw new BusinessRuleViolationException("BR-XXX", "${error_message}");
        }
    }

    /**
     * Validate update request
     * @throws BusinessRuleViolationException if validation fails
     */
    public void validateUpdate(${EntityName} entity, ${EntityName}UpdateRequest request) {
        // BR-XXX: Cannot update deleted entities
        if (entity.getStatus() == ${EntityName}Status.DELETED) {
            throw new BusinessRuleViolationException("BR-XXX", "Cannot update deleted entity");
        }
    }
}
```

## Event Publishing Pattern

```java
@Service
@RequiredArgsConstructor
@Slf4j
public class ${EntityName}Service {

    private final ApplicationEventPublisher eventPublisher;

    @Transactional
    public ${EntityName}Response create(${EntityName}CreateRequest request) {
        // ... create logic ...

        ${EntityName} saved = repository.save(entity);

        // Publish domain event
        eventPublisher.publishEvent(new ${EntityName}CreatedEvent(saved));

        return mapper.toResponse(saved);
    }
}
```

## Integration with External Services

```java
@Service
@RequiredArgsConstructor
@Slf4j
public class ${EntityName}Service {

    private final ExternalServiceClient externalClient;

    @CircuitBreaker(name = "externalService", fallbackMethod = "fallbackMethod")
    @Retry(name = "externalService")
    @Transactional
    public ${EntityName}Response createWithExternalValidation(${EntityName}CreateRequest request) {
        // Call external service
        ExternalResponse response = externalClient.validate(request);

        if (!response.isValid()) {
            throw new BusinessRuleViolationException("EXT-001", response.getMessage());
        }

        // Continue with creation
        return create(request);
    }

    private ${EntityName}Response fallbackMethod(${EntityName}CreateRequest request, Exception e) {
        log.warn("External service unavailable, using fallback: {}", e.getMessage());
        // Fallback logic
        throw new ServiceUnavailableException("External validation service unavailable");
    }
}
```

## Transaction Patterns

### Read-Only by Default

```java
@Service
@Transactional(readOnly = true)  // Default read-only
public class ${EntityName}Service {

    @Transactional  // Override for write operations
    public ${EntityName}Response create(...) { }
}
```

### Propagation Patterns

```java
// REQUIRED (default) - Join existing or create new
@Transactional(propagation = Propagation.REQUIRED)

// REQUIRES_NEW - Always create new (independent)
@Transactional(propagation = Propagation.REQUIRES_NEW)

// MANDATORY - Must have existing transaction
@Transactional(propagation = Propagation.MANDATORY)
```

## Best Practices

1. **Use @RequiredArgsConstructor** for constructor injection
2. **Add @Slf4j** for logging
3. **Default to @Transactional(readOnly = true)** at class level
4. **Validate business rules** before mutations
5. **Publish domain events** for cross-cutting concerns
6. **Use circuit breakers** for external calls
7. **Log method entry/exit** for debugging
8. **Soft delete** instead of hard delete
