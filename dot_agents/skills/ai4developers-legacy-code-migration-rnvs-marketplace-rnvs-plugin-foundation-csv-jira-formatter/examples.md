# CSV Jira Formatter - Examples

This document provides practical examples of using the CSV Jira Formatter skill in real RNVS→VNRM migration scenarios.

## Example 1: Phase 9 - Single Story Export

### Scenario
Generate a single user story for the validation service with acceptance criteria.

### Story Data
```python
story = {
    "summary": "Implement Rufnummer validation service",
    "priority": "High",
    "description": "As a validation service, I want to validate Rufnummer format and structure, so that only valid phone numbers are accepted for porting.",
    "labels": ["vnrm-validation-service", "validation", "phase-12"],
    "acceptance_criteria": """Given a 10-digit Rufnummer (format: 0XXXXXXXXX)
When validation service is called
Then validation passes and returns status: VALID

Given a 9-digit Rufnummer
When validation service is called
Then validation fails and returns error: INVALID_LENGTH

Given a Rufnummer with non-numeric characters
When validation service is called
Then validation fails and returns error: INVALID_FORMAT""",
    "business_scope": "UC-PDA-001: Rufnummernportierung importieren"
}
```

### Generated CSV
```csv
Issue Type,Summary,Priority,Epic Link,Description,Labels,Affect Version,Acceptance Criteria,Business Scope
Story,"Implement Rufnummer validation service",High,PDA-Import,"As a validation service, I want to validate Rufnummer format and structure, so that only valid phone numbers are accepted for porting.","vnrm-validation-service, validation, phase-12",VNRM-1.0,"Given a 10-digit Rufnummer (format: 0XXXXXXXXX)
When validation service is called
Then validation passes and returns status: VALID

Given a 9-digit Rufnummer
When validation service is called
Then validation fails and returns error: INVALID_LENGTH

Given a Rufnummer with non-numeric characters
When validation service is called
Then validation fails and returns error: INVALID_FORMAT","UC-PDA-001: Rufnummernportierung importieren"
```

---

## Example 2: Phase 9 - Multiple Stories for Microservice

### Scenario
Generate user stories for the complete PDA Import Validation microservice (6 stories).

### Stories Data
```python
stories = [
    {
        "summary": "Create Rufnummer validation API endpoint",
        "priority": "High",
        "description": "As a client application, I want to call a REST API to validate Rufnummern, so that I can verify numbers before processing.",
        "labels": ["vnrm-validation-service", "api", "rest"],
        "acceptance_criteria": "Given POST /api/v1/validate/rufnummer endpoint\nWhen valid Rufnummer is sent\nThen response returns 200 OK with validation result",
        "business_scope": "UC-PDA-001"
    },
    {
        "summary": "Validate Rufnummer format (ONKZ + subscriber number)",
        "priority": "High",
        "description": "As the validation service, I want to validate Rufnummer format (ONKZ + subscriber), so that malformed numbers are rejected.",
        "labels": ["vnrm-validation-service", "validation", "business-logic"],
        "acceptance_criteria": "Given Rufnummer with valid ONKZ\nWhen format validation runs\nThen validation passes",
        "business_scope": "UC-PDA-001"
    },
    {
        "summary": "Check ONKZ against RDM reference data",
        "priority": "High",
        "description": "As the validation service, I want to verify ONKZ exists in RDM, so that only allocated area codes are accepted.",
        "labels": ["vnrm-validation-service", "validation", "rdm-integration"],
        "acceptance_criteria": "Given Rufnummer with ONKZ 030 (Berlin)\nWhen RDM lookup is performed\nThen ONKZ is confirmed valid",
        "business_scope": "UC-PDA-001"
    },
    {
        "summary": "Validate subscriber number length per ONKZ",
        "priority": "Medium",
        "description": "As the validation service, I want to validate subscriber number length matches ONKZ rules, so that numbers comply with BNetzA regulations.",
        "labels": ["vnrm-validation-service", "validation", "bnetz-compliance"],
        "acceptance_criteria": "Given ONKZ 030 (requires 7-8 digits)\nWhen subscriber number is 7 digits\nThen validation passes",
        "business_scope": "UC-PDA-001"
    },
    {
        "summary": "Log validation results for audit",
        "priority": "Medium",
        "description": "As a compliance officer, I want all validation attempts logged, so that we have audit trail for regulatory review.",
        "labels": ["vnrm-validation-service", "logging", "audit"],
        "acceptance_criteria": "Given any validation attempt\nWhen validation completes\nThen result is logged with timestamp, input, and outcome",
        "business_scope": "UC-PDA-001"
    },
    {
        "summary": "Handle validation errors gracefully",
        "priority": "Medium",
        "description": "As a client application, I want clear error messages for invalid Rufnummern, so that I can provide feedback to users.",
        "labels": ["vnrm-validation-service", "error-handling", "api"],
        "acceptance_criteria": "Given invalid Rufnummer\nWhen validation fails\nThen response returns 400 with error code and message",
        "business_scope": "UC-PDA-001"
    }
]
```

### Usage
```python
csv_output = format_story_csv(stories, "PDA-Import", "VNRM-1.0")
write_file("phase9/jira_stories.csv", csv_output)
```

### Generated CSV (excerpt)
```csv
Issue Type,Summary,Priority,Epic Link,Description,Labels,Affect Version,Acceptance Criteria,Business Scope
Story,"Create Rufnummer validation API endpoint",High,PDA-Import,"As a client application, I want to call a REST API to validate Rufnummern, so that I can verify numbers before processing.","vnrm-validation-service, api, rest",VNRM-1.0,"Given POST /api/v1/validate/rufnummer endpoint
When valid Rufnummer is sent
Then response returns 200 OK with validation result",UC-PDA-001
Story,"Validate Rufnummer format (ONKZ + subscriber number)",High,PDA-Import,"As the validation service, I want to validate Rufnummer format (ONKZ + subscriber), so that malformed numbers are rejected.","vnrm-validation-service, validation, business-logic",VNRM-1.0,"Given Rufnummer with valid ONKZ
When format validation runs
Then validation passes",UC-PDA-001
...
```

---

## Example 3: Phase 9 - Test Cases for Story

### Scenario
Generate test cases for the "Rufnummer validation API" story (5 unit tests).

### Test Cases Data
```python
testcases = [
    {
        "summary": "Validate 10-digit Rufnummer passes",
        "priority": "High",
        "description": "Positive test: Valid 10-digit Rufnummer with Berlin ONKZ (030)",
        "labels": ["unit-test", "positive", "vnrm-validation-service"],
        "test_steps": "1. Call POST /api/v1/validate/rufnummer\n2. Request body: {\"rfnr\": \"0301234567\"}\n3. Verify HTTP status code\n4. Verify response body structure",
        "expected_result": "Status: 200 OK\nResponse: {\"valid\": true, \"result\": \"PASS\", \"rfnr\": \"0301234567\"}",
        "story_link": "STORY-001"
    },
    {
        "summary": "Validate 11-digit Rufnummer passes",
        "priority": "High",
        "description": "Positive test: Valid 11-digit Rufnummer with Munich ONKZ (089)",
        "labels": ["unit-test", "positive", "vnrm-validation-service"],
        "test_steps": "1. Call POST /api/v1/validate/rufnummer\n2. Request body: {\"rfnr\": \"08912345678\"}\n3. Verify HTTP status code\n4. Verify response body structure",
        "expected_result": "Status: 200 OK\nResponse: {\"valid\": true, \"result\": \"PASS\", \"rfnr\": \"08912345678\"}",
        "story_link": "STORY-001"
    },
    {
        "summary": "Reject 9-digit Rufnummer (too short)",
        "priority": "High",
        "description": "Negative test: Invalid Rufnummer with insufficient digits",
        "labels": ["unit-test", "negative", "vnrm-validation-service"],
        "test_steps": "1. Call POST /api/v1/validate/rufnummer\n2. Request body: {\"rfnr\": \"030123456\"}\n3. Verify HTTP status code\n4. Verify error response structure",
        "expected_result": "Status: 400 Bad Request\nResponse: {\"valid\": false, \"error\": \"INVALID_LENGTH\", \"message\": \"Rufnummer must be 10-11 digits\"}",
        "story_link": "STORY-001"
    },
    {
        "summary": "Reject Rufnummer with invalid characters",
        "priority": "Medium",
        "description": "Negative test: Rufnummer contains non-numeric characters",
        "labels": ["unit-test", "negative", "vnrm-validation-service"],
        "test_steps": "1. Call POST /api/v1/validate/rufnummer\n2. Request body: {\"rfnr\": \"030-123-4567\"}\n3. Verify HTTP status code\n4. Verify error response structure",
        "expected_result": "Status: 400 Bad Request\nResponse: {\"valid\": false, \"error\": \"INVALID_FORMAT\", \"message\": \"Rufnummer must contain only digits\"}",
        "story_link": "STORY-001"
    },
    {
        "summary": "Reject Rufnummer with invalid ONKZ",
        "priority": "Medium",
        "description": "Negative test: ONKZ not found in RDM reference data",
        "labels": ["unit-test", "negative", "vnrm-validation-service", "rdm-integration"],
        "test_steps": "1. Call POST /api/v1/validate/rufnummer\n2. Request body: {\"rfnr\": \"0991234567\"} (invalid ONKZ)\n3. Verify HTTP status code\n4. Verify error response structure",
        "expected_result": "Status: 400 Bad Request\nResponse: {\"valid\": false, \"error\": \"INVALID_ONKZ\", \"message\": \"ONKZ 099 not found in RDM\"}",
        "story_link": "STORY-001"
    }
]
```

### Usage
```python
csv_output = format_testcase_csv(testcases, "PDA-Import", "VNRM-1.0")
write_file("phase9/jira_tests.csv", csv_output)
```

### Generated CSV (excerpt)
```csv
Issue Type,Summary,Priority,Epic Link,Description,Labels,Affect Version,Test Steps,Expected Result,Story Link
Test,"Validate 10-digit Rufnummer passes",High,PDA-Import,"Positive test: Valid 10-digit Rufnummer with Berlin ONKZ (030)","unit-test, positive, vnrm-validation-service",VNRM-1.0,"1. Call POST /api/v1/validate/rufnummer
2. Request body: {""rfnr"": ""0301234567""}
3. Verify HTTP status code
4. Verify response body structure","Status: 200 OK
Response: {""valid"": true, ""result"": ""PASS"", ""rfnr"": ""0301234567""}",STORY-001
Test,"Reject 9-digit Rufnummer (too short)",High,PDA-Import,"Negative test: Invalid Rufnummer with insufficient digits","unit-test, negative, vnrm-validation-service",VNRM-1.0,"1. Call POST /api/v1/validate/rufnummer
2. Request body: {""rfnr"": ""030123456""}
3. Verify HTTP status code
4. Verify error response structure","Status: 400 Bad Request
Response: {""valid"": false, ""error"": ""INVALID_LENGTH"", ""message"": ""Rufnummer must be 10-11 digits""}",STORY-001
...
```

---

## Example 4: Complete Phase 9 Workflow

### Scenario
Generate all stories and tests for PDA Import feature (Phase 9 output).

### Full Workflow Code
```python
# Step 1: Define all user stories
stories = [
    # ... (6 stories from Example 2)
]

# Step 2: Generate story CSV
story_csv = format_story_csv(
    stories=stories,
    epic_link="PDA-Import",
    version="VNRM-1.0"
)

# Step 3: Validate story CSV
story_validation = validate_csv(story_csv)
if not story_validation["valid"]:
    print("Errors in story CSV:")
    for error in story_validation["errors"]:
        print(f"  - {error}")
    exit(1)

# Step 4: Save story CSV
write_file("results/pda-import/phase9/jira_stories.csv", story_csv)
print(f"✓ Generated {len(stories)} stories")

# Step 5: Define test cases for each story
testcases = [
    # ... (5 tests from Example 3 for STORY-001)
    # ... (additional tests for other stories)
]

# Step 6: Generate test CSV
test_csv = format_testcase_csv(
    testcases=testcases,
    epic_link="PDA-Import",
    version="VNRM-1.0"
)

# Step 7: Validate test CSV
test_validation = validate_csv(test_csv)
if not test_validation["valid"]:
    print("Errors in test CSV:")
    for error in test_validation["errors"]:
        print(f"  - {error}")
    exit(1)

# Step 8: Save test CSV
write_file("results/pda-import/phase9/jira_tests.csv", test_csv)
print(f"✓ Generated {len(testcases)} test cases")

# Step 9: Display summary
print(f"""
Phase 9 Output Summary:
- Stories: {len(stories)}
- Test Cases: {len(testcases)}
- Epic: PDA-Import
- Version: VNRM-1.0

Files generated:
- results/pda-import/phase9/jira_stories.csv
- results/pda-import/phase9/jira_tests.csv

Next steps:
1. Review CSV files for correctness
2. Import stories to Jira first
3. Update test story_link fields with actual Jira IDs
4. Import tests to Jira
""")
```

---

## Example 5: Handling Special Characters

### Scenario
Story description contains German umlauts, commas, quotes, and newlines.

### Story with Special Characters
```python
story = {
    "summary": "Überprüfung der ONKZ-Gültigkeit",
    "priority": "High",
    "description": """Als Validierungsservice möchte ich die Gültigkeit der ONKZ überprüfen, damit nur "autorisierte" Bereiche akzeptiert werden.

Hintergrund: Die BNetzA verwaltet die ONKZ-Liste, die folgende Formate enthält:
- 2-stellig (z.B. 30 für Berlin)
- 3-stellig (z.B. 711 für Stuttgart)
- 4-stellig (z.B. 6221 für Heidelberg)

Wichtig: Sonderzeichen wie ä, ö, ü, ß müssen korrekt behandelt werden.""",
    "labels": ["vnrm-validation", "bnetzá-integration", "umlaute"],
    "acceptance_criteria": """Gegeben: Eine ONKZ aus der BNetzA-Liste
Wenn: Die Validierung durchgeführt wird
Dann: Die ONKZ wird als "gültig" markiert

Gegeben: Eine ungültige ONKZ
Wenn: Die Validierung durchgeführt wird
Dann: Ein Fehler wird zurückgegeben""",
    "business_scope": "UC-PDA-001: Portierung durchführen"
}
```

### Generated CSV (showing proper escaping)
```csv
Issue Type,Summary,Priority,Epic Link,Description,Labels,Affect Version,Acceptance Criteria,Business Scope
Story,"Überprüfung der ONKZ-Gültigkeit",High,PDA-Import,"Als Validierungsservice möchte ich die Gültigkeit der ONKZ überprüfen, damit nur ""autorisierte"" Bereiche akzeptiert werden.

Hintergrund: Die BNetzA verwaltet die ONKZ-Liste, die folgende Formate enthält:
- 2-stellig (z.B. 30 für Berlin)
- 3-stellig (z.B. 711 für Stuttgart)
- 4-stellig (z.B. 6221 für Heidelberg)

Wichtig: Sonderzeichen wie ä, ö, ü, ß müssen korrekt behandelt werden.","vnrm-validation, bnetzá-integration, umlaute",VNRM-1.0,"Gegeben: Eine ONKZ aus der BNetzA-Liste
Wenn: Die Validierung durchgeführt wird
Dann: Die ONKZ wird als ""gültig"" markiert

Gegeben: Eine ungültige ONKZ
Wenn: Die Validierung durchgeführt wird
Dann: Ein Fehler wird zurückgegeben","UC-PDA-001: Portierung durchführen"
```

**Key Escaping Applied**:
- Quotes: `"autorisierte"` → `""autorisierte""`
- Quotes: `"gültig"` → `""gültig""`
- Commas: Entire description wrapped in quotes
- Newlines: Preserved as actual newlines within quotes
- German characters: ä, ö, ü, ß preserved (UTF-8 encoding)

---

## Example 6: Integration with Phase 9 Agent

### Scenario
The agile-story-engineer agent uses this skill to generate Jira export during Phase 9.

### Agent Integration Pattern
```python
# In phase9-generate-jira-stories command/agent

# Step 1: Agent analyzes Phase 8 gap analysis
gap_analysis = read_file("results/pda-import/phase8/gap_analysis.md")

# Step 2: Agent generates stories based on gaps
stories = []
for gap in identified_gaps:
    story = {
        "summary": generate_story_title(gap),
        "priority": determine_priority(gap),
        "description": generate_user_story(gap),
        "labels": extract_labels(gap),
        "acceptance_criteria": generate_acceptance_criteria(gap),
        "business_scope": map_to_business_use_case(gap)
    }
    stories.append(story)

# Step 3: Use csv-jira-formatter skill
csv_output = format_story_csv(
    stories=stories,
    epic_link="PDA-Import",
    version="VNRM-1.0"
)

# Step 4: Validate
validation = validate_csv(csv_output)
if validation["warnings"]:
    print(f"⚠ Warnings: {len(validation['warnings'])}")
    for warning in validation["warnings"]:
        print(f"  - {warning}")

# Step 5: Save output
write_file("results/pda-import/phase9/jira_stories.csv", csv_output)
print(f"✓ Phase 9: Generated {len(stories)} Jira stories")
```

---

## Example 7: Validation Error Handling

### Scenario
Story has multiple validation issues that need to be fixed.

### Story with Issues
```python
story = {
    "summary": "This is a very long summary that exceeds the 255 character limit which will cause an error when importing to Jira because Jira has a hard limit on the summary field length and this summary is way too verbose and needs to be shortened significantly to comply with Jira requirements",
    "priority": "Ultra-High",  # Invalid priority
    "description": "Missing user story format",  # No "As a... I want... so that..."
    "labels": ["label1", "label2", "label3", "label4", "label5", "label6", "label7", "label8", "label9", "label10", "label11"],  # Too many labels
    "acceptance_criteria": "",  # Empty criteria
    "business_scope": "UC-PDA-001"
}
```

### Validation Result
```python
csv_output = format_story_csv([story], "EPIC-123", "V1.0")
validation = validate_csv(csv_output)

# validation = {
#     "valid": False,
#     "errors": [
#         "Summary exceeds 255 characters: 267 chars",
#         "Invalid priority: 'Ultra-High'. Must be Critical/High/Medium/Low"
#     ],
#     "warnings": [
#         "Story has 11 labels (recommend ≤ 10)",
#         "Empty acceptance criteria",
#         "Description missing user story format (As a... I want... so that...)"
#     ]
# }
```

### Fixed Story
```python
story_fixed = {
    "summary": "Implement ONKZ validation with BNetzA integration",  # Shortened to 54 chars
    "priority": "High",  # Valid priority
    "description": "As a validation service, I want to validate ONKZ against BNetzA database, so that only authorized area codes are accepted.",
    "labels": ["vnrm-validation", "bnetzá", "onkz", "validation"],  # Reduced to 4 labels
    "acceptance_criteria": "Given valid ONKZ\nWhen validation runs\nThen ONKZ is accepted",
    "business_scope": "UC-PDA-001"
}
```

---

## Best Practices Demonstrated

### 1. Story Writing
- ✓ Use standard user story format: "As a [role], I want to [action], so that [benefit]"
- ✓ Keep summary under 100 characters for readability
- ✓ Include context in description (background, technical details)
- ✓ Use Given/When/Then format for acceptance criteria
- ✓ Link to business use cases for traceability

### 2. Test Case Writing
- ✓ Use descriptive test names that indicate expected behavior
- ✓ Number test steps for clarity
- ✓ Include both positive and negative test cases
- ✓ Specify exact expected results (status codes, response structure)
- ✓ Always link tests to parent stories

### 3. Label Strategy
- ✓ Use consistent naming: kebab-case (e.g., "vnrm-validation-service")
- ✓ Include component labels: service name
- ✓ Include type labels: "unit-test", "integration-test"
- ✓ Include phase labels: "phase-12", "phase-13"
- ✓ Limit to 5-7 labels per issue for maintainability

### 4. CSV Generation
- ✓ Always validate CSV before saving
- ✓ Review warnings even if no errors
- ✓ Save with UTF-8 encoding for German characters
- ✓ Use descriptive filenames: `phase9_pda_import_stories.csv`
- ✓ Test import with small batch first (5-10 issues)

### 5. Jira Import
- ✓ Import stories before tests (so story IDs exist for linking)
- ✓ Verify field mappings match Jira configuration
- ✓ Disable email notifications for bulk imports
- ✓ Review import summary for errors
- ✓ Spot-check several issues after import
