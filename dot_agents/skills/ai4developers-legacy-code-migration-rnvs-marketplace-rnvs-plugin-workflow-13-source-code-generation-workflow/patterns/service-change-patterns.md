# Service Change Patterns

Patterns for adding and modifying Spring Boot service classes in CHANGE mode.

## Pattern 1: Add New Method to Existing Service

When adding a new method to an existing service:

```java
// MODIFICATION: Add to existing service after last method

    /**
     * ${method_description}
     * Implements: ${business_rule_id}
     * RNVS Source: ${rnvs_source_reference}
     * Tested by: ${test_class}.${test_method}()
     *
     * @param ${param_name} ${param_description}
     * @return ${return_description}
     * @throws ${exception_type} ${exception_condition}
     */
    @Transactional${readonly_if_query}
    public ${ReturnType} ${methodName}(${Parameters}) {
        log.info("${method_name} called with: {}", ${log_params});

        // Validate business rules
        ${validation_logic}

        // Execute business logic
        ${business_logic}

        // Publish event if needed
        ${event_publishing}

        return ${return_value};
    }
```

### Example: Add validation method to FeatureService

```java
// File: src/main/java/com/vnrm/feature/service/FeatureServiceImpl.java
// EDIT: Add after line 120 (after updateFeature method)

    /**
     * Validate feature configuration before activation.
     * Implements: BR-FEAT-005
     * RNVS Source: RNVS.Feature.ValidateConfig (feature_handler.tcl:234-289)
     * Tested by: FeatureServiceTest.shouldValidateConfiguration()
     *
     * @param featureId The feature ID to validate
     * @param request The validation request with configuration params
     * @return ValidationResult with status and any validation errors
     * @throws FeatureNotFoundException if feature does not exist
     */
    @Transactional(readOnly = true)
    public ValidationResult validateConfiguration(Long featureId, ValidationRequest request) {
        log.info("Validating configuration for feature: {}", featureId);

        // Fetch feature
        Feature feature = featureRepository.findById(featureId)
                .orElseThrow(() -> new FeatureNotFoundException(featureId));

        // Validate business rules
        List<ValidationError> errors = new ArrayList<>();

        // Rule 1: Configuration must be complete
        if (request.getConfig() == null || request.getConfig().isEmpty()) {
            errors.add(new ValidationError("CONFIG_EMPTY", "Configuration cannot be empty"));
        }

        // Rule 2: Feature must be in valid state for validation
        if (!feature.getStatus().equals(FeatureStatus.DRAFT)) {
            errors.add(new ValidationError("INVALID_STATE",
                    "Feature must be in DRAFT state for validation"));
        }

        // Rule 3: Check external dependencies
        if (request.isCheckDependencies()) {
            List<String> missingDeps = checkDependencies(feature);
            if (!missingDeps.isEmpty()) {
                errors.add(new ValidationError("MISSING_DEPENDENCIES",
                        "Missing dependencies: " + String.join(", ", missingDeps)));
            }
        }

        log.info("Validation complete for feature {}: {} errors found",
                featureId, errors.size());

        return ValidationResult.builder()
                .featureId(featureId)
                .valid(errors.isEmpty())
                .errors(errors)
                .validatedAt(Instant.now())
                .build();
    }

    private List<String> checkDependencies(Feature feature) {
        // Implementation for dependency checking
        return Collections.emptyList();
    }
```

---

## Pattern 2: Create New Service

When creating a new service class:

```java
package ${base_package}.service;

import ${base_package}.dto.${RequestDto};
import ${base_package}.dto.${ResponseDto};
import ${base_package}.entity.${Entity};
import ${base_package}.exception.${ResourceNotFoundException};
import ${base_package}.mapper.${MapperName};
import ${base_package}.repository.${RepositoryName};
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import de.telekom.horizon.client.HorizonClient;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

/**
 * Service for ${resource_name} business operations.
 * Implements: ${business_rule_ids}
 * RNVS Source: ${rnvs_module_reference}
 *
 * @since ${version}
 */
@Service
@RequiredArgsConstructor
@Slf4j
@Transactional
public class ${ResourceName}ServiceImpl implements ${ResourceName}Service {

    private final ${RepositoryName} repository;
    private final ${MapperName} mapper;
    private final HorizonClient horizonClient;

    /**
     * Find all ${resource_plural}.
     * Tested by: ${ServiceTest}.shouldFindAll()
     */
    @Override
    @Transactional(readOnly = true)
    public List<${ResponseDto}> findAll() {
        log.debug("Finding all ${resource_plural}");
        return repository.findAll().stream()
                .map(mapper::toDto)
                .collect(Collectors.toList());
    }

    /**
     * Find ${resource_name} by ID.
     * Tested by: ${ServiceTest}.shouldFindById()
     */
    @Override
    @Transactional(readOnly = true)
    public Optional<${ResponseDto}> findById(Long id) {
        log.debug("Finding ${resource_name} by id: {}", id);
        return repository.findById(id)
                .map(mapper::toDto);
    }

    /**
     * Create new ${resource_name}.
     * Implements: ${create_business_rule}
     * Tested by: ${ServiceTest}.shouldCreate()
     */
    @Override
    public ${ResponseDto} create(${RequestDto} request) {
        log.info("Creating ${resource_name}: {}", request);

        // Validate uniqueness
        if (repository.existsByName(request.getName())) {
            throw new ${ResourceName}AlreadyExistsException(request.getName());
        }

        // Create entity
        ${Entity} entity = mapper.toEntity(request);
        entity.setCreatedAt(Instant.now());

        // Save
        ${Entity} saved = repository.save(entity);
        log.info("${resource_name} created with id: {}", saved.getId());

        // Publish event
        publishEvent("${RESOURCE}_CREATED", saved);

        return mapper.toDto(saved);
    }

    /**
     * Update ${resource_name}.
     * Implements: ${update_business_rule}
     * Tested by: ${ServiceTest}.shouldUpdate()
     */
    @Override
    public Optional<${ResponseDto}> update(Long id, ${RequestDto} request) {
        log.info("Updating ${resource_name} id: {}", id);

        return repository.findById(id)
                .map(existing -> {
                    mapper.updateEntity(request, existing);
                    existing.setUpdatedAt(Instant.now());
                    ${Entity} updated = repository.save(existing);

                    publishEvent("${RESOURCE}_UPDATED", updated);

                    return mapper.toDto(updated);
                });
    }

    /**
     * Delete ${resource_name}.
     * Tested by: ${ServiceTest}.shouldDelete()
     */
    @Override
    public void delete(Long id) {
        log.info("Deleting ${resource_name} id: {}", id);

        if (!repository.existsById(id)) {
            throw new ${ResourceNotFoundException}(id);
        }

        repository.deleteById(id);

        // Publish deletion event
        publishEvent("${RESOURCE}_DELETED", id);
    }

    private void publishEvent(String eventType, Object payload) {
        try {
            HorizonEvent<Object> event = HorizonEvent.builder()
                    .withEventType(eventType)
                    .withPayload(payload)
                    .withCorrelationId(UUID.randomUUID().toString())
                    .build();
            horizonClient.publish(event);
            log.debug("Published Horizon event: {}", eventType);
        } catch (Exception e) {
            log.error("Failed to publish Horizon event: {}", eventType, e);
        }
    }
}
```

---

## Pattern 3: Add Helper Method

When adding a private helper method:

```java
// MODIFICATION: Add private helper method

    /**
     * ${helper_description}
     * Used by: ${calling_methods}
     */
    private ${ReturnType} ${helperMethodName}(${Parameters}) {
        ${implementation}
    }
```

---

## Pattern 4: Add Caching

When adding caching to an existing method:

```java
// MODIFICATION: Add @Cacheable annotation

    @Override
    @Transactional(readOnly = true)
    @Cacheable(value = "${cache_name}", key = "#id")  // ADDED
    public Optional<${ResponseDto}> findById(Long id) {
        log.debug("Finding ${resource_name} by id: {}", id);
        return repository.findById(id)
                .map(mapper::toDto);
    }
```

---

## Anti-Patterns to Avoid

1. **Don't skip transactions**: Use @Transactional for write operations
2. **Don't forget readOnly**: Use @Transactional(readOnly = true) for queries
3. **Don't swallow exceptions**: Log and rethrow or handle appropriately
4. **Don't skip event publishing**: Publish events for state changes
5. **Don't hardcode values**: Use configuration properties
