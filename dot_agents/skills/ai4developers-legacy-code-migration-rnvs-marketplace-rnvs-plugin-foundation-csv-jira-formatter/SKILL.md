---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-foundation-csv-jira-formatter
description: Format user stories and test cases as Jira-compatible CSV for direct import with proper escaping and column structure. This skill should be used in Phase 9 when generating Jira stories and test cases from gap analysis and business requirements.
allowed-tools: Read, Write
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/foundation/skills/csv-jira-formatter by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# CSV Jira Formatter Skill

## Purpose
Generate CSV files formatted for direct import into Jira, with proper column structure, field escaping, and German character encoding (UTF-8) for RNVS/VNRM project management.

## When to Use
- **Phase 9**: Converting user stories and test cases to Jira CSV export
- Bulk importing stories and tests to Jira
- Creating test coverage matrices for Phase 10

## Quick Reference

### CSV Structure
**Stories**: `Issue Type, Summary, Priority, Epic Link, Description, Labels, Affect Version, Acceptance Criteria, Business Scope`

**Tests**: `Issue Type, Summary, Priority, Epic Link, Description, Labels, Affect Version, Test Steps, Expected Result, Story Link`

### Key Escaping Rules
1. **Commas**: Wrap field in quotes → `"As a user, I want..."`
2. **Newlines**: Use `\n` → `"Step 1\nStep 2"`
3. **Quotes**: Double them → `"He said ""Hello"""`
4. **German characters**: UTF-8 encoding → `"Überprüfung"`

**See [REFERENCE.md](REFERENCE.md) for complete field specifications and escaping rules.**

## Instructions

### 1. Generate Stories CSV

Use `format_story_csv()` to convert stories to Jira-compatible CSV:

```python
stories = [
    {
        "summary": "Implement validation service",
        "priority": "High",
        "description": "As a validation service, I want to...",
        "labels": ["vnrm-validation-service", "phase-12"],
        "acceptance_criteria": "Given...\nWhen...\nThen...",
        "business_scope": "UC-PDA-001"
    }
]

csv_output = format_story_csv(stories, "PDA-Import", "VNRM-1.0")
```

### 2. Generate Test Cases CSV

Use `format_testcase_csv()` to convert tests to Jira-compatible CSV:

```python
testcases = [
    {
        "summary": "Validate 10-digit Rufnummer",
        "priority": "High",
        "description": "Positive test for valid format",
        "labels": ["unit-test", "vnrm-validation-service"],
        "test_steps": "1. Call API\n2. Verify response",
        "expected_result": "Status 200, validation passes",
        "story_link": "STORY-001"
    }
]

csv_output = format_testcase_csv(testcases, "PDA-Import", "VNRM-1.0")
```

### 3. Validate Before Saving

Always validate CSV before writing to file:

```python
validation = validate_csv(csv_output)
if validation["valid"]:
    write_file("phase9/jira_stories.csv", csv_output)
else:
    print(f"Errors: {validation['errors']}")
```

## Progressive Disclosure

- **SKILL.md** (this file) - Overview and basic usage
- **[REFERENCE.md](REFERENCE.md)** - Complete field specifications, escaping rules, API reference, Jira import procedure
- **[examples.md](examples.md)** - Real Phase 9 scenarios with complete story/test examples

Load REFERENCE.md when needing detailed field specifications or Jira import steps.
Load examples.md when needing to see complete Phase 9 workflows.

## Best Practices

1. **Keep summaries concise**: Max 255 chars, ideally < 100
2. **Use standard user story format**: "As a [role], I want to [action], so that [benefit]"
3. **Use Given/When/Then** for acceptance criteria
4. **Number test steps**: Always use "1. Step\n2. Step" format
5. **Link tests to stories**: Always provide story_link
6. **UTF-8 encoding**: Save CSV files with UTF-8 for German characters
7. **Validate before saving**: Always run `validate_csv()` before writing files
8. **Import stories first**: Import stories before tests (so story IDs exist for linking)

---

**For complete specifications and Jira import procedure, see [REFERENCE.md](REFERENCE.md)**
