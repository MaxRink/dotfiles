# DTO and Mapper Patterns

Patterns for DTOs and MapStruct mappers in VNRM microservices.

---

## Pattern 1: Request DTO

Standard request DTO with validation:

```java
package ${base_package}.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.*;
import lombok.*;

/**
 * Request DTO for creating/updating ${resource_name}.
 * Implements: ${business_rule}
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ${Resource}Request {

    /**
     * Name of the ${resource}.
     */
    @NotBlank(message = "Name is required")
    @Size(min = 1, max = 255, message = "Name must be between 1 and 255 characters")
    private String name;

    /**
     * Description of the ${resource}.
     */
    @Size(max = 2000, message = "Description cannot exceed 2000 characters")
    private String description;

    /**
     * External identifier (e.g., from legacy system).
     */
    @JsonProperty("external_id")
    @Pattern(regexp = "^[A-Z0-9-]+$", message = "External ID must be alphanumeric with dashes")
    private String externalId;

    /**
     * Initial status (optional, defaults to NEW).
     */
    @JsonProperty("initial_status")
    private String initialStatus;

    /**
     * Configuration key-value pairs.
     */
    private java.util.Map<String, Object> configuration;

    /**
     * Related entity ID (if applicable).
     */
    @JsonProperty("${parent}_id")
    @Positive(message = "${Parent} ID must be positive")
    private Long ${parent}Id;
}
```

---

## Pattern 2: Response DTO

Standard response DTO:

```java
package ${base_package}.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.*;

import java.time.Instant;

/**
 * Response DTO for ${resource_name}.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ${Resource}Response {

    /**
     * Unique identifier.
     */
    private Long id;

    /**
     * Name of the ${resource}.
     */
    private String name;

    /**
     * Description of the ${resource}.
     */
    private String description;

    /**
     * External identifier.
     */
    @JsonProperty("external_id")
    private String externalId;

    /**
     * Current status.
     */
    private String status;

    /**
     * Related entity.
     */
    @JsonProperty("${parent}")
    private ${Parent}Summary ${parent};

    /**
     * When the ${resource} was created.
     */
    @JsonProperty("created_at")
    private Instant createdAt;

    /**
     * When the ${resource} was last updated.
     */
    @JsonProperty("updated_at")
    private Instant updatedAt;

    /**
     * Who created the ${resource}.
     */
    @JsonProperty("created_by")
    private String createdBy;

    /**
     * Nested summary DTO for related entity.
     */
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class ${Parent}Summary {
        private Long id;
        private String name;
    }
}
```

---

## Pattern 3: Page Response DTO

For paginated responses:

```java
package ${base_package}.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.*;

import java.util.List;

/**
 * Paginated response wrapper.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class PageResponse<T> {

    /**
     * List of items in current page.
     */
    private List<T> content;

    /**
     * Current page number (0-based).
     */
    private int page;

    /**
     * Page size.
     */
    private int size;

    /**
     * Total number of items.
     */
    @JsonProperty("total_elements")
    private long totalElements;

    /**
     * Total number of pages.
     */
    @JsonProperty("total_pages")
    private int totalPages;

    /**
     * Whether this is the first page.
     */
    private boolean first;

    /**
     * Whether this is the last page.
     */
    private boolean last;

    /**
     * Create from Spring Page.
     */
    public static <T> PageResponse<T> from(org.springframework.data.domain.Page<T> page) {
        return PageResponse.<T>builder()
                .content(page.getContent())
                .page(page.getNumber())
                .size(page.getSize())
                .totalElements(page.getTotalElements())
                .totalPages(page.getTotalPages())
                .first(page.isFirst())
                .last(page.isLast())
                .build();
    }
}
```

---

## Pattern 4: MapStruct Mapper

Standard MapStruct mapper:

```java
package ${base_package}.mapper;

import ${base_package}.dto.${Resource}Request;
import ${base_package}.dto.${Resource}Response;
import ${base_package}.entity.${Resource};
import org.mapstruct.*;

import java.util.List;

/**
 * MapStruct mapper for ${Resource} entity.
 */
@Mapper(
    componentModel = "spring",
    nullValuePropertyMappingStrategy = NullValuePropertyMappingStrategy.IGNORE,
    unmappedTargetPolicy = ReportingPolicy.WARN
)
public interface ${Resource}Mapper {

    /**
     * Map entity to response DTO.
     */
    @Mapping(source = "status", target = "status", qualifiedByName = "statusToString")
    @Mapping(source = "${parent}", target = "${parent}", qualifiedByName = "to${Parent}Summary")
    ${Resource}Response toResponse(${Resource} entity);

    /**
     * Map list of entities to list of response DTOs.
     */
    List<${Resource}Response> toResponseList(List<${Resource}> entities);

    /**
     * Map request DTO to entity (for create).
     */
    @Mapping(target = "id", ignore = true)
    @Mapping(target = "createdAt", ignore = true)
    @Mapping(target = "updatedAt", ignore = true)
    @Mapping(target = "createdBy", ignore = true)
    @Mapping(target = "updatedBy", ignore = true)
    @Mapping(source = "initialStatus", target = "status", qualifiedByName = "stringToStatus")
    ${Resource} toEntity(${Resource}Request request);

    /**
     * Update entity from request DTO (for update).
     */
    @Mapping(target = "id", ignore = true)
    @Mapping(target = "createdAt", ignore = true)
    @Mapping(target = "createdBy", ignore = true)
    @Mapping(target = "status", ignore = true)  // Status changed via dedicated method
    void updateEntity(${Resource}Request request, @MappingTarget ${Resource} entity);

    /**
     * Convert status enum to string.
     */
    @Named("statusToString")
    default String statusToString(${Resource}Status status) {
        return status != null ? status.name() : null;
    }

    /**
     * Convert string to status enum.
     */
    @Named("stringToStatus")
    default ${Resource}Status stringToStatus(String status) {
        return status != null ? ${Resource}Status.valueOf(status) : ${Resource}Status.NEW;
    }

    /**
     * Map parent entity to summary DTO.
     */
    @Named("to${Parent}Summary")
    default ${Resource}Response.${Parent}Summary to${Parent}Summary(${Parent} parent) {
        if (parent == null) {
            return null;
        }
        return ${Resource}Response.${Parent}Summary.builder()
                .id(parent.getId())
                .name(parent.getName())
                .build();
    }
}
```

---

## Pattern 5: Mapper with Custom Methods

Mapper with complex transformations:

```java
package ${base_package}.mapper;

import ${base_package}.dto.*;
import ${base_package}.entity.*;
import org.mapstruct.*;
import org.springframework.beans.factory.annotation.Autowired;

import java.util.List;

/**
 * Advanced mapper with custom methods.
 */
@Mapper(
    componentModel = "spring",
    uses = {${Related}Mapper.class},
    injectionStrategy = InjectionStrategy.CONSTRUCTOR
)
public abstract class ${Resource}Mapper {

    @Autowired
    protected ${Related}Repository ${related}Repository;

    /**
     * Map entity to detailed response.
     */
    @Mapping(source = "${related}s", target = "${related}s", qualifiedByName = "toSummaryList")
    @Mapping(target = "computedField", expression = "java(computeField(entity))")
    public abstract ${Resource}DetailResponse toDetailResponse(${Resource} entity);

    /**
     * Map request to entity, resolving related entities.
     */
    @Mapping(target = "${related}s", ignore = true)
    @AfterMapping
    void resolve${Related}s(${Resource}Request request, @MappingTarget ${Resource} entity) {
        if (request.get${Related}Ids() != null) {
            List<${Related}> ${related}s = ${related}Repository
                    .findAllById(request.get${Related}Ids());
            entity.set${Related}s(${related}s);
        }
    }

    /**
     * Compute derived field.
     */
    protected String computeField(${Resource} entity) {
        // Custom computation logic
        return entity.getPrefix() + "-" + entity.getId();
    }

    /**
     * Map related entities to summary list.
     */
    @Named("toSummaryList")
    protected abstract List<${Related}Summary> toSummaryList(List<${Related}> entities);
}
```

---

## Pattern 6: Filter/Search Request DTO

For search/filter endpoints:

```java
package ${base_package}.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.*;
import lombok.*;
import org.springframework.format.annotation.DateTimeFormat;

import java.time.LocalDate;
import java.util.List;

/**
 * Filter criteria for searching ${resource_plural}.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ${Resource}Filter {

    /**
     * Filter by name (partial match).
     */
    @Size(max = 255)
    private String name;

    /**
     * Filter by status(es).
     */
    @JsonProperty("statuses")
    private List<String> statuses;

    /**
     * Filter by ${parent} ID.
     */
    @JsonProperty("${parent}_id")
    private Long ${parent}Id;

    /**
     * Created after this date.
     */
    @JsonProperty("created_after")
    @DateTimeFormat(iso = DateTimeFormat.ISO.DATE)
    private LocalDate createdAfter;

    /**
     * Created before this date.
     */
    @JsonProperty("created_before")
    @DateTimeFormat(iso = DateTimeFormat.ISO.DATE)
    private LocalDate createdBefore;

    /**
     * Include soft-deleted records.
     */
    @JsonProperty("include_deleted")
    @Builder.Default
    private Boolean includeDeleted = false;

    /**
     * Page number (0-based).
     */
    @Min(0)
    @Builder.Default
    private Integer page = 0;

    /**
     * Page size.
     */
    @Min(1)
    @Max(100)
    @Builder.Default
    private Integer size = 20;

    /**
     * Sort field.
     */
    @JsonProperty("sort_by")
    @Builder.Default
    private String sortBy = "createdAt";

    /**
     * Sort direction.
     */
    @JsonProperty("sort_direction")
    @Builder.Default
    private String sortDirection = "DESC";
}
```

---

## Anti-Patterns to Avoid

1. **Don't expose entities directly** - Always use DTOs for API responses
2. **Don't skip validation** - Add constraints to request DTOs
3. **Don't use primitive wrappers for required fields** - Use primitives where null is invalid
4. **Don't forget `@JsonProperty`** - Use for snake_case JSON field names
5. **Don't map everything** - Use summary DTOs for related entities
6. **Don't hardcode defaults in entity** - Set defaults in request DTO
