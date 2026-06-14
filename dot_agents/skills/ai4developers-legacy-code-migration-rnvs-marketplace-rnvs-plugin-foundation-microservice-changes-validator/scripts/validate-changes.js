#!/usr/bin/env node

/**
 * validate-changes.js
 *
 * Proper validation for microservice-changes-design.json quality assessment.
 * Validates OpenAPI schemas, DDL, Avro schemas, and JSON structure.
 * Uses manual validation pattern (no external dependencies).
 *
 * Usage:
 *   node validate-changes.js --delta <path> --classification <path> --output <path>
 *
 * Exit codes:
 *   0 = Success (COMPLETE status)
 *   1 = Validation failed (PARTIAL or INCOMPLETE status)
 *   2 = File not found or parse error
 */

const fs = require('fs');
const path = require('path');

// Parse command line arguments
function parseArgs() {
  const args = process.argv.slice(2);
  const params = {};

  for (let i = 0; i < args.length; i += 2) {
    const key = args[i].replace('--', '');
    params[key] = args[i + 1];
  }

  if (!params.delta || !params.classification || !params.output) {
    console.error('Usage: node validate-changes.js --delta <path> --classification <path> --output <path>');
    process.exit(2);
  }

  return params;
}

// Load and parse JSON file
function loadJSON(filePath) {
  try {
    if (!fs.existsSync(filePath)) {
      console.error(`❌ File not found: ${filePath}`);
      process.exit(2);
    }

    const content = fs.readFileSync(filePath, 'utf-8');
    return JSON.parse(content);
  } catch (error) {
    console.error(`❌ Error reading/parsing ${filePath}: ${error.message}`);
    process.exit(2);
  }
}

// Safe array length
function safeLength(value) {
  return Array.isArray(value) ? value.length : 0;
}

// ======================
// Validation Helpers
// ======================

/**
 * Validate OpenAPI endpoint schema structure
 * Checks for required OpenAPI 3.0 fields and valid structure
 */
function validateOpenAPIEndpoint(endpoint) {
  const errors = [];
  const warnings = [];

  // Required fields
  if (!endpoint.path) errors.push('Missing path');
  if (!endpoint.method) errors.push('Missing method');
  if (!endpoint.description) warnings.push('Missing description');

  // Validate HTTP method
  const validMethods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'];
  if (endpoint.method && !validMethods.includes(endpoint.method.toUpperCase())) {
    errors.push(`Invalid HTTP method: ${endpoint.method}`);
  }

  // Validate request structure if present
  if (endpoint.request) {
    if (endpoint.request.body && !endpoint.request.body.schema) {
      warnings.push('Request body missing schema');
    }
  }

  // Validate response structure if present
  if (endpoint.response) {
    const statusCodes = Object.keys(endpoint.response);

    // Check for common status codes
    if (!statusCodes.includes('200') && !statusCodes.includes('201') && !statusCodes.includes('202')) {
      warnings.push('Missing success response (200/201/202)');
    }
    if (!statusCodes.includes('400')) {
      warnings.push('Missing 400 Bad Request response');
    }
    if (!statusCodes.includes('500')) {
      warnings.push('Missing 500 Internal Server Error response');
    }

    // Validate each response has description or error_code
    statusCodes.forEach(code => {
      const response = endpoint.response[code];
      if (!response.description && !response.error_code) {
        warnings.push(`Response ${code} missing description and error_code`);
      }
    });
  } else {
    errors.push('Missing response definitions');
  }

  return { errors, warnings, isValid: errors.length === 0 };
}

/**
 * Validate PostgreSQL DDL statement
 * Checks for basic DDL syntax and required elements
 */
function validateDDL(ddl, tableName) {
  const errors = [];
  const warnings = [];

  if (!ddl || typeof ddl !== 'string') {
    errors.push('DDL must be a non-empty string');
    return { errors, warnings, isValid: false };
  }

  // Check if it's a CREATE TABLE or ALTER TABLE statement
  const isCreateTable = /^\s*CREATE\s+TABLE/i.test(ddl);
  const isAlterTable = /^\s*ALTER\s+TABLE/i.test(ddl);

  if (!isCreateTable && !isAlterTable) {
    errors.push('DDL must be CREATE TABLE or ALTER TABLE statement');
  }

  // For CREATE TABLE, check essential elements
  if (isCreateTable) {
    // Check for primary key
    if (!/PRIMARY\s+KEY/i.test(ddl)) {
      warnings.push('Table missing explicit PRIMARY KEY');
    }

    // Check for timestamps (created_at, updated_at)
    if (!/created_at/i.test(ddl)) {
      warnings.push('Table missing created_at timestamp');
    }
    if (!/updated_at/i.test(ddl)) {
      warnings.push('Table missing updated_at timestamp');
    }

    // Check for optimistic locking version column (common pattern)
    if (!/version\s+INTEGER/i.test(ddl) && !/version\s+BIGINT/i.test(ddl)) {
      warnings.push('Table might be missing version column for optimistic locking');
    }
  }

  // Validate basic SQL syntax
  const openParens = (ddl.match(/\(/g) || []).length;
  const closeParens = (ddl.match(/\)/g) || []).length;
  if (openParens !== closeParens) {
    errors.push('Unbalanced parentheses in DDL');
  }

  // Check for ending semicolon
  if (!ddl.trim().endsWith(';')) {
    warnings.push('DDL should end with semicolon');
  }

  return { errors, warnings, isValid: errors.length === 0 };
}

/**
 * Validate Avro schema structure
 * Checks for required Avro fields and valid types
 */
function validateAvroSchema(schema) {
  const errors = [];
  const warnings = [];

  if (!schema || typeof schema !== 'object') {
    errors.push('Avro schema must be an object');
    return { errors, warnings, isValid: false };
  }

  // Required fields for record type
  if (schema.type === 'record') {
    if (!schema.name) errors.push('Avro record missing name');
    if (!schema.namespace) warnings.push('Avro record missing namespace');
    if (!schema.fields || !Array.isArray(schema.fields)) {
      errors.push('Avro record missing fields array');
    } else {
      // Validate each field
      schema.fields.forEach((field, index) => {
        if (!field.name) errors.push(`Field ${index} missing name`);
        if (!field.type) errors.push(`Field ${field.name || index} missing type`);
      });

      // Check for common event fields
      const fieldNames = schema.fields.map(f => f.name);
      if (!fieldNames.includes('event_id')) {
        warnings.push('Event schema missing event_id field');
      }
      if (!fieldNames.includes('event_timestamp')) {
        warnings.push('Event schema missing event_timestamp field');
      }
      if (!fieldNames.includes('correlation_id')) {
        warnings.push('Event schema missing correlation_id field');
      }
    }
  }

  // Validate Avro types
  const validAvroTypes = ['null', 'boolean', 'int', 'long', 'float', 'double',
                          'bytes', 'string', 'record', 'enum', 'array', 'map', 'union', 'fixed'];
  if (schema.type && !validAvroTypes.includes(schema.type) && !Array.isArray(schema.type)) {
    errors.push(`Invalid Avro type: ${schema.type}`);
  }

  return { errors, warnings, isValid: errors.length === 0 };
}

/**
 * Validate JSON structure using manual checks (no external dependencies)
 * Checks required fields, types, and nested structure
 * Returns validation result with errors/warnings
 */
function validateStructure(data, requiredFields, typeChecks) {
  const errors = [];
  const warnings = [];

  // Check required fields
  const missing = requiredFields.filter(field => {
    const keys = field.split('.');
    let current = data;
    for (const key of keys) {
      if (!current || !(key in current)) return true;
      current = current[key];
    }
    return false;
  });

  if (missing.length > 0) {
    errors.push(`Missing required fields: ${missing.join(', ')}`);
  }

  // Check types
  typeChecks.forEach(check => {
    const keys = check.path.split('.');
    let current = data;
    for (const key of keys) {
      if (!current) break;
      current = current[key];
    }

    if (current !== undefined && current !== null) {
      const actualType = Array.isArray(current) ? 'array' : typeof current;
      if (actualType !== check.type) {
        errors.push(`${check.path} must be ${check.type}, got ${actualType}`);
      }
    }
  });

  return { errors, warnings, isValid: errors.length === 0 };
}

// ======================
// Gate Validation Functions
// ======================

// Gate 1: Completeness (30 points)
// Checks if all delta categories are populated with meaningful data
function validateCompleteness(delta) {
  const changes = delta.changes || {};
  let score = 0;
  const errors = [];
  const warnings = [];

  // API changes (6 points)
  const apiChanges = changes.api_changes || {};
  const totalApiChanges = safeLength(apiChanges.endpoints_to_add) +
                          safeLength(apiChanges.endpoints_to_modify) +
                          safeLength(apiChanges.endpoints_to_deprecate);
  if (totalApiChanges > 0) {
    score += 6;
  } else {
    warnings.push('No API changes detected');
  }

  // Database changes (6 points)
  const dbChanges = changes.database_changes || {};
  const totalDbChanges = safeLength(dbChanges.tables_to_add) +
                         safeLength(dbChanges.columns_to_add) +
                         safeLength(dbChanges.indexes_to_add);
  if (totalDbChanges > 0) {
    score += 6;
  } else {
    warnings.push('No database changes detected');
  }

  // Event changes (6 points)
  const eventChanges = changes.event_changes || {};
  const totalEventChanges = safeLength(eventChanges.topics_to_add) +
                            safeLength(eventChanges.subscriptions_to_add);
  if (totalEventChanges > 0) {
    score += 6;
  } else {
    warnings.push('No event changes detected');
  }

  // State machine changes (6 points)
  const stateChanges = changes.state_machine_changes || {};
  const totalStateChanges = safeLength(stateChanges.new_states) +
                            safeLength(stateChanges.new_transitions);
  if (totalStateChanges > 0) {
    score += 6;
  } else {
    warnings.push('No state machine changes detected');
  }

  // Dependency changes (6 points)
  const depChanges = changes.dependency_changes || {};
  if (safeLength(depChanges.new_internal_dependencies) > 0) {
    score += 6;
  } else {
    warnings.push('No dependency changes detected');
  }

  return {
    gate: 'Completeness',
    weight: 30,
    score: score,
    passed: score >= 18, // At least 3 out of 5 categories
    errors: errors,
    warnings: warnings
  };
}

// Gate 2: API Quality (30 points)
// Proper validation of API endpoint specifications using OpenAPI 3.0 rules
function validateApiQuality(delta) {
  const apiChanges = delta.changes?.api_changes || {};
  let score = 0;
  const errors = [];
  const warnings = [];

  const endpointsToAdd = apiChanges.endpoints_to_add || [];
  const endpointsToModify = apiChanges.endpoints_to_modify || [];
  const endpointsToDeprecate = apiChanges.endpoints_to_deprecate || [];
  const totalEndpoints = endpointsToAdd.length + endpointsToModify.length + endpointsToDeprecate.length;

  if (totalEndpoints === 0) {
    score = 30; // No API changes = perfect score for this gate
    warnings.push('No API changes to validate');
    return {
      gate: 'API Quality',
      weight: 30,
      score: score,
      passed: true,
      errors: errors,
      warnings: warnings
    };
  }

  // Validate each endpoint using proper OpenAPI validation (20 points)
  let validEndpointCount = 0;
  let endpointErrorCount = 0;

  [...endpointsToAdd, ...endpointsToModify].forEach((endpoint, index) => {
    const validation = validateOpenAPIEndpoint(endpoint);

    if (validation.isValid) {
      validEndpointCount++;
    } else {
      endpointErrorCount++;
      validation.errors.forEach(err => {
        errors.push(`Endpoint ${endpoint.path || index}: ${err}`);
      });
    }

    validation.warnings.forEach(warn => {
      warnings.push(`Endpoint ${endpoint.path || index}: ${warn}`);
    });
  });

  score += (validEndpointCount / (endpointsToAdd.length + endpointsToModify.length || 1)) * 20;

  // Check for RNVS source mapping (5 points)
  let withMappingCount = 0;
  [...endpointsToAdd, ...endpointsToModify, ...endpointsToDeprecate].forEach(endpoint => {
    if (endpoint.maps_from || endpoint.source) {
      withMappingCount++;
    }
  });
  score += (withMappingCount / totalEndpoints) * 5;

  // Check for business rules enforcement (5 points)
  let withBusinessRulesCount = 0;
  [...endpointsToAdd, ...endpointsToModify].forEach(endpoint => {
    if (endpoint.business_rules_enforced && Array.isArray(endpoint.business_rules_enforced) && endpoint.business_rules_enforced.length > 0) {
      withBusinessRulesCount++;
    }
  });
  score += (withBusinessRulesCount / (endpointsToAdd.length + endpointsToModify.length || 1)) * 5;

  // Summary messages
  if (endpointErrorCount > 0) {
    errors.push(`${endpointErrorCount} endpoints failed OpenAPI validation`);
  }
  if (withMappingCount < totalEndpoints) {
    warnings.push(`${totalEndpoints - withMappingCount} endpoints missing RNVS source mapping`);
  }

  return {
    gate: 'API Quality',
    weight: 30,
    score: Math.round(score),
    passed: score >= 20 && endpointErrorCount === 0,
    errors: errors,
    warnings: warnings
  };
}

// Gate 3: Database Quality (20 points)
// Proper validation of database changes including DDL syntax
function validateDatabaseQuality(delta) {
  const dbChanges = delta.changes?.database_changes || {};
  let score = 0;
  const errors = [];
  const warnings = [];

  const tablesToAdd = dbChanges.tables_to_add || [];
  const columnsToAdd = dbChanges.columns_to_add || [];
  const indexesToAdd = dbChanges.indexes_to_add || [];

  const totalDbChanges = tablesToAdd.length + columnsToAdd.length + indexesToAdd.length;

  if (totalDbChanges === 0) {
    score = 20; // No database changes = perfect score
    warnings.push('No database changes to validate');
    return {
      gate: 'Database Quality',
      weight: 20,
      score: score,
      passed: true,
      errors: errors,
      warnings: warnings
    };
  }

  // Validate DDL for tables_to_add (10 points)
  let validDDLCount = 0;
  tablesToAdd.forEach((table, index) => {
    if (table.ddl) {
      const validation = validateDDL(table.ddl, table.table_name);

      if (validation.isValid) {
        validDDLCount++;
      } else {
        validation.errors.forEach(err => {
          errors.push(`Table ${table.table_name || index}: ${err}`);
        });
      }

      validation.warnings.forEach(warn => {
        warnings.push(`Table ${table.table_name || index}: ${warn}`);
      });
    } else {
      errors.push(`Table ${table.table_name || index}: Missing DDL statement`);
    }
  });

  // Validate columns_to_add have DDL
  columnsToAdd.forEach((column, index) => {
    if (column.ddl) {
      const validation = validateDDL(column.ddl, column.table_name);
      if (!validation.isValid) {
        validation.errors.forEach(err => {
          errors.push(`Column ${column.column_name || index}: ${err}`);
        });
      }
    } else {
      errors.push(`Column ${column.column_name || index}: Missing DDL statement`);
    }
  });

  // Validate indexes_to_add have DDL
  indexesToAdd.forEach((index, idx) => {
    if (!index.ddl) {
      errors.push(`Index ${index.index_name || idx}: Missing DDL statement`);
    }
  });

  score += (validDDLCount / (tablesToAdd.length || 1)) * 10;

  // Check for documentation (5 points)
  let withPurposeCount = 0;
  tablesToAdd.forEach(table => {
    if (table.purpose && table.purpose.length > 20) {
      withPurposeCount++;
    }
  });
  score += (withPurposeCount / (tablesToAdd.length || 1)) * 5;

  // Check for source attribution (5 points)
  let withSourceCount = 0;
  [...tablesToAdd, ...columnsToAdd, ...indexesToAdd].forEach(item => {
    if (item.source) {
      withSourceCount++;
    }
  });
  score += (withSourceCount / totalDbChanges) * 5;

  if (withPurposeCount < tablesToAdd.length) {
    warnings.push(`${tablesToAdd.length - withPurposeCount} tables missing clear purpose`);
  }
  if (withSourceCount < totalDbChanges) {
    warnings.push(`${totalDbChanges - withSourceCount} database changes missing source attribution`);
  }

  return {
    gate: 'Database Quality',
    weight: 20,
    score: Math.round(score),
    passed: score >= 14 && errors.length === 0,
    errors: errors,
    warnings: warnings
  };
}

// Gate 4: Integration Quality (10 points)
// Proper validation of event schemas and dependency specifications
function validateIntegrationQuality(delta) {
  const eventChanges = delta.changes?.event_changes || {};
  const depChanges = delta.changes?.dependency_changes || {};
  let score = 0;
  const errors = [];
  const warnings = [];

  const topicsToAdd = eventChanges.topics_to_add || [];
  const subscriptionsToAdd = eventChanges.subscriptions_to_add || [];
  const depsToAdd = depChanges.new_internal_dependencies || [];

  const totalIntegrations = topicsToAdd.length + subscriptionsToAdd.length + depsToAdd.length;

  if (totalIntegrations === 0) {
    score = 10; // No integrations = perfect score
    warnings.push('No integration changes to validate');
    return {
      gate: 'Integration Quality',
      weight: 10,
      score: score,
      passed: true,
      errors: errors,
      warnings: warnings
    };
  }

  // Validate Avro schemas for topics_to_add (5 points)
  let validSchemaCount = 0;
  topicsToAdd.forEach((topic, index) => {
    if (topic.avro_schema) {
      const validation = validateAvroSchema(topic.avro_schema);

      if (validation.isValid) {
        validSchemaCount++;
      } else {
        validation.errors.forEach(err => {
          errors.push(`Topic ${topic.topic_name || index}: ${err}`);
        });
      }

      validation.warnings.forEach(warn => {
        warnings.push(`Topic ${topic.topic_name || index}: ${warn}`);
      });
    } else {
      errors.push(`Topic ${topic.topic_name || index}: Missing avro_schema`);
    }
  });

  score += (validSchemaCount / (topicsToAdd.length || 1)) * 5;

  // Check subscriptions have idempotency strategy (2 points)
  let withIdempotencyCount = 0;
  subscriptionsToAdd.forEach((sub, index) => {
    if (sub.idempotency && sub.idempotency.length > 10) {
      withIdempotencyCount++;
    } else {
      warnings.push(`Subscription ${sub.topic_name || index}: Missing idempotency strategy`);
    }
  });
  score += (withIdempotencyCount / (subscriptionsToAdd.length || 1)) * 2;

  // Check items have descriptions and source attribution (3 points)
  let withDescCount = 0;
  let withSourceCount = 0;
  [...topicsToAdd, ...subscriptionsToAdd, ...depsToAdd].forEach(item => {
    if (item.description && item.description.length > 20) {
      withDescCount++;
    }
    if (item.source || item.source_service) {
      withSourceCount++;
    }
  });
  score += (withDescCount / totalIntegrations) * 1.5;
  score += (withSourceCount / totalIntegrations) * 1.5;

  if (withDescCount < totalIntegrations) {
    warnings.push(`${totalIntegrations - withDescCount} integrations missing descriptions`);
  }
  if (withSourceCount < totalIntegrations) {
    warnings.push(`${totalIntegrations - withSourceCount} integrations missing source attribution`);
  }

  return {
    gate: 'Integration Quality',
    weight: 10,
    score: Math.round(score),
    passed: score >= 7 && errors.length === 0,
    errors: errors,
    warnings: warnings
  };
}

// Gate 5: Schema Validation (10 points)
// Manual JSON structure validation (no external dependencies)
function validateSchema(delta) {
  const errors = [];
  const warnings = [];
  let score = 10; // Start with perfect score, deduct for issues

  // Check 1: Valid JSON (already validated via JSON.parse in loadJSON)
  // Score: implicit (file already parsed successfully)

  // Check 2: Required top-level fields
  const requiredTopLevel = ['baseline', 'requirements', 'changes'];
  const missingTopLevel = requiredTopLevel.filter(field => !(field in delta));

  if (missingTopLevel.length > 0) {
    errors.push(`Missing required top-level fields: ${missingTopLevel.join(', ')}`);
    score -= 3;
  }

  // Check 3: Baseline object structure
  if (!delta.baseline) {
    errors.push('Missing baseline object');
    score -= 2;
  } else {
    if (typeof delta.baseline !== 'object') {
      errors.push('baseline must be an object');
      score -= 2;
    } else {
      // Required baseline fields
      if (!delta.baseline.source) {
        errors.push('baseline.source is required');
        score -= 1;
      } else if (typeof delta.baseline.source !== 'string') {
        errors.push('baseline.source must be a string');
      }

      if (!delta.baseline.service_name) {
        errors.push('baseline.service_name is required');
        score -= 1;
      } else if (typeof delta.baseline.service_name !== 'string') {
        errors.push('baseline.service_name must be a string');
      }

      // Optional but recommended
      if (delta.baseline.service_version && typeof delta.baseline.service_version !== 'string') {
        warnings.push('baseline.service_version should be a string');
      }
    }
  }

  // Check 4: Requirements object structure
  if (!delta.requirements) {
    errors.push('Missing requirements object');
    score -= 2;
  } else {
    if (typeof delta.requirements !== 'object') {
      errors.push('requirements must be an object');
      score -= 2;
    } else {
      // Required requirements fields
      if (!delta.requirements.source) {
        errors.push('requirements.source is required');
        score -= 1;
      } else if (typeof delta.requirements.source !== 'string') {
        errors.push('requirements.source must be a string');
      }

      if (!delta.requirements.feature_name) {
        errors.push('requirements.feature_name is required');
        score -= 1;
      } else if (typeof delta.requirements.feature_name !== 'string') {
        errors.push('requirements.feature_name must be a string');
      }
    }
  }

  // Check 5: Changes object structure
  if (!delta.changes) {
    errors.push('Missing changes object');
    score -= 3;
  } else {
    if (typeof delta.changes !== 'object') {
      errors.push('changes must be an object');
      score -= 3;
    } else {
      // Validate nested changes structure
      const changeCategories = [
        'api_changes',
        'database_changes',
        'event_changes',
        'state_machine_changes',
        'dependency_changes'
      ];

      changeCategories.forEach(category => {
        if (delta.changes[category]) {
          if (typeof delta.changes[category] !== 'object') {
            warnings.push(`changes.${category} should be an object`);
          } else {
            // Validate arrays within each category
            Object.keys(delta.changes[category]).forEach(key => {
              if (delta.changes[category][key] && !Array.isArray(delta.changes[category][key])) {
                warnings.push(`changes.${category}.${key} should be an array`);
              }
            });
          }
        }
      });

      // Check for at least one change category
      const hasAnyChanges = changeCategories.some(cat =>
        delta.changes[cat] && Object.keys(delta.changes[cat]).length > 0
      );

      if (!hasAnyChanges) {
        warnings.push('No changes detected in any category (api, database, event, state_machine, dependency)');
      }
    }
  }

  return {
    gate: 'Schema Validation',
    weight: 10,
    score: Math.max(0, score),
    passed: score >= 7 && errors.length === 0,
    errors: errors,
    warnings: warnings
  };
}

// Calculate overall quality score
function calculateOverallScore(gates) {
  let weightedScore = 0;
  let totalWeight = 0;

  gates.forEach(gate => {
    weightedScore += (gate.score / gate.weight) * gate.weight;
    totalWeight += gate.weight;
  });

  return Math.round(weightedScore);
}

// Determine overall status
function determineStatus(score, qualityTarget) {
  if (score >= qualityTarget) {
    return 'COMPLETE';
  } else if (score >= qualityTarget - 15) {
    return 'PARTIAL';
  } else {
    return 'INCOMPLETE';
  }
}

// Main execution
function main() {
  const params = parseArgs();

  console.log('🔍 Validating microservice changes...');
  console.log(`   Delta: ${params.delta}`);
  console.log(`   Classification: ${params.classification}`);

  // Load inputs
  const delta = loadJSON(params.delta);
  const classification = loadJSON(params.classification);

  // Run validation gates
  const gate1 = validateCompleteness(delta);
  const gate2 = validateApiQuality(delta);
  const gate3 = validateDatabaseQuality(delta);
  const gate4 = validateIntegrationQuality(delta);
  const gate5 = validateSchema(delta);

  const gates = [gate1, gate2, gate3, gate4, gate5];

  // Calculate overall score
  const overallScore = calculateOverallScore(gates);
  const qualityTarget = classification.quality_target || 75;
  const overallStatus = determineStatus(overallScore, qualityTarget);

  // Collect all errors and warnings
  const allErrors = gates.flatMap(g => g.errors);
  const allWarnings = gates.flatMap(g => g.warnings);

  // Build validation report
  const report = {
    validated_at: new Date().toISOString(),
    validation_method: 'PROPER',
    baseline: delta.baseline,
    requirements: delta.requirements,
    change_type: classification.change_type,
    complexity_score: classification.complexity_score,
    overall_status: overallStatus,
    overall_quality_score: overallScore,
    quality_target: qualityTarget,
    gates_passed: gates.filter(g => g.passed).length,
    gates_total: gates.length,
    validation_gates: gates.map(g => ({
      gate: g.gate,
      weight: g.weight,
      score: g.score,
      passed: g.passed,
      error_count: g.errors.length,
      warning_count: g.warnings.length
    })),
    errors: allErrors,
    warnings: allWarnings,
    recommendations: generateRecommendations(overallStatus, gates)
  };

  // Write output
  const outputDir = path.dirname(params.output);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  fs.writeFileSync(params.output, JSON.stringify(report, null, 2), 'utf-8');

  // Summary
  console.log(`✅ Validation complete (PROPER)`);
  console.log(`   Status: ${overallStatus}`);
  console.log(`   Score: ${overallScore}/${qualityTarget}`);
  console.log(`   Gates Passed: ${report.gates_passed}/${report.gates_total}`);
  console.log(`   Errors: ${allErrors.length}`);
  console.log(`   Warnings: ${allWarnings.length}`);
  console.log(`   Output: ${params.output}`);

  // Exit code based on status
  if (overallStatus === 'COMPLETE') {
    process.exit(0);
  } else {
    process.exit(1);
  }
}

// Generate recommendations based on validation results
function generateRecommendations(status, gates) {
  const recommendations = [];

  if (status === 'COMPLETE') {
    recommendations.push('All validation gates passed. Delta design is ready for review.');
  } else {
    gates.forEach(gate => {
      if (!gate.passed) {
        recommendations.push(`Improve ${gate.gate}: ${gate.errors.join(', ') || gate.warnings.join(', ')}`);
      }
    });
  }

  return recommendations;
}

// Run if called directly
if (require.main === module) {
  main();
}

module.exports = {
  validateCompleteness,
  validateApiQuality,
  validateDatabaseQuality,
  validateIntegrationQuality,
  validateSchema,
  calculateOverallScore,
  determineStatus
};
