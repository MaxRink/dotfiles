# Output Schemas

## Output Files

- `results/${FEATURE}/phase1/file-inventory.json`
- `results/${FEATURE}/phase1/dependency-graph.json`

For formal JSON Schema definitions, see [references/](references/).

---

## file-inventory.json

### Required Evidence Fields (NEW)

The following fields are **MANDATORY** to prevent hallucination:

| Field | Type | Purpose |
|-------|------|---------|
| `content_read` | boolean | Proves file was actually read |
| `read_method` | string | Documents HOW file was read |
| `read_chunks` | array | For chunked reads, lists ranges |
| `keyword_matches[].sample_lines` | array | Proves keywords found in content |
| `dependencies[].source_line` | integer | Proves dependency found in code |
| `dependencies[].pattern_found` | string | Shows actual code pattern |
| `scoring_breakdown.keyword_density_reason` | string | Explains score calculation |

### Complete Schema

```json
{
  "feature": "RFNR-ERR",
  "timestamp": "2026-01-14T14:30:00Z",

  "discovery_method": {
    "module_references_available": true,
    "module_folders_used": ["/modules/rnb", "/modules/error"],
    "keyword_search_performed": true,
    "keywords_used": ["RFM", "VFM", "format_plausi", "fc_fcode", "errorhandler"],
    "dependency_extraction_depth": 2
  },

  "summary": {
    "total_files_discovered": 63,
    "high_relevance_files": 28,
    "medium_relevance_files": 22,
    "low_relevance_files": 13,
    "dependency_discovered_files": 8,
    "excluded_files": 3,
    "files_fully_read": 28,
    "files_partially_read": 22,
    "files_grep_verified": 13
  },

  "files": [
    {
      "file_path": "script/plsql/pack_body_rfnr.sql",
      "language": "PL/SQL",
      "file_type": "Package Body",
      "relevance_score": 95,
      "classification": "high",

      "content_read": true,
      "read_method": "chunked",
      "read_chunks": [[1, 1000], [1001, 2000], [2001, 3000], [3001, 4000]],
      "lines_read": 4000,

      "discovery_method": "keyword_search",

      "keyword_matches": [
        {
          "keyword": "RFM",
          "occurrences": 47,
          "sample_lines": [123, 456, 789, 1234, 2345]
        },
        {
          "keyword": "format_plausi",
          "occurrences": 12,
          "sample_lines": [234, 567, 890]
        },
        {
          "keyword": "fc_fcode",
          "occurrences": 89,
          "sample_lines": [100, 200, 300, 400, 500]
        }
      ],

      "scoring_breakdown": {
        "module_reference": 0,
        "component_match": 25,
        "keyword_density": 25,
        "keyword_density_reason": "148 total matches (47+12+89) across 5 keywords = avg 29.6, max score",
        "language_priority": 10,
        "exclusion_penalty": 0,
        "dependency_indicator": 10
      },

      "dependencies": [
        {
          "target": "pack_body_val",
          "source_line": 234,
          "pattern_found": "p_val.format_plausi_a(l_rfnr, pm_fc_fcode)"
        },
        {
          "target": "pack_body_pm",
          "source_line": 567,
          "pattern_found": "p_pm.p_anlegen_pm(l_pm_id, l_fc_fcode)"
        },
        {
          "target": "pack_rnps",
          "source_line": 890,
          "pattern_found": "p_rnps.get_error_code(l_fc_fcode)"
        }
      ],

      "line_count": 9827,
      "reason": "Core PL/SQL package for RFNR processing. Contains 148 keyword matches across error-related terms. Calls validation, problem message, and RNPS packages."
    },
    {
      "file_path": "script/plsql/pack_body_val.sql",
      "language": "PL/SQL",
      "file_type": "Package Body",
      "relevance_score": 88,
      "classification": "high",

      "content_read": true,
      "read_method": "chunked",
      "read_chunks": [[1, 1000], [1001, 2000], [2001, 3000]],
      "lines_read": 3000,

      "discovery_method": "dependency",

      "keyword_matches": [
        {
          "keyword": "VFM",
          "occurrences": 34,
          "sample_lines": [145, 267, 389, 512]
        },
        {
          "keyword": "format_plausi",
          "occurrences": 28,
          "sample_lines": [100, 200, 300, 400]
        }
      ],

      "scoring_breakdown": {
        "module_reference": 0,
        "component_match": 20,
        "keyword_density": 22,
        "keyword_density_reason": "62 matches (34+28) across 5 keywords = avg 12.4",
        "language_priority": 10,
        "exclusion_penalty": 0,
        "dependency_indicator": 8
      },

      "dependencies": [
        {
          "target": "pack_strukt",
          "source_line": 456,
          "pattern_found": "p_strukt.validate_structure(l_data)"
        }
      ],

      "line_count": 7635,
      "reason": "Validation package. Discovered as dependency of pack_body_rfnr. Contains VFM error codes and format_plausi procedures."
    },
    {
      "file_path": "script/tcl/rnb_utils.tcl",
      "language": "TCL",
      "file_type": "Utility Library",
      "relevance_score": 45,
      "classification": "medium",

      "content_read": true,
      "read_method": "partial",
      "lines_read": 500,
      "keyword_context_lines": [[78, 128], [234, 284]],

      "discovery_method": "keyword_search",

      "keyword_matches": [
        {
          "keyword": "RFM",
          "occurrences": 5,
          "sample_lines": [89, 103, 245]
        }
      ],

      "scoring_breakdown": {
        "module_reference": 0,
        "component_match": 10,
        "keyword_density": 8,
        "keyword_density_reason": "5 matches for 5 keywords = avg 1.0",
        "language_priority": 5,
        "exclusion_penalty": 0,
        "dependency_indicator": 0
      },

      "dependencies": [
        {
          "target": "common_utils.tcl",
          "source_line": 12,
          "pattern_found": "source ../lib/common_utils.tcl"
        }
      ],

      "line_count": 187,
      "reason": "TCL utility library with helper functions. Contains some RFM-related formatting."
    },
    {
      "file_path": "rnvs/entw/module/fehler/src/rnvserror.cpp",
      "language": "C++",
      "file_type": "Error Class",
      "relevance_score": 25,
      "classification": "low",

      "content_read": false,
      "read_method": "grep_context",
      "verification_note": "Keyword 'RFM' found at line 45 via grep, 20-line context verified",

      "discovery_method": "keyword_search",

      "keyword_matches": [
        {
          "keyword": "RFM",
          "occurrences": 2,
          "sample_lines": [45, 67]
        }
      ],

      "scoring_breakdown": {
        "module_reference": 0,
        "component_match": 5,
        "keyword_density": 3,
        "keyword_density_reason": "2 matches for 5 keywords = avg 0.4",
        "language_priority": 8,
        "exclusion_penalty": 0,
        "dependency_indicator": 0
      },

      "dependencies": [],

      "line_count": 150,
      "reason": "C++ error class. Low relevance - only 2 keyword matches, peripheral to core error logic."
    }
  ],

  "excluded_files": [
    {
      "file_path": "script/plsql/pack_body_fusion.sql",
      "reason": "Matches excluded_scope: 'fusion operations'",
      "keyword_matches": ["RFM", "fusion"],
      "would_be_score": 45
    }
  ],

  "unresolved_dependencies": [
    {
      "dependency_name": "external_bnetz_gateway",
      "referenced_by": ["pack_body_rfnr.sql"],
      "reason": "External system integration - BNetzA Gateway not in RNVS codebase"
    }
  ]
}
```

---

## dependency-graph.json

```json
{
  "feature": "RFNR-ERR",
  "timestamp": "2026-01-14T14:30:00Z",

  "nodes": [
    {
      "id": "pack_body_rfnr.sql",
      "type": "PL/SQL Package Body",
      "relevance": "high",
      "is_entry_point": true,
      "file_path": "script/plsql/pack_body_rfnr.sql",
      "content_read": true
    },
    {
      "id": "pack_body_val.sql",
      "type": "PL/SQL Package Body",
      "relevance": "high",
      "is_entry_point": false,
      "file_path": "script/plsql/pack_body_val.sql",
      "content_read": true
    },
    {
      "id": "pack_body_pm.sql",
      "type": "PL/SQL Package Body",
      "relevance": "high",
      "is_entry_point": false,
      "file_path": "script/plsql/pack_body_pm.sql",
      "content_read": true
    }
  ],

  "edges": [
    {
      "from": "pack_body_rfnr.sql",
      "to": "pack_body_val.sql",
      "relationship": "calls_procedure",
      "details": "Calls p_val.format_plausi_a() for validation",
      "source_line": 234,
      "pattern_found": "p_val.format_plausi_a(l_rfnr, pm_fc_fcode)"
    },
    {
      "from": "pack_body_rfnr.sql",
      "to": "pack_body_pm.sql",
      "relationship": "calls_procedure",
      "details": "Calls p_pm.p_anlegen_pm() for problem message creation",
      "source_line": 567,
      "pattern_found": "p_pm.p_anlegen_pm(l_pm_id, l_fc_fcode)"
    }
  ],

  "external_dependencies": [
    {
      "name": "BNetzA Gateway",
      "type": "External System",
      "referenced_by": ["pack_body_rfnr.sql"],
      "integration_type": "KCODE message exchange"
    }
  ],

  "dependency_closure": {
    "is_complete": true,
    "unresolved_internal_count": 0,
    "coverage_percentage": 100,
    "validation_message": "All internal dependencies resolved with source line evidence"
  }
}
```

---

## Schema Field Reference

### content_read (REQUIRED)

```json
"content_read": {
  "type": "boolean",
  "required": true,
  "description": "Was file content actually read (not just found via grep)?",
  "validation": "MUST be true for files with relevance_score >= 70"
}
```

### read_method (REQUIRED)

```json
"read_method": {
  "type": "string",
  "required": true,
  "enum": ["full", "chunked", "partial", "grep_context", "agent_delegated", "rlm_delegated"],
  "description": "How was the file read?",
  "definitions": {
    "full": "Entire file read with Read tool",
    "chunked": "File read in multiple chunks",
    "partial": "First N lines read + keyword context",
    "grep_context": "Grep with context lines only",
    "agent_delegated": "Read by multi-language-code-analyzer agent",
    "rlm_delegated": "Read via RLM skill with file:line attribution"
  }
}
```

### read_chunks (REQUIRED for chunked)

```json
"read_chunks": {
  "type": "array",
  "items": {
    "type": "array",
    "items": { "type": "integer" },
    "minItems": 2,
    "maxItems": 2
  },
  "description": "For chunked reads, list of [start_line, end_line] ranges",
  "example": [[1, 1000], [1001, 2000], [2001, 3000]]
}
```

### keyword_matches[].sample_lines (REQUIRED)

```json
"sample_lines": {
  "type": "array",
  "items": { "type": "integer" },
  "minItems": 1,
  "required": true,
  "description": "Line numbers where keyword was found (EVIDENCE)",
  "validation": "Must contain at least one line number proving the match"
}
```

### dependencies[].source_line (REQUIRED)

```json
"source_line": {
  "type": "integer",
  "required": true,
  "description": "Line number where dependency was found (EVIDENCE)",
  "validation": "Must be actual line number from reading the file"
}
```

### dependencies[].pattern_found (REQUIRED)

```json
"pattern_found": {
  "type": "string",
  "required": true,
  "description": "Actual code pattern found in file (EVIDENCE)",
  "example": "p_val.format_plausi_a(l_rfnr, pm_fc_fcode)",
  "validation": "Must be verbatim code from the file"
}
```

### scoring_breakdown.keyword_density_reason (REQUIRED)

```json
"keyword_density_reason": {
  "type": "string",
  "required": true,
  "description": "Explanation of how keyword_density score was calculated",
  "example": "47 RFM + 12 format_plausi = 59 matches for 5 keywords, avg 11.8"
}
```

---

## Validation Rules

Before accepting file-inventory.json as valid:

1. **All files with `relevance_score >= 70`** MUST have `content_read: true`
2. **All `keyword_matches` entries** MUST have non-empty `sample_lines` array
3. **All `dependencies` entries** MUST have `source_line` and `pattern_found`
4. **All `scoring_breakdown` objects** MUST have `keyword_density_reason`
5. **`read_method` must match evidence:**
   - If `full`: `lines_read` should equal `line_count`
   - If `chunked`: `read_chunks` must be present
   - If `partial`: `keyword_context_lines` should be present
