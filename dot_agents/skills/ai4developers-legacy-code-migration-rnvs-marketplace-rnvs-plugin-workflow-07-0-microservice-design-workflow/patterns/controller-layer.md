# Controller Layer Patterns

Spring Boot REST controller patterns for VNRM microservices.

## Controller Template

```java
package com.telekom.vnrm.${submodule}.${service}.controller;

import com.telekom.vnrm.${submodule}.${service}.dto.${EntityName}CreateRequest;
import com.telekom.vnrm.${submodule}.${service}.dto.${EntityName}UpdateRequest;
import com.telekom.vnrm.${submodule}.${service}.dto.${EntityName}Response;
import com.telekom.vnrm.${submodule}.${service}.service.${EntityName}Service;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * REST Controller for ${EntityName} operations
 */
@RestController
@RequestMapping("/api/v1/${resource-path}")
@RequiredArgsConstructor
@Slf4j
@Tag(name = "${EntityName}", description = "${EntityName} management operations")
public class ${EntityName}Controller {

    private final ${EntityName}Service service;

    @PostMapping
    @Operation(summary = "Create ${EntityName}", description = "Creates a new ${EntityName}")
    @ApiResponses({
        @ApiResponse(responseCode = "201", description = "${EntityName} created successfully"),
        @ApiResponse(responseCode = "400", description = "Invalid request data"),
        @ApiResponse(responseCode = "409", description = "${EntityName} already exists"),
        @ApiResponse(responseCode = "500", description = "Internal server error")
    })
    public ResponseEntity<${EntityName}Response> create(
            @Valid @RequestBody ${EntityName}CreateRequest request) {
        log.info("POST /api/v1/${resource-path} - Creating ${EntityName}");
        ${EntityName}Response response = service.create(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    @GetMapping("/{id}")
    @Operation(summary = "Get ${EntityName} by ID", description = "Retrieves ${EntityName} by its ID")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "${EntityName} found"),
        @ApiResponse(responseCode = "404", description = "${EntityName} not found"),
        @ApiResponse(responseCode = "500", description = "Internal server error")
    })
    public ResponseEntity<${EntityName}Response> getById(
            @Parameter(description = "${EntityName} ID") @PathVariable Long id) {
        log.info("GET /api/v1/${resource-path}/{} - Getting ${EntityName}", id);
        return ResponseEntity.ok(service.getById(id));
    }

    @GetMapping
    @Operation(summary = "Get all ${EntityName}s", description = "Retrieves all ${EntityName}s with pagination")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "List of ${EntityName}s"),
        @ApiResponse(responseCode = "500", description = "Internal server error")
    })
    public ResponseEntity<Page<${EntityName}Response>> getAll(
            @Parameter(description = "Pagination parameters") Pageable pageable) {
        log.info("GET /api/v1/${resource-path} - Getting all ${EntityName}s");
        return ResponseEntity.ok(service.getAll(pageable));
    }

    @PutMapping("/{id}")
    @Operation(summary = "Update ${EntityName}", description = "Updates an existing ${EntityName}")
    @ApiResponses({
        @ApiResponse(responseCode = "200", description = "${EntityName} updated successfully"),
        @ApiResponse(responseCode = "400", description = "Invalid request data"),
        @ApiResponse(responseCode = "404", description = "${EntityName} not found"),
        @ApiResponse(responseCode = "409", description = "Conflict - version mismatch"),
        @ApiResponse(responseCode = "500", description = "Internal server error")
    })
    public ResponseEntity<${EntityName}Response> update(
            @Parameter(description = "${EntityName} ID") @PathVariable Long id,
            @Valid @RequestBody ${EntityName}UpdateRequest request) {
        log.info("PUT /api/v1/${resource-path}/{} - Updating ${EntityName}", id);
        return ResponseEntity.ok(service.update(id, request));
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "Delete ${EntityName}", description = "Deletes an existing ${EntityName}")
    @ApiResponses({
        @ApiResponse(responseCode = "204", description = "${EntityName} deleted successfully"),
        @ApiResponse(responseCode = "404", description = "${EntityName} not found"),
        @ApiResponse(responseCode = "500", description = "Internal server error")
    })
    public ResponseEntity<Void> delete(
            @Parameter(description = "${EntityName} ID") @PathVariable Long id) {
        log.info("DELETE /api/v1/${resource-path}/{} - Deleting ${EntityName}", id);
        service.delete(id);
        return ResponseEntity.noContent().build();
    }
}
```

## DTO Templates

### Create Request

```java
package com.telekom.vnrm.${submodule}.${service}.dto;

import jakarta.validation.constraints.*;
import lombok.*;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ${EntityName}CreateRequest {

    @NotBlank(message = "${fieldName} is required")
    @Size(max = ${maxLength}, message = "${fieldName} must not exceed ${maxLength} characters")
    private String ${fieldName};

    @NotNull(message = "${enumField} is required")
    private ${EnumType} ${enumField};

    @Email(message = "Invalid email format")
    private String email;

    @Pattern(regexp = "^\\+?[0-9]{10,15}$", message = "Invalid phone number format")
    private String phoneNumber;
}
```

### Update Request

```java
package com.telekom.vnrm.${submodule}.${service}.dto;

import jakarta.validation.constraints.*;
import lombok.*;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ${EntityName}UpdateRequest {

    @NotNull(message = "Version is required for optimistic locking")
    private Long version;

    @Size(max = ${maxLength}, message = "${fieldName} must not exceed ${maxLength} characters")
    private String ${fieldName};
}
```

### Response

```java
package com.telekom.vnrm.${submodule}.${service}.dto;

import lombok.*;
import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ${EntityName}Response {

    private Long id;
    private String ${fieldName};
    private String status;
    private Long version;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
```

## Error Response Pattern

```java
package com.telekom.vnrm.${submodule}.${service}.dto;

import lombok.*;
import java.time.LocalDateTime;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ErrorResponse {

    private LocalDateTime timestamp;
    private int status;
    private String error;
    private String message;
    private String path;
    private String traceId;
    private List<FieldError> fieldErrors;

    @Data
    @Builder
    public static class FieldError {
        private String field;
        private String message;
        private Object rejectedValue;
    }
}
```

## Exception Handler

```java
package com.telekom.vnrm.${submodule}.${service}.controller;

import com.telekom.vnrm.${submodule}.${service}.dto.ErrorResponse;
import com.telekom.vnrm.${submodule}.${service}.exception.*;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.*;

@RestControllerAdvice
@Slf4j
public class GlobalExceptionHandler {

    @ExceptionHandler(${EntityName}NotFoundException.class)
    public ResponseEntity<ErrorResponse> handleNotFound(${EntityName}NotFoundException ex) {
        log.warn("Entity not found: {}", ex.getMessage());
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
            .body(ErrorResponse.builder()
                .status(404)
                .error("Not Found")
                .message(ex.getMessage())
                .build());
    }

    @ExceptionHandler(BusinessRuleViolationException.class)
    public ResponseEntity<ErrorResponse> handleBusinessRule(BusinessRuleViolationException ex) {
        log.warn("Business rule violation: {} - {}", ex.getRuleId(), ex.getMessage());
        return ResponseEntity.status(HttpStatus.BAD_REQUEST)
            .body(ErrorResponse.builder()
                .status(400)
                .error("Business Rule Violation")
                .message(ex.getMessage())
                .build());
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleValidation(MethodArgumentNotValidException ex) {
        var fieldErrors = ex.getBindingResult().getFieldErrors().stream()
            .map(fe -> ErrorResponse.FieldError.builder()
                .field(fe.getField())
                .message(fe.getDefaultMessage())
                .rejectedValue(fe.getRejectedValue())
                .build())
            .toList();

        return ResponseEntity.status(HttpStatus.BAD_REQUEST)
            .body(ErrorResponse.builder()
                .status(400)
                .error("Validation Failed")
                .message("Request validation failed")
                .fieldErrors(fieldErrors)
                .build());
    }
}
```

## HTTP Status Codes Reference

| Code | Description | When to Use |
|------|-------------|-------------|
| 200 | OK | Successful GET, PUT |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Validation error, business rule violation |
| 401 | Unauthorized | Missing authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Duplicate, optimistic locking failure |
| 500 | Internal Server Error | Unexpected errors |

## Best Practices

1. **Use @Valid** for request validation
2. **Return appropriate HTTP status codes**
3. **Document with OpenAPI annotations**
4. **Log request entry points**
5. **Use ResponseEntity** for full control
6. **Implement global exception handling**
7. **Include pagination** for list endpoints
8. **Version APIs** in URL path (/api/v1/)
