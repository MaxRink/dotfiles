#!/usr/bin/env node

/**
 * classify-change-type.js
 *
 * Analyzes computed delta to determine change type, complexity score, and quality target.
 *
 * Usage:
 *   node classify-change-type.js --delta <path> --output <path>
 *
 * Exit codes:
 *   0 = Success
 *   1 = Validation error (missing data, invalid format)
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

  if (!params.delta || !params.output) {
    console.error('Usage: node classify-change-type.js --delta <path> --output <path>');
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

// Calculate complexity score
function calculateComplexity(delta) {
  const apiChanges = delta.changes?.api_changes || {};
  const databaseChanges = delta.changes?.database_changes || {};
  const eventChanges = delta.changes?.event_changes || {};
  const stateMachineChanges = delta.changes?.state_machine_changes || {};
  const dependencyChanges = delta.changes?.dependency_changes || {};

  const weights = {
    api_add: 1,
    api_modify: 2,
    api_deprecate: 3,
    db_table_add: 5,
    db_column_add: 2,
    db_index_add: 1,
    event_topic_add: 3,
    event_subscription_add: 2,
    state_new: 4,
    state_transition: 2,
    dependency_add: 3
  };

  const complexity =
    safeLength(apiChanges.endpoints_to_add) * weights.api_add +
    safeLength(apiChanges.endpoints_to_modify) * weights.api_modify +
    safeLength(apiChanges.endpoints_to_deprecate) * weights.api_deprecate +
    safeLength(databaseChanges.tables_to_add) * weights.db_table_add +
    safeLength(databaseChanges.columns_to_add) * weights.db_column_add +
    safeLength(databaseChanges.indexes_to_add) * weights.db_index_add +
    safeLength(eventChanges.topics_to_add) * weights.event_topic_add +
    safeLength(eventChanges.subscriptions_to_add) * weights.event_subscription_add +
    safeLength(stateMachineChanges.new_states) * weights.state_new +
    safeLength(stateMachineChanges.new_transitions) * weights.state_transition +
    safeLength(dependencyChanges.new_internal_dependencies) * weights.dependency_add;

  return complexity;
}

// Determine if change is breaking
function isBreakingChange(delta) {
  const apiChanges = delta.changes?.api_changes || {};

  const hasDeprecations = safeLength(apiChanges.endpoints_to_deprecate) > 0;
  const hasModifications = safeLength(apiChanges.endpoints_to_modify) > 0;

  return hasDeprecations || hasModifications;
}

// Classify change type
function classifyChangeType(complexity, breaking) {
  if (breaking) {
    return 'BREAKING';
  }

  if (complexity < 10) {
    return 'ADDITIVE';
  }

  if (complexity < 30) {
    return 'ENHANCEMENT';
  }

  return 'REFACTORING';
}

// Get quality target based on change type
function getQualityTarget(changeType) {
  const targets = {
    'ADDITIVE': 80,
    'ENHANCEMENT': 75,
    'BREAKING': 70,
    'REFACTORING': 70
  };

  return targets[changeType] || 75;
}

// Get change type description
function getChangeTypeDescription(changeType) {
  const descriptions = {
    'ADDITIVE': 'Safe additions (new endpoints, tables, events) without breaking existing functionality',
    'ENHANCEMENT': 'Moderate complexity additions with multiple new components',
    'BREAKING': 'Changes that modify or deprecate existing APIs - requires careful migration planning',
    'REFACTORING': 'Major architectural changes with high complexity'
  };

  return descriptions[changeType] || 'Unknown change type';
}

// Main execution
function main() {
  const params = parseArgs();

  console.log('🔍 Classifying change type...');
  console.log(`   Delta file: ${params.delta}`);

  // Load delta
  const delta = loadJSON(params.delta);

  // Validate delta structure
  if (!delta.changes) {
    console.error('❌ Invalid delta format: missing changes object');
    process.exit(1);
  }

  // Calculate complexity
  const complexity = calculateComplexity(delta);
  const breaking = isBreakingChange(delta);
  const changeType = classifyChangeType(complexity, breaking);
  const qualityTarget = getQualityTarget(changeType);

  // Build classification output
  const classification = {
    classified_at: new Date().toISOString(),
    baseline: delta.baseline,
    requirements: delta.requirements,
    change_type: changeType,
    change_description: getChangeTypeDescription(changeType),
    complexity_score: complexity,
    is_breaking_change: breaking,
    quality_target: qualityTarget,
    change_summary: {
      api: {
        add: safeLength(delta.changes.api_changes?.endpoints_to_add),
        modify: safeLength(delta.changes.api_changes?.endpoints_to_modify),
        deprecate: safeLength(delta.changes.api_changes?.endpoints_to_deprecate)
      },
      database: {
        tables_add: safeLength(delta.changes.database_changes?.tables_to_add),
        columns_add: safeLength(delta.changes.database_changes?.columns_to_add),
        indexes_add: safeLength(delta.changes.database_changes?.indexes_to_add)
      },
      events: {
        topics_add: safeLength(delta.changes.event_changes?.topics_to_add),
        subscriptions_add: safeLength(delta.changes.event_changes?.subscriptions_to_add)
      },
      state_machines: {
        states_add: safeLength(delta.changes.state_machine_changes?.new_states),
        transitions_add: safeLength(delta.changes.state_machine_changes?.new_transitions)
      },
      dependencies: {
        services_add: safeLength(delta.changes.dependency_changes?.new_internal_dependencies)
      }
    }
  };

  // Write output
  const outputDir = path.dirname(params.output);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  fs.writeFileSync(params.output, JSON.stringify(classification, null, 2), 'utf-8');

  // Summary
  console.log('✅ Classification complete');
  console.log(`   Change Type: ${changeType}`);
  console.log(`   Breaking: ${breaking ? 'YES ⚠️' : 'NO'}`);
  console.log(`   Complexity: ${complexity}`);
  console.log(`   Quality Target: ≥${qualityTarget}/100`);
  console.log(`   Description: ${getChangeTypeDescription(changeType)}`);
  console.log(`   Output: ${params.output}`);

  process.exit(0);
}

// Run if called directly
if (require.main === module) {
  main();
}

module.exports = {
  calculateComplexity,
  isBreakingChange,
  classifyChangeType,
  getQualityTarget,
  getChangeTypeDescription
};
