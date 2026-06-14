---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-workflow-14-test-script-generation-workflow
description: Comprehensive methodology for Phase 14 system test script generation. Generates executable test scripts including Postman collections, JMeter plans, pytest integration tests, and OWASP ZAP security scripts. UNIFIED - works for both NEW and CHANGE modes with mode-aware scope.
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/workflow/skills/14-test-script-generation-workflow by codex-knowledge-curation/scripts/persist_project_skills.py. -->

<required_reading>
Read `results/${FEATURE}/.workflow-state.md` before any operation.
This provides workflow mode (NEW or CHANGE), completed phases, and session context.
Use Mode from state file instead of .workflow-state.md.
</required_reading>

# System Test Generation Methodology

## Purpose

Provides comprehensive methodology for **Phase 14 system test script generation** - converting Phase 11 test scenarios and Phase 13/13.1 source code into executable test scripts:

- **Postman Collections**: API endpoint testing with assertions
- **JMeter Test Plans**: Performance, load, stress, and spike testing
- **pytest Integration Tests**: Service integration and E2E testing
- **OWASP ZAP Scripts**: Automated security vulnerability scanning
- **Test Execution Scripts**: Shell orchestration for CI/CD

**Key Principle**: Phase 14 is UNIFIED - works for both NEW and CHANGE modes. Only the SCOPE differs (all endpoints vs changed endpoints). Output always goes to `results/phase14/`.

## When to Use

Use this skill when you need to:

- **Generate API Test Collections** - Postman/Newman tests for REST endpoints
- **Create Performance Tests** - JMeter plans for load/stress testing
- **Build Integration Tests** - pytest scripts for E2E testing
- **Automate Security Scans** - OWASP ZAP scripts for vulnerability detection
- **Orchestrate Test Execution** - Shell scripts for CI/CD pipelines

**Phase Integration**: Used by `/rnvs-workflow:phase14-generate-system-test-scripts` command after Phase 13/13.1.

## Agent Guidance

When you are invoked to perform Phase 14 system test script generation:

**Input Files**:
- `results/${FEATURE}/.workflow-state.md` - Workflow mode
- `results/${FEATURE}/phase11/test-scenarios.json` - Test scenarios

**Mode-Specific Inputs**:
- NEW mode: `results/${FEATURE}/phase13/source_code/` - Generated source code
- CHANGE mode: `results/${FEATURE}/phase13.1/applied-edits-log.json` - Applied changes

**Your Task** (7 Stages):

### Stage 1: Determine Mode and Scope

1. Read `.workflow-state.md` to get `workflow_mode`
2. **NEW mode**:
   - Read Phase 13 source_code/ for all API endpoints
   - Generate tests for ALL endpoints
3. **CHANGE mode**:
   - Read Phase 13.1 applied-edits-log.json
   - Generate tests ONLY for changed/new endpoints
   - Reference existing test baseline from Phase 6 test_infrastructure

**Output for both modes**: `results/${FEATURE}/phase14/` (same location)

### Stage 1.5: Interactive Test Script Selection

**MANDATORY**: Before generating any test scripts, present the user with an interactive selection dialog.

**Use AskUserQuestion to present options:**

```
AskUserQuestion:
  question: "Which test scripts should be generated for this feature?"
  header: "Test Script Selection"
  options:
    - label: "1. Postman Collections (API Tests)"
      description: "REST API endpoint tests with assertions → test_scripts/postman/"
    - label: "2. JMeter Test Plans (Performance Tests)"
      description: "Load, stress, spike, and endurance tests → test_scripts/jmeter/"
    - label: "3. pytest Integration Tests (E2E Tests)"
      description: "Service integration and end-to-end tests → test_scripts/integration/"
    - label: "4. OWASP ZAP Security Scripts (Security Scans)"
      description: "Automated vulnerability scanning → test_scripts/security/"
    - label: "5. Test Execution Scripts (CI/CD Orchestration)"
      description: "Shell scripts for pipeline integration → test_scripts/run_all_tests.sh"
    - label: "All (Recommended)"
      description: "Generate all test script types for comprehensive coverage"
  multiSelect: true
  defaultSelection: "All (Recommended)"
```

**User Response Processing:**
1. Parse user selection (single, multiple, or "All")
2. Store selection in memory for subsequent stages
3. Skip unselected stages during generation

**Selection Mapping:**
| Selection | Stage to Execute |
|-----------|------------------|
| 1 | Stage 2: Postman Collections |
| 2 | Stage 3: JMeter Test Plans |
| 3 | Stage 4: pytest Integration Tests |
| 4 | Stage 5: OWASP ZAP Security Scripts |
| 5 | Stage 6: Test Execution Scripts |
| All | All stages (2-6) |

**Important**:
- Wait for user response before proceeding
- Validate input and re-prompt if invalid
- Confirm selection before generating
- Stage 7 (Test Execution Guide) is always generated as summary

### Stage 2: Generate Postman Collections (Conditional)

**Only execute if user selected option 1 in Stage 1.5**

Generate API test collections for each service/endpoint group:

**Collection Structure**:
```json
{
  "info": {
    "name": "VNRM ${service_name} API Tests",
    "description": "E2E API tests for ${feature}",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    {"key": "baseUrl", "value": "http://localhost:8080"},
    {"key": "apiVersion", "value": "v1"},
    {"key": "authToken", "value": ""}
  ],
  "item": [
    {
      "name": "Setup - Get Auth Token",
      "event": [{"listen": "test", "script": {"exec": ["..."]}}],
      "request": {...}
    },
    {
      "name": "Test 1 - ${operation}",
      "event": [{"listen": "test", "script": {"exec": ["..."]}}],
      "request": {...}
    }
  ]
}
```

**Test Categories**:
- Authentication and authorization tests
- CRUD operation tests (Create, Read, Update, Delete)
- Business logic validation tests
- Error handling and edge case tests
- Data validation tests

**Output**: `results/${FEATURE}/phase14/test_scripts/postman/`

### Stage 3: Generate JMeter Test Plans (Conditional)

**Only execute if user selected option 2 in Stage 1.5**

Generate performance test plans:

**Test Types**:

| Type | Threads | Ramp-up | Duration | Purpose |
|------|---------|---------|----------|---------|
| Load | 100 | 60s | 300s | Normal load testing |
| Stress | 500 | 120s | 600s | Beyond normal capacity |
| Spike | 200 | 10s | 180s | Sudden load increase |
| Endurance | 50 | 30s | 3600s | Sustained load |

**JMeter Plan Structure** (XML):
- Thread Group with configurable parameters
- HTTP Request Defaults for base URL
- HTTP Samplers for each endpoint
- Response Assertions (status codes, content)
- Duration Assertions (response time thresholds)
- Summary Report listener

**Output**: `results/${FEATURE}/phase14/test_scripts/jmeter/`

### Stage 4: Generate pytest Integration Tests (Conditional)

**Only execute if user selected option 3 in Stage 1.5**

Generate pytest scripts for integration testing:

**Test Structure**:
```python
import pytest
import requests

BASE_URL = "http://localhost:8080/api/v1"

@pytest.fixture(scope="session")
def auth_token():
    """Get authentication token for tests"""
    response = requests.post(f"{BASE_URL}/auth/login", json={...})
    return response.json()["token"]

@pytest.fixture
def api_headers(auth_token):
    """Create headers with auth token"""
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }

class Test${ServiceName}API:
    """Integration tests for ${ServiceName} API"""

    def test_create_${resource}(self, api_headers):
        """Test creating a new ${resource}"""
        # Arrange
        payload = {...}

        # Act
        response = requests.post(f"{BASE_URL}/${resource}",
                                json=payload, headers=api_headers)

        # Assert
        assert response.status_code == 201
        assert "id" in response.json()
```

**Test Categories**:
- API endpoint testing (CRUD)
- Service-to-service communication
- Database integration
- Event-driven flows
- Error scenarios and boundary conditions

**Output**: `results/${FEATURE}/phase14/test_scripts/integration/`

### Stage 5: Generate OWASP ZAP Security Scripts (Conditional)

**Only execute if user selected option 4 in Stage 1.5**

Generate automated security scanning scripts:

**ZAP Script Structure**:
```python
#!/usr/bin/env python3
from zapv2 import ZAPv2
import time

ZAP_API_KEY = 'your-api-key'
TARGET_URL = 'http://localhost:8080/api/v1'

zap = ZAPv2(apikey=ZAP_API_KEY)

# Spider the target
scan_id = zap.spider.scan(TARGET_URL)
while int(zap.spider.status(scan_id)) < 100:
    time.sleep(2)

# Active scan
scan_id = zap.ascan.scan(TARGET_URL)
while int(zap.ascan.status(scan_id)) < 100:
    time.sleep(5)

# Get alerts
alerts = zap.core.alerts(baseurl=TARGET_URL)
high_alerts = [a for a in alerts if a['risk'] == 'High']

# Generate report
html_report = zap.core.htmlreport()
with open('zap_report.html', 'w') as f:
    f.write(html_report)

# Fail if high-risk vulnerabilities
if len(high_alerts) > 0:
    exit(1)
```

**Security Test Coverage**:
- Automated vulnerability scanning
- Authentication/authorization testing
- Input validation testing
- SQL injection testing
- XSS testing
- OWASP Top 10 vulnerabilities

**Output**: `results/${FEATURE}/phase14/test_scripts/security/`

### Stage 6: Generate Test Execution Scripts (Conditional)

**Only execute if user selected option 5 in Stage 1.5**

Generate shell scripts for CI/CD pipeline integration:

**run_all_tests.sh Structure**:
```bash
#!/bin/bash
set -e

echo "Starting Test Execution..."

# Run API Tests (if Postman collections exist)
if [ -d "postman" ]; then
    echo "Running Postman/Newman API Tests..."
    newman run postman/api_tests.json --environment postman/environment.json
fi

# Run Integration Tests (if pytest tests exist)
if [ -d "integration" ]; then
    echo "Running pytest Integration Tests..."
    pytest integration/ -v --html=reports/pytest-report.html
fi

# Run Performance Tests (if JMeter plans exist)
if [ -d "jmeter" ]; then
    echo "Running JMeter Performance Tests..."
    jmeter -n -t jmeter/load_test.jmx -l results/load.jtl
fi

# Run Security Tests (if ZAP scripts exist)
if [ -d "security" ]; then
    echo "Running OWASP ZAP Security Scans..."
    python3 security/zap_scan.py
fi

echo "All tests completed!"
```

**Output**: `results/${FEATURE}/phase14/test_scripts/run_all_tests.sh`

### Stage 7: Generate Test Execution Guide (Always)

**Always execute regardless of user selection - provides summary of generated tests**

Create comprehensive test execution documentation:

**Guide Structure**:
```markdown
# Test Execution Guide: ${FEATURE}

## 1. Prerequisites
- Docker and Docker Compose installed
- Node.js and newman installed
- Python 3.x and pytest installed
- JMeter installed
- OWASP ZAP installed

## 2. Environment Setup
[Docker compose commands, environment variables]

## 3. Running Tests

### 3.1 API Tests (Postman/Newman)
```bash
newman run postman/api_tests.json --environment postman/env.json
```

### 3.2 Integration Tests (pytest)
```bash
pytest integration/ -v --html=reports/pytest-report.html
```

### 3.3 Performance Tests (JMeter)
```bash
jmeter -n -t jmeter/load_test.jmx -l results/load.jtl
```

### 3.4 Security Tests (OWASP ZAP)
```bash
python3 security/zap_scan.py
```

### 3.5 Run All Tests
```bash
./run_all_tests.sh
```

## 4. Test Results
[Location and interpretation of results]

## 5. CI/CD Integration
[Pipeline configuration examples]

## 6. Troubleshooting
[Common issues and solutions]

**Output**: `results/${FEATURE}/phase14/test_execution_guide.md`

---

## Quick Reference

### Output Directory Structure

```
results/${FEATURE}/phase14/
├── test_scripts/
│   ├── postman/
│   │   ├── api_tests.json
│   │   └── environment.json
│   ├── jmeter/
│   │   ├── load_test.jmx
│   │   ├── stress_test.jmx
│   │   └── spike_test.jmx
│   ├── integration/
│   │   ├── conftest.py
│   │   ├── test_${service}_api.py
│   │   └── requirements.txt
│   ├── security/
│   │   ├── zap_scan.py
│   │   └── zap_config.yaml
│   ├── data/
│   │   └── setup_test_data.py
│   └── run_all_tests.sh
└── test_execution_guide.md
```

### Mode-Aware Scope

| Mode | Input Source | Scope | Output Location |
|------|--------------|-------|-----------------|
| **NEW** | Phase 13 source_code/ | All endpoints | results/phase14/ |
| **CHANGE** | Phase 13.1 applied-edits-log.json | Changed endpoints only | results/phase14/ |

### Test Tool Matrix

| Tool | Purpose | Output Format |
|------|---------|---------------|
| Postman/Newman | API testing | JSON collection |
| JMeter | Performance testing | JMX plan |
| pytest | Integration testing | Python scripts |
| OWASP ZAP | Security testing | Python + HTML report |

---

## Success Criteria

When using this skill, ensure:

- [ ] Interactive selection dialog presented to user (Stage 1.5)
- [ ] User selection correctly parsed and validated
- [ ] Only selected test types are generated
- [ ] Workflow mode correctly determines scope (all vs changed)
- [ ] Postman collections cover all relevant endpoints (if selected)
- [ ] JMeter plans include load, stress, and spike scenarios (if selected)
- [ ] pytest tests cover API endpoints and integration points (if selected)
- [ ] OWASP ZAP script configured for security scanning (if selected)
- [ ] Test execution scripts orchestrate selected test types (if selected)
- [ ] Test execution guide is comprehensive and actionable (always generated)
- [ ] CI/CD integration patterns documented

---

## Final Step: Update Workflow State

After all diagrams validate, update `results/${FEATURE}/.workflow-state.md`:

1. **Phase 14**: Set to Complete with timestamp
2. **Last Activity**: "Completed Phase 14 test script generation"
3. **Next Action**: "Run /15-code-quality-workflow ${FEATURE}"
4. **Decisions Log**: Add system test scripts

---

## Related Skills

- **11-system-test-workflow** - Phase 11 test scenario definition (input)
- **13-source-code-generation-workflow** - Phase 13.1 applied changes (input for CHANGE mode)
- **code-generator** - Phase 13 source code (input for NEW mode)
- **15-code-quality-workflow** - Phase 15 quality analysis (next phase)

---

**This skill provides the complete methodology for generating production-ready system test scripts in the RNVS-VNRM migration workflow.**
