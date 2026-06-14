# Controller Change Patterns

Patterns for adding and modifying Spring Boot REST controllers in CHANGE mode.

## Pattern 1: Add New Endpoint to Existing Controller

When adding a new endpoint to an existing controller:

```java
// MODIFICATION: Add to existing controller after last endpoint method

    /**
     * ${endpoint_description}
     * Implements: ${business_rule_id}
     * RNVS Source: ${rnvs_source_reference}
     * Tested by: ${test_class}.${test_method}()
     */
    @${HttpMethod}Mapping("${path}")
    @Operation(summary = "${operation_summary}")
    public ResponseEntity<${ResponseType}> ${methodName}(
            ${parameters}) {
        log.info("${HttpMethod} ${path} - ${log_message}");
        ${service_call}
        return ResponseEntity.ok(result);
    }
```

### Example: Add POST endpoint to FeatureController

```java
// File: src/main/java/com/vnrm/feature/controller/FeatureController.java
// EDIT: Add after line 85 (after last existing method)

    /**
     * Validate feature configuration before activation.
     * Implements: BR-FEAT-005
     * RNVS Source: RNVS.Feature.ValidateConfig (feature_handler.tcl:234)
     * Tested by: FeatureControllerTest.shouldValidateConfiguration()
     */
    @PostMapping("/{id}/validate")
    @Operation(summary = "Validate feature configuration")
    public ResponseEntity<ValidationResult> validateConfiguration(
            @PathVariable Long id,
            @Valid @RequestBody ValidationRequest request) {
        log.info("POST /api/v1/features/{}/validate - Validating configuration", id);
        ValidationResult result = featureService.validateConfiguration(id, request);
        return ResponseEntity.ok(result);
    }
```

---

## Pattern 2: Create New Controller

When creating a new controller for a new resource:

```java
package ${base_package}.controller;

import ${base_package}.dto.${RequestDto};
import ${base_package}.dto.${ResponseDto};
import ${base_package}.service.${ServiceName};
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.util.List;

/**
 * Controller for ${resource_name} operations.
 * Implements: ${api_requirement_ids}
 * RNVS Source: ${rnvs_module_reference}
 *
 * @since ${version}
 */
@RestController
@RequestMapping("/api/v1/${resource_path}")
@RequiredArgsConstructor
@Slf4j
@Validated
@Tag(name = "${tag_name}", description = "${tag_description}")
public class ${ResourceName}Controller {

    private final ${ServiceName} ${serviceName};

    /**
     * Get all ${resource_plural}.
     * Tested by: ${ControllerTest}.shouldGetAll${Resource}()
     */
    @GetMapping
    @Operation(summary = "Get all ${resource_plural}")
    public ResponseEntity<List<${ResponseDto}>> getAll() {
        log.info("GET /api/v1/${resource_path} - Fetching all ${resource_plural}");
        List<${ResponseDto}> result = ${serviceName}.findAll();
        return ResponseEntity.ok(result);
    }

    /**
     * Get ${resource_name} by ID.
     * Tested by: ${ControllerTest}.shouldGet${Resource}ById()
     */
    @GetMapping("/{id}")
    @Operation(summary = "Get ${resource_name} by ID")
    public ResponseEntity<${ResponseDto}> getById(@PathVariable Long id) {
        log.info("GET /api/v1/${resource_path}/{} - Fetching ${resource_name}", id);
        return ${serviceName}.findById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Create new ${resource_name}.
     * Implements: ${create_business_rule}
     * Tested by: ${ControllerTest}.shouldCreate${Resource}()
     */
    @PostMapping
    @Operation(summary = "Create new ${resource_name}")
    public ResponseEntity<${ResponseDto}> create(
            @Valid @RequestBody ${RequestDto} request) {
        log.info("POST /api/v1/${resource_path} - Creating ${resource_name}");
        ${ResponseDto} result = ${serviceName}.create(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(result);
    }

    /**
     * Update ${resource_name}.
     * Implements: ${update_business_rule}
     * Tested by: ${ControllerTest}.shouldUpdate${Resource}()
     */
    @PutMapping("/{id}")
    @Operation(summary = "Update ${resource_name}")
    public ResponseEntity<${ResponseDto}> update(
            @PathVariable Long id,
            @Valid @RequestBody ${RequestDto} request) {
        log.info("PUT /api/v1/${resource_path}/{} - Updating ${resource_name}", id);
        return ${serviceName}.update(id, request)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Delete ${resource_name}.
     * Tested by: ${ControllerTest}.shouldDelete${Resource}()
     */
    @DeleteMapping("/{id}")
    @Operation(summary = "Delete ${resource_name}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void delete(@PathVariable Long id) {
        log.info("DELETE /api/v1/${resource_path}/{} - Deleting ${resource_name}", id);
        ${serviceName}.delete(id);
    }
}
```

---

## Pattern 3: Modify Existing Endpoint

When modifying an existing endpoint (e.g., adding query parameters):

```java
// MODIFICATION: Replace existing method

    /**
     * Get all ${resource_plural} with filtering.
     * MODIFIED: Added status and date filtering (BR-FEAT-010)
     * RNVS Source: ${rnvs_source}
     * Tested by: ${ControllerTest}.shouldFilterByStatus()
     */
    @GetMapping
    @Operation(summary = "Get all ${resource_plural} with optional filtering")
    public ResponseEntity<List<${ResponseDto}>> getAll(
            @RequestParam(required = false) String status,
            @RequestParam(required = false) @DateTimeFormat(iso = ISO.DATE) LocalDate fromDate,
            @RequestParam(required = false) @DateTimeFormat(iso = ISO.DATE) LocalDate toDate) {
        log.info("GET /api/v1/${resource_path} - Fetching with filters: status={}, from={}, to={}",
                status, fromDate, toDate);
        List<${ResponseDto}> result = ${serviceName}.findAll(status, fromDate, toDate);
        return ResponseEntity.ok(result);
    }
```

---

## Pattern 4: Add Validation Annotations

When adding validation to request parameters:

```java
// MODIFICATION: Add validation annotations to existing method

    @PostMapping
    public ResponseEntity<${ResponseDto}> create(
            @Valid @RequestBody ${RequestDto} request,  // Added @Valid
            @RequestHeader("X-Request-ID") @NotBlank String requestId) {  // Added @NotBlank
        // ...
    }
```

---

## Anti-Patterns to Avoid

1. **Don't duplicate endpoints**: Check if endpoint already exists before adding
2. **Don't forget logging**: Every endpoint should log its invocation
3. **Don't skip validation**: Use @Valid for request bodies, @NotNull/@NotBlank for path/query params
4. **Don't hardcode responses**: Use ResponseEntity for proper HTTP status codes
5. **Don't forget OpenAPI annotations**: @Operation, @Tag for API documentation
