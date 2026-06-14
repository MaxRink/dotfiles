# Knowledge Graph Navigator - Practical Examples

This file provides concrete usage patterns for MCP knowledge graph tools across different analysis phases.

## Phase 1: Initial Codebase Exploration

**Goal**: Understand overall structure of the RNVS codebase.

### Pattern: Repository Overview

```javascript
// Step 1: List indexed projects
list_projects()
// Returns: { projects: [{ project_path: "/path/to/rnvs-legacy" }] }

// Step 2: Generate repository map for overview
repo_map({
  project_absolute_path: "/path/to/rnvs-legacy",
  relative_paths: ["src"],
  depth: 1,
  show_definitions: true
})
// Returns: Directory tree + high-level definitions

// Step 3: Search for key business components
search_codebase_definitions({
  search_terms: ["PortingService", "RNBValidator", "NumberBlock"],
  project_absolute_path: "/path/to/rnvs-legacy"
})
// Returns: Locations of key classes across codebase

// Step 4: Read selected component implementations
read_definitions({
  definitions: [{
    names: ["PortingService"],
    file_path: "src/main/java/com/telco/porting/PortingService.java"
  }]
})
// Returns: Full source code of PortingService class
```

### Pattern: Understanding a Specific Feature

```javascript
// Search for number-portability related definitions
search_codebase_definitions({
  search_terms: [
    "NumberPorting", "porting", "Portierung",  // Various names
    "RNB", "allocation", "Zuteilung"            // Related terms
  ],
  project_absolute_path: "/rnvs-legacy"
})

// Read multiple related definitions efficiently
read_definitions({
  definitions: [
    {
      names: ["submitPortingRequest", "checkPortingStatus", "cancelPorting"],
      file_path: "src/services/PortingService.java"
    },
    {
      names: ["validateRNB", "checkRNBAvailability"],
      file_path: "src/validators/RNBValidator.java"
    }
  ]
})
```

---

## Phase 2: Dependency Mapping

**Goal**: Map all dependencies and call hierarchies for components.

### Pattern: Find All Callers of a Function

```javascript
// Step 1: Find where validatePortingRequest is defined
search_codebase_definitions({
  search_terms: ["validatePortingRequest"],
  project_absolute_path: "/rnvs-legacy"
})
// Returns: Found in PortingValidator.java:45

// Step 2: Find all callers
get_references({
  definition_name: "validatePortingRequest",
  file_path: "/rnvs-legacy/src/validators/PortingValidator.java",
  page: 1
})
// Returns: 8 call sites across 5 files with code context

// Step 3: For each caller, recursively find its callers (build call graph)
// Example: Found caller in PortingService.java:processRequest()
get_references({
  definition_name: "processRequest",
  file_path: "/rnvs-legacy/src/services/PortingService.java",
  page: 1
})
// Continue building call tree...
```

### Pattern: Map External Dependencies

```javascript
// Find Spring Framework usage
import_usage({
  project_absolute_path: "/rnvs-legacy",
  packages: [
    { import_path: "org.springframework.web.bind.annotation", name: "RestController" },
    { import_path: "org.springframework.stereotype", name: "Service" },
    { import_path: "org.springframework.data.jpa.repository" }
  ],
  page: 1,
  page_size: 100
})
// Returns: All Spring annotations usage across the codebase

// Find database dependencies
import_usage({
  project_absolute_path: "/rnvs-legacy",
  packages: [
    { import_path: "java.sql.Connection" },
    { import_path: "oracle.jdbc" }
  ]
})
// Returns: All JDBC/Oracle usage
```

---

## Phase 3: Business Rule Tracing

**Goal**: Trace how business rules are implemented across multiple files.

### Pattern: Extract Validation Rules

```javascript
// Step 1: Search for validation-related functions
search_codebase_definitions({
  search_terms: [
    "validate", "check", "verify",           // English patterns
    "pruefen", "validieren", "kontrollieren" // German patterns
  ],
  project_absolute_path: "/rnvs-legacy",
  page: 1
})

// Step 2: Read validation function implementations
read_definitions({
  definitions: [{
    names: [
      "checkONKZValidity",
      "validateRNBOwnership",
      "verifyPortingEligibility"
    ],
    file_path: "src/validators/BusinessRuleValidator.java"
  }]
})

// Step 3: Find where each rule is applied
get_references({
  definition_name: "checkONKZValidity",
  file_path: "/rnvs-legacy/src/validators/BusinessRuleValidator.java"
})
// Returns: All places where ONKZ validation is enforced

// Step 4: Map rule → use case → business objective
// Document each rule's implementation and usage context
```

---

## Phase 4: Business Logic Analysis

**Goal**: Understand how business logic flows through components.

### Pattern: Trace End-to-End Flow

```javascript
// Step 1: Find entry point (REST controller)
search_codebase_definitions({
  search_terms: ["PortingController"],
  project_absolute_path: "/rnvs-legacy"
})

// Step 2: Read controller methods
read_definitions({
  definitions: [{
    names: ["PortingController"],
    file_path: "src/controllers/PortingController.java"
  }]
})
// Identify methods: submitPortingRequest(), checkStatus()

// Step 3: Navigate to service layer from controller code
// From controller line: "return portingService.processRequest(dto);"
get_definition({
  file_path: "/rnvs-legacy/src/controllers/PortingController.java",
  line: "        return portingService.processRequest(dto);",
  symbol_name: "processRequest"
})
// Returns: Definition in PortingService.java:78-120

// Step 4: Read service implementation
read_definitions({
  definitions: [{
    names: ["processRequest"],
    file_path: "src/services/PortingService.java"
  }]
})

// Step 5: Continue tracing through validation layer, data layer, etc.
// Build complete execution flow diagram
```

---

## Phase 5: Control Flow Mapping

**Goal**: Map execution paths through the system for a business process.

### Pattern: Build Complete Call Chain

```javascript
// Step 1: Start with entry point
search_codebase_definitions({
  search_terms: ["submitPortingRequest"],
  project_absolute_path: "/rnvs-legacy"
})

// Step 2: Read entry point
read_definitions({
  definitions: [{
    names: ["submitPortingRequest"],
    file_path: "src/controllers/PortingController.java"
  }]
})
// Note all method calls in implementation

// Step 3: For each method call, navigate to definition
// Example from code: validator.validateRNB(block)
get_definition({
  file_path: "/rnvs-legacy/src/controllers/PortingController.java",
  line: "    if (!validator.validateRNB(block)) {",
  symbol_name: "validateRNB"
})

// Step 4: Recursively analyze called methods
read_definitions({
  definitions: [{
    names: ["validateRNB"],
    file_path: "src/validators/RNBValidator.java"
  }]
})

// Step 5: Map external integrations
import_usage({
  project_absolute_path: "/rnvs-legacy",
  packages: [
    { import_path: "oracle.jdbc" },          // Database calls
    { import_path: "org.apache.http.client" }, // REST client
    { import_path: "javax.jms" }              // Message queue
  ]
})

// Result: Complete RNVS → VNRM control flow mapping
```

---

## Advanced Patterns

### Pattern: Pagination for Large Result Sets

```javascript
// Initial search
let page = 1;
let hasMore = true;

while (hasMore) {
  const result = get_references({
    definition_name: "commonUtilityFunction",
    file_path: "/rnvs-legacy/src/utils/Common.java",
    page: page
  });

  // Process references
  // result.definitions.forEach(...)

  // Check for more pages
  hasMore = result.next_page !== null;
  page = result.next_page || page;
}
```

### Pattern: Efficient Batch Reading

```javascript
// GOOD: Group multiple definitions from same file
read_definitions({
  definitions: [
    {
      names: [
        "validateRNB",
        "checkRNBAvailability",
        "allocateRNB",
        "releaseRNB"
      ],
      file_path: "src/services/RNBService.java"
    },
    {
      names: [
        "validateONKZ",
        "checkONKZFormat"
      ],
      file_path: "src/validators/ONKZValidator.java"
    }
  ]
})
// Single call, optimized token usage
```

### Pattern: Hybrid MCP + Grep Approach

```javascript
// Step 1: Use MCP for structure
repo_map({
  project_absolute_path: "/rnvs-legacy",
  relative_paths: ["src/main/java/com/telco"],
  depth: 2
})
// Returns: Package structure and class overview

// Step 2: Use MCP to find definitions
search_codebase_definitions({
  search_terms: ["ErrorHandler"],
  project_absolute_path: "/rnvs-legacy"
})

// Step 3: Use Grep for string patterns MCP can't find
// Example: Find all error codes (string literals)
grep({
  pattern: "ERROR_[A-Z_]+",
  path: "src/main/java/com/telco",
  output_mode: "content"
})

// Step 4: Use Read for file-level context
read({
  file_path: "/rnvs-legacy/src/config/ErrorCodes.properties"
})
```

---

## Troubleshooting

### Problem: Definition Not Found

```javascript
// Try 1: Search with variations
search_codebase_definitions({
  search_terms: [
    "PortingService",      // Exact name
    "portingService",      // camelCase
    "PORTING_SERVICE",     // CONSTANT_CASE
    "Portierung"           // German variant
  ],
  project_absolute_path: "/rnvs-legacy"
})

// Try 2: Use repo_map to browse structure
repo_map({
  project_absolute_path: "/rnvs-legacy",
  relative_paths: ["src"],
  depth: 2,
  show_definitions: true
})

// Try 3: Fallback to Grep
grep({
  pattern: "class.*Porting.*Service",
  path: "src",
  output_mode: "files_with_matches"
})
```

### Problem: Stale Results

```javascript
// If results seem stale, inform the user that re-indexing may be needed
// User can manually trigger re-indexing if required

// Retry your query
search_codebase_definitions({
  search_terms: ["RecentlyAddedClass"],
  project_absolute_path: "/rnvs-legacy"
})

// If still not found, fallback to Grep
grep({
  pattern: "class.*RecentlyAddedClass",
  path: "src"
})
```

### Problem: Too Many Results

```javascript
// Strategy 1: Increase page_size
get_references({
  definition_name: "commonMethod",
  file_path: "/project/utils/Common.java",
  page: 1
})
// Check next_page field and paginate

// Strategy 2: Use more specific search terms
search_codebase_definitions({
  search_terms: ["PortingRequestValidator"], // More specific
  project_absolute_path: "/rnvs-legacy"
})
// Instead of: search_terms: ["validate"]  // Too broad
```

---

## Quick Reference: Tool Selection Guide

| Goal | MCP Tool | Alternative |
|------|----------|-------------|
| Find function definition | `search_codebase_definitions` | Grep pattern |
| Find all callers | `get_references` | Grep + manual |
| Navigate to definition | `get_definition` | Manual search |
| Read function body | `read_definitions` | Read file |
| Map dependencies | `import_usage` + `get_references` | Grep imports |
| Repository overview | `repo_map` | ls + Glob |
| Check indexed projects | `list_projects` | Manual path |

---

## Real-World Workflow Example

**Scenario**: Analyze number portability validation logic in Phase 3.

```javascript
// 1. Get project path
list_projects()
// → "/Users/dev/rnvs-legacy"

// 2. Overview of porting module
repo_map({
  project_absolute_path: "/Users/dev/rnvs-legacy",
  relative_paths: ["src/main/java/com/telco/porting"],
  depth: 2
})
// → See PortingValidator.java, RNBValidator.java, ONKZValidator.java

// 3. Find all validation functions
search_codebase_definitions({
  search_terms: [
    "validatePortingRequest",
    "validateRNB",
    "checkONKZValidity"
  ],
  project_absolute_path: "/Users/dev/rnvs-legacy"
})
// → Found 3 functions across 2 files

// 4. Read validation implementations
read_definitions({
  definitions: [{
    names: ["validatePortingRequest", "validateRNB"],
    file_path: "src/main/java/com/telco/porting/PortingValidator.java"
  }]
})
// → Extract business rules from code

// 5. Find where rules are applied
get_references({
  definition_name: "validatePortingRequest",
  file_path: "src/main/java/com/telco/porting/PortingValidator.java"
})
// → 12 call sites across 6 files

// 6. Trace one call site to understand context
get_definition({
  file_path: "src/main/java/com/telco/controllers/PortingController.java",
  line: "    validator.validatePortingRequest(request);",
  symbol_name: "validatePortingRequest"
})
// → Navigate back to validator definition

// Result: Complete validation rule mapping for Phase 3
```

---

**Refer back to [SKILL.md](SKILL.md) for tool reference and instructions.**
