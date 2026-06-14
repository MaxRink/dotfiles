#!/usr/bin/env node

/**
 * validate-code-changes.js
 *
 * Validates that all Phase 7.1 design changes are covered by code files.
 * Checks API coverage, database coverage, and overall completeness.
 *
 * Usage:
 *   node validate-code-changes.js --delta <path> --classification <path> --phase7.1 <path> --output <path>
 *
 * Exit codes:
 *   0 = Validation passed (COMPLETE)
 *   1 = Validation incomplete (warnings but can proceed)
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

  if (!params.delta || !params.classification || !params['phase7.1'] || !params.output) {
    console.error('Usage: node validate-code-changes.js --delta <path> --classification <path> --phase7.1 <path> --output <path>');
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

// Safe array access
function safeArray(value) {
  return Array.isArray(value) ? value : [];
}

// Safe length
function safeLength(value) {
  return Array.isArray(value) ? value.length : 0;
}

// Gate 1: Completeness - All Phase 7.1 changes mapped to code
function validateCompleteness(delta, phase7_1) {
  const results = {
    gate: 'COMPLETENESS',
    passed: true,
    score: 100,
    findings: []
  };

  // Check API changes coverage
  const endpointsToAdd = safeArray(phase7_1.changes?.api_changes?.endpoints_to_add);
  const endpointsToModify = safeArray(phase7_1.changes?.api_changes?.endpoints_to_modify);
  const allEndpoints = [...endpointsToAdd, ...endpointsToModify];

  const codedEndpoints = new Set();
  for (const file of safeArray(delta.files_to_create)) {
    if (file.type === 'controller') {
      for (const endpoint of safeArray(file.endpoints)) {
        codedEndpoints.add(`${endpoint.method}:${endpoint.path}`);
      }
    }
  }
  for (const file of safeArray(delta.files_to_modify)) {
    if (file.type === 'controller') {
      for (const mod of safeArray(file.modifications)) {
        codedEndpoints.add(`${mod.method}:${mod.path}`);
      }
    }
  }

  const uncoveredEndpoints = allEndpoints.filter(e =>
    !codedEndpoints.has(`${e.method}:${e.path}`)
  );

  if (uncoveredEndpoints.length > 0) {
    results.passed = false;
    results.score -= 10 * uncoveredEndpoints.length;
    results.findings.push({
      type: 'UNCOVERED_ENDPOINTS',
      severity: 'ERROR',
      count: uncoveredEndpoints.length,
      details: uncoveredEndpoints.map(e => `${e.method} ${e.path}`)
    });
  }

  // Check database changes coverage
  const tablesToAdd = safeArray(phase7_1.changes?.database_changes?.tables_to_add);
  const migrations = safeArray(delta.migrations_needed);
  const migratedTables = new Set();
  for (const m of migrations) {
    for (const t of safeArray(m.tables)) {
      migratedTables.add(t.table_name || t.name);
    }
  }

  const uncoveredTables = tablesToAdd.filter(t =>
    !migratedTables.has(t.table_name || t.name)
  );

  if (uncoveredTables.length > 0) {
    results.passed = false;
    results.score -= 15 * uncoveredTables.length;
    results.findings.push({
      type: 'UNCOVERED_TABLES',
      severity: 'ERROR',
      count: uncoveredTables.length,
      details: uncoveredTables.map(t => t.table_name || t.name)
    });
  }

  results.score = Math.max(0, results.score);
  return results;
}

// Gate 2: API Coverage - Controllers exist for all endpoints
function validateApiCoverage(delta, phase7_1) {
  const results = {
    gate: 'API_COVERAGE',
    passed: true,
    score: 100,
    findings: []
  };

  const endpointsToAdd = safeArray(phase7_1.changes?.api_changes?.endpoints_to_add);

  // Check that new endpoints have corresponding controllers
  const controllerPaths = new Set(
    safeArray(delta.files_to_create)
      .filter(f => f.type === 'controller')
      .flatMap(f => safeArray(f.endpoints).map(e => e.path))
  );

  const modifiedPaths = new Set(
    safeArray(delta.files_to_modify)
      .filter(f => f.type === 'controller')
      .flatMap(f => safeArray(f.modifications).map(m => m.path))
  );

  const allCoveredPaths = new Set([...controllerPaths, ...modifiedPaths]);

  const missingControllers = endpointsToAdd.filter(e =>
    !allCoveredPaths.has(e.path)
  );

  if (missingControllers.length > 0) {
    results.passed = false;
    results.score -= 20 * missingControllers.length;
    results.findings.push({
      type: 'MISSING_CONTROLLERS',
      severity: 'ERROR',
      count: missingControllers.length,
      details: missingControllers.map(e => `${e.method} ${e.path} - No controller mapped`)
    });
  }

  // Check that DTOs are created for endpoints with request/response schemas
  const endpointsWithSchemas = endpointsToAdd.filter(e =>
    e.request_schema || e.response_schema
  );

  const dtoFiles = safeArray(delta.files_to_create).filter(f => f.type === 'dto');

  if (endpointsWithSchemas.length > 0 && dtoFiles.length === 0) {
    results.score -= 10;
    results.findings.push({
      type: 'MISSING_DTOS',
      severity: 'WARNING',
      count: endpointsWithSchemas.length,
      details: ['Endpoints have schemas but no DTOs were generated']
    });
  }

  results.score = Math.max(0, results.score);
  return results;
}

// Gate 3: Database Coverage - Migrations exist for schema changes
function validateDatabaseCoverage(delta, phase7_1) {
  const results = {
    gate: 'DATABASE_COVERAGE',
    passed: true,
    score: 100,
    findings: []
  };

  const tablesToAdd = safeArray(phase7_1.changes?.database_changes?.tables_to_add);
  const columnsToAdd = safeArray(phase7_1.changes?.database_changes?.columns_to_add);
  const indexesToAdd = safeArray(phase7_1.changes?.database_changes?.indexes_to_add);

  const migrations = safeArray(delta.migrations_needed);

  // Check tables
  if (tablesToAdd.length > 0 && migrations.length === 0) {
    results.passed = false;
    results.score -= 30;
    results.findings.push({
      type: 'NO_MIGRATIONS',
      severity: 'ERROR',
      count: tablesToAdd.length,
      details: [`${tablesToAdd.length} tables need to be created but no migrations defined`]
    });
  }

  // Check that entity files exist for new tables
  const entityFiles = safeArray(delta.files_to_create).filter(f => f.type === 'entity');

  if (tablesToAdd.length > entityFiles.length) {
    results.score -= 10;
    results.findings.push({
      type: 'MISSING_ENTITIES',
      severity: 'WARNING',
      count: tablesToAdd.length - entityFiles.length,
      details: [`${tablesToAdd.length} tables but only ${entityFiles.length} entity files`]
    });
  }

  // Check that repository files exist for new entities
  const repoFiles = safeArray(delta.files_to_create).filter(f => f.type === 'repository');

  if (entityFiles.length > repoFiles.length) {
    results.score -= 5;
    results.findings.push({
      type: 'MISSING_REPOSITORIES',
      severity: 'WARNING',
      count: entityFiles.length - repoFiles.length,
      details: [`${entityFiles.length} entities but only ${repoFiles.length} repository files`]
    });
  }

  results.score = Math.max(0, results.score);
  return results;
}

// Gate 4: Source Traceability - Changes have RNVS source references
function validateSourceTraceability(delta, phase7_1) {
  const results = {
    gate: 'SOURCE_TRACEABILITY',
    passed: true,
    score: 100,
    findings: []
  };

  const filesWithoutSource = [];

  for (const file of safeArray(delta.files_to_create)) {
    if (safeLength(file.source_requirements) === 0) {
      filesWithoutSource.push(file.path);
    }
  }

  if (filesWithoutSource.length > 0) {
    results.score -= 5 * filesWithoutSource.length;
    results.findings.push({
      type: 'MISSING_SOURCE_REFERENCE',
      severity: 'WARNING',
      count: filesWithoutSource.length,
      details: filesWithoutSource.slice(0, 5) // Show first 5
    });
  }

  results.score = Math.max(0, results.score);
  return results;
}

// Gate 5: Event Coverage - Handlers exist for Kafka topics
function validateEventCoverage(delta, phase7_1) {
  const results = {
    gate: 'EVENT_COVERAGE',
    passed: true,
    score: 100,
    findings: []
  };

  const topicsToAdd = safeArray(phase7_1.changes?.event_changes?.topics_to_add);
  const subscriptionsToAdd = safeArray(phase7_1.changes?.event_changes?.subscriptions_to_add);

  const handlerFiles = safeArray(delta.files_to_create).filter(f => f.type === 'event_handler');

  // Check that subscriptions have handlers
  if (subscriptionsToAdd.length > 0 && handlerFiles.length === 0) {
    results.score -= 20;
    results.findings.push({
      type: 'MISSING_EVENT_HANDLERS',
      severity: 'WARNING',
      count: subscriptionsToAdd.length,
      details: [`${subscriptionsToAdd.length} subscriptions but no event handlers`]
    });
  }

  results.score = Math.max(0, results.score);
  return results;
}

// Calculate overall quality score
function calculateOverallScore(gateResults, qualityTarget) {
  const totalScore = gateResults.reduce((sum, g) => sum + g.score, 0);
  const averageScore = Math.round(totalScore / gateResults.length);

  return {
    overall_score: averageScore,
    quality_target: qualityTarget,
    passed: averageScore >= qualityTarget,
    gates_passed: gateResults.filter(g => g.passed).length,
    total_gates: gateResults.length
  };
}

// Generate recommendations
function generateRecommendations(gateResults) {
  const recommendations = [];

  for (const gate of gateResults) {
    for (const finding of gate.findings) {
      if (finding.severity === 'ERROR') {
        recommendations.push(`Fix ${finding.type}: ${finding.details[0] || finding.count + ' issues found'}`);
      } else if (finding.severity === 'WARNING') {
        recommendations.push(`Consider: ${finding.type} - ${finding.count} items may need attention`);
      }
    }
  }

  return recommendations;
}

// Main execution
function main() {
  const params = parseArgs();

  console.log('🔍 Validating code changes...');
  console.log(`   Delta: ${params.delta}`);
  console.log(`   Classification: ${params.classification}`);
  console.log(`   Phase 7.1 Design: ${params['phase7.1']}`);

  // Load inputs
  const delta = loadJSON(params.delta);
  const classification = loadJSON(params.classification);
  const phase7_1 = loadJSON(params['phase7.1']);

  const qualityTarget = classification.quality_target || 75;

  // Run validation gates
  const gateResults = [
    validateCompleteness(delta, phase7_1),
    validateApiCoverage(delta, phase7_1),
    validateDatabaseCoverage(delta, phase7_1),
    validateSourceTraceability(delta, phase7_1),
    validateEventCoverage(delta, phase7_1)
  ];

  // Calculate overall score
  const overallResult = calculateOverallScore(gateResults, qualityTarget);
  const recommendations = generateRecommendations(gateResults);

  // Build validation report
  const report = {
    validated_at: new Date().toISOString(),
    status: overallResult.passed ? 'COMPLETE' : 'INCOMPLETE',
    overall_quality_score: overallResult.overall_score,
    quality_target: overallResult.quality_target,
    passed: overallResult.passed,
    gates_summary: {
      passed: overallResult.gates_passed,
      total: overallResult.total_gates
    },
    gate_results: gateResults,
    recommendations: recommendations,
    next_steps: overallResult.passed
      ? ['Proceed with code generation using computed delta']
      : ['Address ERROR findings before proceeding', 'Review WARNING findings for completeness']
  };

  // Write output
  const outputDir = path.dirname(params.output);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  fs.writeFileSync(params.output, JSON.stringify(report, null, 2), 'utf-8');

  // Summary
  console.log(`✅ Validation complete: ${report.status}`);
  console.log(`   Overall Score: ${overallResult.overall_score}/100`);
  console.log(`   Quality Target: ≥${qualityTarget}/100`);
  console.log(`   Gates Passed: ${overallResult.gates_passed}/${overallResult.total_gates}`);

  if (recommendations.length > 0) {
    console.log('\n   Recommendations:');
    recommendations.slice(0, 3).forEach(r => console.log(`   - ${r}`));
  }

  console.log(`\n   Output: ${params.output}`);

  // Exit with appropriate code
  if (overallResult.passed) {
    process.exit(0);
  } else {
    process.exit(1);
  }
}

// Run if called directly
if (require.main === module) {
  main();
}

module.exports = {
  validateCompleteness,
  validateApiCoverage,
  validateDatabaseCoverage,
  validateSourceTraceability,
  validateEventCoverage,
  calculateOverallScore,
  generateRecommendations
};
