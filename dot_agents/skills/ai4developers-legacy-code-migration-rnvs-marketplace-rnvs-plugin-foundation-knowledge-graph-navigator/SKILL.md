---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-foundation-knowledge-graph-navigator
description: Navigate codebases using MCP knowledge graph for code analysis, dependency mapping, and reference tracking. CRITICAL - GitLab Knowledge Graph supports ONLY Java, Ruby, Python, TypeScript, JavaScript, Kotlin. Does NOT support TCL, PL/SQL, C++, Shell. Use Grep for unsupported languages.
allowed-tools: Read, mcp__*
user-invocable: false
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/foundation/skills/knowledge-graph-navigator by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# Knowledge Graph Navigator Skill

## Purpose

Provides instructions for using MCP (Model Context Protocol) knowledge graph tools to efficiently navigate and analyze multi-language RNVS legacy codebases. The knowledge graph enables structured code exploration through definitions, references, and dependency mapping.

## MCP Knowledge Graph Tools

The MCP knowledge graph provides 7 tools for code navigation. Use these tools to understand code structure before resorting to Grep/Read.

### 1. `list_projects`

**Purpose**: Get list of all indexed projects to find the project root path.

**Input**: No parameters

**Output**:

- `projects`: Array of project objects with `project_path` (absolute path)

**Usage**:

```javascript
list_projects();
// Returns: { projects: [{ project_path: "/path/to/project" }] }
```

---

### 2. `search_codebase_definitions`

**Purpose**: Find functions, classes, methods, constants, interfaces by name across the codebase.

**Input**:

- `project_absolute_path` (string, required): Project root directory
- `search_terms` (string[], required): Array of definition names to search
- `page` (integer, optional, default: 1): Page number for pagination

**Output**:

- `definitions`: Array of matching definitions with:
  - `name`: Definition name
  - `fqn`: Fully qualified name
  - `definition_type`: Type (Function/Class/Method/Constant)
  - `location`: File path and line range (format: `file:LstartLine-endLine`)
  - `context`: Code snippet with signature
- `next_page`: Next page number if more results available
- `system_message`: Search results summary

**Usage**:

```javascript
search_codebase_definitions({
  search_terms: ["validatePortingRequest", "NumberBlock"],
  project_absolute_path: "/rnvs-legacy",
  page: 1,
});
```

---

### 3. `read_definitions`

**Purpose**: Read complete code bodies for multiple definitions. Optimizes token usage by batching definitions from same file.

**Input**:

- `definitions` (array, required): Array of objects with:
  - `names` (string[], required): Array of exact definition names
  - `file_path` (string, required): Absolute or project-relative path

**Output**:

- `definitions`: Array with:
  - `name`: Definition name
  - `fqn`: Fully qualified name
  - `definition_type`: Type of definition
  - `location`: File path and line range
  - `definition_body`: Full source code
- `system_message`: Status message

**Usage**:

```javascript
read_definitions({
  definitions: [
    {
      names: ["calculateTotal", "formatCurrency"],
      file_path: "src/utils/math.js",
    },
    {
      names: ["UserService"],
      file_path: "src/services/user.js",
    },
  ],
});
```

**Best practice**: Group multiple definitions from same file to save tokens.

---

### 4. `get_definition`

**Purpose**: Navigate from a usage/call site to its definition. Returns definition location or import statement if external.

**Input**:

- `file_path` (string, required): Absolute or project-relative path to file with usage
- `line` (string, required): Exact line of code (preserve whitespace)
- `symbol_name` (string, required): Callable symbol name (method/function)

**Output**:

- `definitions`: Array of definition objects (can be multiple if ambiguous):
  - `type`: "Definition" (workspace) or "ImportedSymbol" (external)
  - `name`: Symbol name
  - `fqn`: Fully qualified name
  - `primary_file_path`: Project-relative path
  - `absolute_file_path`: Absolute path
  - `start_line` / `end_line`: Line numbers
  - `code`: Code snippet
  - `is_ambiguous`: Boolean flag
- `system_message`: Status/disambiguation message

**Usage**:

```javascript
get_definition({
  file_path: "/project/src/porting/PortingService.java",
  line: "    var result = validator.validateRNB(block);",
  symbol_name: "validateRNB",
});
```

---

### 5. `get_references`

**Purpose**: Find all places where a function/class/constant is used across the codebase.

**Input**:

- `definition_name` (string, required): Exact symbol name (case-sensitive)
- `file_path` (string, required): Absolute or relative path where definition is declared
- `page` (integer, optional, default: 1): Page number for pagination

**Output**:

- `definitions`: Array of definitions that reference the target, each with:
  - `name`: Name of referencing definition
  - `location`: File path and line number
  - `definition_type`: Type (Method/Constructor/Class)
  - `fqn`: Fully qualified name
  - `references`: Array of specific reference instances:
    - `reference_type`: Type of reference (CALLS/PropertyReference)
    - `location`: File path and line number
    - `context`: Surrounding code lines
- `next_page`: Next page number if available
- `system_message`: Results summary

**Usage**:

```javascript
get_references({
  definition_name: "calculateTotal",
  file_path: "/project/src/utils/math.js",
  page: 1,
});
```

**Workflow**: Use with `search_codebase_definitions` first to locate definition, then find references.

---

### 6. `repo_map`

**Purpose**: Generate compact, API-style map of repository structure with definitions.

**Input**:

- `project_absolute_path` (string, required): Project root directory
- `relative_paths` (string[], required): Project-relative paths (files or directories)
- `show_directories` (boolean, optional, default: true): Include directory tree
- `show_definitions` (boolean, optional, default: true): Include files and definitions
- `depth` (integer, optional, default: 1, max: 3): Nesting depth for definitions
- `page` (integer, optional, default: 1): Page number
- `page_size` (integer, optional, default: 50, max: 200): Results per page

**Output**: XML string with:

- `<directories>`: ASCII directory tree
- `<files>`: Array of file entries with:
  - `<path>`: Project-relative file path
  - `<definitions>`: Definition list with line ranges and snippets
- `<system-message>`: Results summary

**Usage**:

```javascript
repo_map({
  project_absolute_path: "/project",
  relative_paths: ["src/main/java/com/telco"],
  show_definitions: true,
  depth: 2,
  page: 1,
});
```

**Best practice**: Start with depth=1 for large repos.

---

### 7. `import_usage` (Advanced)

**Purpose**: Analyze package/module import usages across the project.

**Input**:

- `project_absolute_path` (string, required): Project root
- `packages` (array, required): Array of import objects:
  - `import_path` (string, required): Import path
  - `name` (string, optional): Specific symbol name
  - `alias` (string, optional): Import alias
- `page` (integer, optional, default: 1): Page number
- `page_size` (integer, optional, default: 50, max: 200): Results per page

**Output**:

- Import locations and usage sites with code snippets

**Usage**:

```javascript
import_usage({
  project_absolute_path: "/project",
  packages: [
    {
      import_path: "org.springframework.web.bind.annotation",
      name: "RestController",
    },
    { import_path: "java.sql.Connection" },
  ],
});
```

---

## Instructions

### Basic Workflow

1. **Start with project path**:

   ```javascript
   list_projects(); // Get indexed project paths
   ```

2. **Find definitions**:

   ```javascript
   search_codebase_definitions({
     search_terms: ["MyClass", "myFunction"],
     project_absolute_path: "/project",
   });
   ```

3. **Read implementation**:

   ```javascript
   read_definitions({
     definitions: [
       {
         names: ["MyClass"],
         file_path: "src/MyClass.java",
       },
     ],
   });
   ```

4. **Find all usages**:
   ```javascript
   get_references({
     definition_name: "myFunction",
     file_path: "/project/src/MyClass.java",
   });
   ```

### Language Support (CRITICAL)

**GitLab Knowledge Graph MCP - Official Supported Languages**:

- **Java**: Classes, interfaces, methods, constants, enums
- **Ruby**: Classes, modules, methods, constants
- **Python**: Classes, functions, methods, variables (definitions, intra-file, partial cross-file)
- **TypeScript**: Classes, interfaces, functions, constants (definitions, intra-file, partial cross-file)
- **JavaScript**: Functions, classes, constants (definitions, intra-file, partial cross-file)
- **Kotlin**: Classes, interfaces, functions, properties (definitions, intra-file, cross-file references)

**NOT Supported (Use Grep for these languages)**:

- **TCL** - Use Grep with glob `*.tcl`
- **PL/SQL** - Use Grep with glob `*.sql`
- **C++** - Use Grep with glob `*.{cpp,hpp}`
- **Shell** - Use Grep with glob `*.sh`

**RNVS Codebase Impact**:

- Total files: 4,112
- Supported (68.5%): 2,817 Java files - Knowledge Graph WORKS
- **Unsupported (31.5%): 1,295 files - Knowledge Graph FAILS**
  - C++ (18%): 738 files
  - TCL (4.5%): 183 files
  - PL/SQL (4.2%): 174 files
  - Shell (3.2%): 133 files

**Critical Implication**: Most RNVS porting features (FNPORT, MFPORT, DNPORT, RNBPORT) are 90-100% TCL/PL/SQL. **Knowledge Graph cannot discover these features.**

**Solution**: Use Grep-based iterative discovery as primary tool for RNVS code analysis. See **domain-term-extractor** skill for regex patterns.

**Important**: Use exact case-sensitive names. Search terms must match symbol names as they appear in code.

### MCP vs Traditional Tools

**Use MCP knowledge graph for**:

- Finding all callers of a function
- Navigating from usage to definition
- Mapping call hierarchies and dependencies
- Structured navigation across large codebases
- Repository-wide overviews

**Use Grep/Read for**:

- Text patterns or regular expressions
- String literals or configuration values
- Code not indexed or MCP unavailable
- Context lines (lines before/after matches)
- Comments or documentation

### Pagination Strategy

1. **Start with default page_size (50)**
2. **Check `next_page` field in response**
3. **Increase page_size to 100-200 for comprehensive analysis** (max: 200)
4. **Follow pagination** when `next_page` is present

### Efficient Batching

**DO**: Group definitions from same file

```javascript
read_definitions({
  definitions: [
    {
      names: ["func1", "func2", "func3"], // Multiple from same file
      file_path: "src/services.js",
    },
  ],
});
```

**DON'T**: Make separate calls for each definition

```javascript
// Inefficient - wastes tokens
read_definitions({
  definitions: [{ names: ["func1"], file_path: "src/services.js" }],
});
read_definitions({
  definitions: [{ names: ["func2"], file_path: "src/services.js" }],
});
```

---

## Best Practices

1. **Project Discovery**:

   - Run `list_projects` at start to verify indexed projects
   - Know your project root path before using other tools

2. **Efficient Querying**:

   - Batch `read_definitions` from same file
   - Use specific function names, not wildcards
   - Start with `search_codebase_definitions` to find locations

3. **Error Handling**:

   - **Definition not found**: Fallback to Grep
   - **Too many results**: Use pagination
   - **External symbols**: Check `type: "ImportedSymbol"`
   - **Stale results**: Ask user to re-index if needed

4. **Hybrid Approach**:
   - Start with MCP for structure
   - Navigate with MCP tools
   - Fallback to Grep for patterns
   - Use Read for file-level context

---

## Usage in Commands

Commands dealing with code analysis should reference this skill:

```markdown
**Refer to the knowledge-graph-navigator skill** for using MCP tools to navigate the codebase.
```

---

## Progressive Disclosure

- **SKILL.md** (this file) - Tool reference and instructions
- **[examples.md](examples.md)** - Practical usage patterns and workflows

Load examples.md when you need to see concrete patterns for Phase 1-5 analysis workflows.

---

**For practical usage patterns, see [examples.md](examples.md)**
