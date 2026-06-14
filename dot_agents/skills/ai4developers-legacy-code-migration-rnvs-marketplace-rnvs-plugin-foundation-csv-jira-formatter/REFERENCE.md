# CSV Jira Formatter - Complete Reference

This document provides complete field specifications, escaping rules, validation rules, and Jira import procedures for the CSV Jira Formatter skill.

## Complete Field Specifications

### Story Fields

| Field | Required | Type | Max Length | Description |
|-------|----------|------|------------|-------------|
| Issue Type | Yes | Enum | - | Always "Story" |
| Summary | Yes | String | 255 chars | Story title |
| Priority | Yes | Enum | - | Critical / High / Medium / Low |
| Epic Link | Yes | String | 255 chars | Epic ID or name |
| Description | Yes | Text | 32,767 chars | User story in standard format |
| Labels | No | CSV List | - | Comma-separated tags |
| Affect Version | Yes | String | 64 chars | Version number (e.g., "VNRM-1.0") |
| Acceptance Criteria | Yes | Text | 32,767 chars | Testable conditions (Given/When/Then format) |
| Business Scope | Yes | String | 255 chars | Business Use Case reference (e.g., "UC-PDA-001") |

### Test Case Fields

| Field | Required | Type | Max Length | Description |
|-------|----------|------|------------|-------------|
| Issue Type | Yes | Enum | - | Always "Test" |
| Summary | Yes | String | 255 chars | Test scenario name |
| Priority | Yes | Enum | - | High / Medium / Low |
| Epic Link | Yes | String | 255 chars | Epic ID or name |
| Description | Yes | Text | 32,767 chars | Test overview |
| Labels | No | CSV List | - | Test type tags (unit-test, integration-test, etc.) |
| Affect Version | Yes | String | 64 chars | Version number |
| Test Steps | Yes | Text | 32,767 chars | Numbered steps (newline-separated) |
| Expected Result | Yes | Text | 32,767 chars | Pass criteria and expected outcome |
| Story Link | Yes | String | 255 chars | Parent story reference |

## Priority Values

### Valid Priority Values
- **Critical** - System-breaking issues, must be addressed immediately
- **High** - Important features or significant bugs
- **Medium** - Standard features or bugs
- **Low** - Nice-to-have features or minor bugs

### Priority Guidelines for Stories
- **Critical**: Core system functionality (authentication, data integrity, regulatory compliance)
- **High**: Important features that block other work or affect many users
- **Medium**: Standard feature development
- **Low**: UI polish, minor improvements

### Priority Guidelines for Tests
- **High**: Tests for critical paths, security, data integrity
- **Medium**: Tests for standard functionality
- **Low**: Edge case tests, UI tests

## Complete Escaping Rules

### 1. Comma Escaping

Fields containing commas MUST be wrapped in double quotes:

```csv
# Without commas (no quotes needed)
Story,Implement validation service,High,PDA-Import

# With commas (quotes required)
Story,"As a user, I want to validate numbers, so that errors are prevented",High,PDA-Import
```

### 2. Newline Escaping

Multi-line fields use `\n` for newlines and MUST be wrapped in quotes:

```csv
# Single line (no quotes needed)
Test,Validate 10-digit number,High,PDA-Import

# Multiple lines (quotes + \n required)
Test,"Test Steps:\n1. Call API\n2. Verify response\n3. Check logs",High,PDA-Import
```

### 3. Quote Escaping

Internal quotes are escaped by doubling them:

```csv
# No internal quotes
Story,Implement service,High,PDA-Import

# With internal quotes (double them)
Story,"He said ""Hello"" to me",High,PDA-Import
Story,"The ""validation"" service checks input",High,PDA-Import
```

### 4. Special Character Handling

#### German Characters (UTF-8)
No escaping needed, save file as UTF-8:
```csv
Story,"Rufnummernportierung durchführen",High,PDA-Import
Story,"Überprüfung der Gültigkeit",High,PDA-Import
```

#### Pipe Characters
No escaping needed:
```csv
Story,"Format: XXX|YYY|ZZZ",High,PDA-Import
```

#### Backslashes
Use double backslash if literal backslash needed:
```csv
Story,"File path: C:\\Users\\data",High,PDA-Import
```

## CSV Format Templates

### Stories CSV Template

```csv
Issue Type,Summary,Priority,Epic Link,Description,Labels,Affect Version,Acceptance Criteria,Business Scope
Story,"[Story Title]","[Priority]","[Epic ID]","As a [role], I want to [action], so that [benefit]","[label1, label2]","[Version]","Given [context]\nWhen [action]\nThen [outcome]","[UC-XXX]"
```

### Test Cases CSV Template

```csv
Issue Type,Summary,Priority,Epic Link,Description,Labels,Affect Version,Test Steps,Expected Result,Story Link
Test,"[Test Scenario Name]","[Priority]","[Epic ID]","[Test Description]","[test-type, component]","[Version]","1. [Step one]\n2. [Step two]\n3. [Step three]","[Expected outcome]","[STORY-XXX]"
```

## Validation Rules

### Error-Level Validations (MUST Fix)

1. **Missing Required Fields**
   - Error: "Missing required field: {field_name}"
   - Fix: Add the missing field value

2. **Invalid Priority Value**
   - Error: "Invalid priority: {value}. Must be Critical/High/Medium/Low"
   - Fix: Use one of the valid priority values

3. **Invalid Issue Type**
   - Error: "Invalid issue type: {value}. Must be Story or Test"
   - Fix: Use "Story" or "Test"

4. **Malformed CSV Structure**
   - Error: "Unmatched quotes on line {N}"
   - Fix: Ensure all quotes are properly closed and escaped

5. **Invalid Character Encoding**
   - Error: "File is not UTF-8 encoded"
   - Fix: Save file with UTF-8 encoding

6. **Summary Too Long**
   - Error: "Summary exceeds 255 characters: {length} chars"
   - Fix: Shorten summary to max 255 characters

### Warning-Level Validations (Should Review)

1. **Summary Near Limit**
   - Warning: "Summary is {length} chars (recommend < 100)"
   - Recommendation: Consider shortening for readability

2. **Description Too Long**
   - Warning: "Description exceeds 10,000 characters"
   - Recommendation: Split into multiple stories or trim content

3. **Too Many Labels**
   - Warning: "Story has {N} labels (recommend ≤ 10)"
   - Recommendation: Remove redundant labels

4. **Empty Acceptance Criteria**
   - Warning: "No acceptance criteria provided"
   - Recommendation: Add Given/When/Then criteria

5. **Test Missing Story Link**
   - Warning: "Test case has no story link"
   - Recommendation: Link test to parent story

6. **Vague Priority**
   - Warning: "Critical priority without justification in description"
   - Recommendation: Document why this is critical

## API Function Reference

### format_story_csv(stories, epic_link, version)

Formats user stories as Jira-compatible CSV.

**Parameters**:
- `stories` (List[Dict]): List of story objects
- `epic_link` (str): Epic identifier (e.g., "PDA-Import" or "EPIC-123")
- `version` (str): Affect version (e.g., "VNRM-1.0")

**Story Object Structure**:
```python
{
    "summary": str,           # Required, max 255 chars
    "priority": str,          # Required: Critical/High/Medium/Low
    "description": str,       # Required, user story format
    "labels": List[str],      # Optional, list of tags
    "acceptance_criteria": str,  # Required, Given/When/Then format
    "business_scope": str     # Required, UC reference
}
```

**Returns**: `str` - CSV-formatted string ready for Jira import

**Example**:
```python
stories = [
    {
        "summary": "Implement validation service API",
        "priority": "High",
        "description": "As a validation service, I want to expose REST API endpoints, so that clients can validate Rufnummern.",
        "labels": ["vnrm-validation-service", "api", "phase-12"],
        "acceptance_criteria": "Given a valid API request\nWhen validation endpoint is called\nThen response returns validation result",
        "business_scope": "UC-PDA-001: Rufnummernportierung"
    }
]

csv_output = format_story_csv(stories, "PDA-Import", "VNRM-1.0")
```

### format_testcase_csv(testcases, epic_link, version)

Formats test cases as Jira-compatible CSV.

**Parameters**:
- `testcases` (List[Dict]): List of test objects
- `epic_link` (str): Epic identifier
- `version` (str): Affect version

**Test Object Structure**:
```python
{
    "summary": str,           # Required, max 255 chars
    "priority": str,          # Required: High/Medium/Low
    "description": str,       # Required, test overview
    "labels": List[str],      # Optional, test type tags
    "test_steps": str,        # Required, numbered steps with \n
    "expected_result": str,   # Required, pass criteria
    "story_link": str         # Required, parent story ID
}
```

**Returns**: `str` - CSV-formatted string ready for Jira import

**Example**:
```python
testcases = [
    {
        "summary": "Validate 10-digit Rufnummer passes",
        "priority": "High",
        "description": "Positive test for valid 10-digit Rufnummer format",
        "labels": ["unit-test", "vnrm-validation-service"],
        "test_steps": "1. Call POST /api/v1/validate/rufnummer\n2. Body: {\"rufnummer\": \"0301234567\"}\n3. Verify response status and body",
        "expected_result": "Status: 200 OK\nResponse: {\"result\": \"PASS\", \"valid\": true}",
        "story_link": "STORY-001"
    }
]

csv_output = format_testcase_csv(testcases, "PDA-Import", "VNRM-1.0")
```

### escape_field(value)

Escapes a single field value for CSV format.

**Parameters**:
- `value` (str): String value to escape

**Returns**: `str` - Escaped string with quotes if needed

**Rules Applied**:
1. If value contains comma, newline, or quote → wrap in quotes
2. If value contains quotes → double them
3. If value contains no special chars → return as-is

**Example**:
```python
escape_field("Simple text")              # → Simple text
escape_field("Text with, comma")         # → "Text with, comma"
escape_field("He said \"Hello\"")        # → "He said ""Hello"""
escape_field("Line1\nLine2")            # → "Line1\nLine2"
```

### validate_csv(csv_string)

Validates CSV structure and content quality.

**Parameters**:
- `csv_string` (str): Complete CSV content to validate

**Returns**: `Dict` with structure:
```python
{
    "valid": bool,           # True if no errors
    "errors": List[str],     # Critical issues (must fix)
    "warnings": List[str]    # Quality issues (should review)
}
```

**Example**:
```python
csv_content = format_story_csv(stories, "EPIC-123", "V1.0")
result = validate_csv(csv_content)

if result["valid"]:
    print("✓ CSV is valid")
    if result["warnings"]:
        print(f"Warnings: {len(result['warnings'])}")
else:
    print(f"✗ Errors found: {len(result['errors'])}")
    for error in result["errors"]:
        print(f"  - {error}")
```

## Jira Import Procedure

### Step 1: Prepare CSV File

1. Generate CSV using `format_story_csv()` or `format_testcase_csv()`
2. Validate using `validate_csv()`
3. Save file with UTF-8 encoding
4. Name file descriptively (e.g., `phase9_pda_import_stories.csv`)

### Step 2: Access Jira Import

1. Log into Jira
2. Navigate to: **System → External System Import → CSV**
3. Or direct URL: `https://your-jira.com/secure/admin/ExternalImport1.jspa`

### Step 3: Configure Import Settings

1. **Upload File**: Select your CSV file
2. **Encoding**: UTF-8
3. **Separator**: Comma
4. **Quote Character**: Double quote (")
5. **Email Notifications**: Off (recommended for bulk imports)
6. **Create New Issues**: Yes
7. **Issue Type**: Map to Story or Test

### Step 4: Map CSV Columns to Jira Fields

Map each CSV column header to corresponding Jira field:

| CSV Column | Jira Field | Notes |
|------------|------------|-------|
| Issue Type | Issue Type | Map to Story/Test issue types |
| Summary | Summary | Standard field |
| Priority | Priority | Must match Jira priority names |
| Epic Link | Epic Link | Custom field (may vary) |
| Description | Description | Standard field |
| Labels | Labels | Standard field |
| Affect Version | Affects Version/s | Version field |
| Acceptance Criteria | Acceptance Criteria | Custom field |
| Business Scope | Business Scope | Custom field |
| Test Steps | Test Steps | Custom field (for Test type) |
| Expected Result | Expected Result | Custom field (for Test type) |
| Story Link | Story Link | Custom field (for Test type) |

**Note**: Custom field names may vary by Jira configuration. Verify field names in your Jira instance.

### Step 5: Preview Import

1. Click "Preview Import"
2. Review sample records
3. Check for mapping errors
4. Verify data appears correctly

### Step 6: Execute Import

1. If preview looks good, click "Begin Import"
2. Monitor import progress
3. Wait for completion (may take several minutes for large imports)

### Step 7: Verify Import

1. Check import summary for errors
2. Navigate to the Epic
3. Verify all stories/tests were created
4. Spot-check several items for correct data
5. Check that labels, priorities, and custom fields populated correctly

### Step 8: Post-Import Cleanup (If Needed)

1. Fix any import errors manually
2. Add missing relationships or links
3. Adjust priorities if needed
4. Notify team of new issues

## Common Import Issues and Solutions

### Issue 1: Field Not Found

**Error**: "Field 'Acceptance Criteria' not found"

**Cause**: Custom field name doesn't match Jira configuration

**Solution**:
1. Check exact field name in Jira: Administration → Issues → Custom Fields
2. Update CSV header to match exact name
3. Or map to correct field during import step

### Issue 2: Invalid Priority Value

**Error**: "Priority 'Critical' is not valid"

**Cause**: Priority name doesn't match Jira priority scheme

**Solution**:
1. Check valid priorities: Administration → Issues → Priorities
2. Update CSV to use exact priority names from Jira
3. Common mappings: Critical → Highest, High → High, Medium → Medium, Low → Low

### Issue 3: German Characters Corrupted

**Error**: "Rufnummer" appears as "Rufnummer"

**Cause**: File not saved as UTF-8

**Solution**:
1. Re-save CSV file with UTF-8 encoding (not ISO-8859-1 or Windows-1252)
2. In Excel: Save As → CSV UTF-8
3. In text editor: Set encoding to UTF-8 before saving

### Issue 4: Newlines Break CSV Structure

**Error**: Import creates multiple issues from one row

**Cause**: Actual newlines in fields instead of `\n`, or missing quotes

**Solution**:
1. Use `\n` for newlines, not actual line breaks
2. Wrap multi-line fields in double quotes
3. Example: `"Step 1\nStep 2\nStep 3"` not:
   ```
   Step 1
   Step 2
   Step 3
   ```

### Issue 5: Commas Break Fields

**Error**: Field values split across columns

**Cause**: Commas in field values without proper quoting

**Solution**:
1. Wrap fields containing commas in double quotes
2. Example: `"As a user, I want to..."` not `As a user, I want to...`

### Issue 6: Quote Escaping Errors

**Error**: Fields contain literal `""` text

**Cause**: Internal quotes not properly escaped

**Solution**:
1. Double internal quotes: `"He said ""Hello"""`
2. Use `escape_field()` function to handle automatically

### Issue 7: Epic Link Not Working

**Error**: Stories not linked to Epic

**Cause**: Epic key doesn't exist or wrong format

**Solution**:
1. Verify Epic exists in Jira
2. Use Epic key (e.g., "EPIC-123") or Epic name
3. Check if custom field "Epic Link" is available for Stories

### Issue 8: Import Succeeds But Fields Empty

**Error**: Issues created but custom fields blank

**Cause**: Field mapping incorrect or fields not available for issue type

**Solution**:
1. Check field configuration for Story/Test issue types
2. Ensure custom fields are available for the issue types being imported
3. Re-map fields during import if needed

## Best Practices Summary

1. **Always validate CSV before import**: Use `validate_csv()` function
2. **Use UTF-8 encoding**: Saves German characters correctly
3. **Keep summaries concise**: Max 255 chars, ideally < 100
4. **Number test steps**: Always use "1. Step one\n2. Step two" format
5. **Link tests to stories**: Always provide story_link value
6. **Use consistent labels**: Standardize tag naming across team
7. **Test with small batch first**: Import 5-10 issues, verify, then import all
8. **Disable notifications for bulk imports**: Prevents email spam
9. **Document custom field mappings**: Keep reference for future imports
10. **Backup before large imports**: Some Jira configs don't allow easy rollback
