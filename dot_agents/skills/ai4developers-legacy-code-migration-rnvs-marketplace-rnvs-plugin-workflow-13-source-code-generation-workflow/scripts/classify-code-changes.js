#!/usr/bin/env node

/**
 * classify-code-changes.js
 *
 * Analyzes computed code delta to determine change type, complexity score,
 * and quality target. Classifies each file as REUSE/MODIFY/NEW.
 *
 * Usage:
 *   node classify-code-changes.js --delta <path> --output <path>
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
    console.error('Usage: node classify-code-changes.js --delta <path> --output <path>');
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

// Complexity weights for different file types
const COMPLEXITY_WEIGHTS = {
  // NEW files
  new_controller: 5,
  new_service: 4,
  new_repository: 3,
  new_entity: 3,
  new_dto: 1,
  new_event_handler: 4,
  new_config: 2,

  // MODIFY files
  modified_controller: 3,
  modified_service: 2,
  modified_repository: 2,
  modified_entity: 2,

  // Migrations
  migration_create_table: 4,
  migration_add_column: 2,
  migration_add_index: 1,

  // Per-item weights
  endpoint_per: 1,
  method_per: 1,
  column_per: 0.5
};

// Calculate complexity score
function calculateComplexity(delta) {
  let complexity = 0;

  // NEW files
  for (const file of safeArray(delta.files_to_create)) {
    switch (file.type) {
      case 'controller':
        complexity += COMPLEXITY_WEIGHTS.new_controller;
        complexity += safeLength(file.endpoints) * COMPLEXITY_WEIGHTS.endpoint_per;
        break;
      case 'service':
        complexity += COMPLEXITY_WEIGHTS.new_service;
        break;
      case 'repository':
        complexity += COMPLEXITY_WEIGHTS.new_repository;
        break;
      case 'entity':
        complexity += COMPLEXITY_WEIGHTS.new_entity;
        complexity += safeLength(file.columns) * COMPLEXITY_WEIGHTS.column_per;
        break;
      case 'dto':
        complexity += COMPLEXITY_WEIGHTS.new_dto;
        break;
      case 'event_handler':
        complexity += COMPLEXITY_WEIGHTS.new_event_handler;
        break;
      case 'config':
        complexity += COMPLEXITY_WEIGHTS.new_config;
        break;
      default:
        complexity += 2; // Default weight for unknown types
    }
  }

  // MODIFY files
  for (const file of safeArray(delta.files_to_modify)) {
    switch (file.type) {
      case 'controller':
        complexity += COMPLEXITY_WEIGHTS.modified_controller;
        complexity += safeLength(file.modifications) * COMPLEXITY_WEIGHTS.method_per;
        break;
      case 'service':
        complexity += COMPLEXITY_WEIGHTS.modified_service;
        complexity += safeLength(file.modifications) * COMPLEXITY_WEIGHTS.method_per;
        break;
      case 'repository':
        complexity += COMPLEXITY_WEIGHTS.modified_repository;
        break;
      case 'entity':
        complexity += COMPLEXITY_WEIGHTS.modified_entity;
        complexity += safeLength(file.modifications) * COMPLEXITY_WEIGHTS.column_per;
        break;
      default:
        complexity += 1;
    }
  }

  // Migrations
  for (const migration of safeArray(delta.migrations_needed)) {
    if (safeLength(migration.tables) > 0) {
      complexity += safeLength(migration.tables) * COMPLEXITY_WEIGHTS.migration_create_table;
    }
    if (safeLength(migration.columns) > 0) {
      complexity += safeLength(migration.columns) * COMPLEXITY_WEIGHTS.migration_add_column;
    }
    if (safeLength(migration.indexes) > 0) {
      complexity += safeLength(migration.indexes) * COMPLEXITY_WEIGHTS.migration_add_index;
    }
  }

  return Math.round(complexity);
}

// Classify change type based on complexity
function classifyChangeType(complexity, hasModifications) {
  if (complexity < 10) {
    return 'ADDITIVE';
  }
  if (complexity < 25) {
    return 'ENHANCEMENT';
  }
  if (complexity < 50) {
    return 'MAJOR_ENHANCEMENT';
  }
  return 'REFACTORING';
}

// Get quality target based on change type
function getQualityTarget(changeType) {
  const targets = {
    'ADDITIVE': 80,
    'ENHANCEMENT': 75,
    'MAJOR_ENHANCEMENT': 70,
    'REFACTORING': 70
  };
  return targets[changeType] || 75;
}

// Get change type description
function getChangeTypeDescription(changeType) {
  const descriptions = {
    'ADDITIVE': 'Simple additions - new files without modifying existing code',
    'ENHANCEMENT': 'Moderate additions with some modifications to existing files',
    'MAJOR_ENHANCEMENT': 'Significant changes with multiple new files and modifications',
    'REFACTORING': 'Large-scale changes requiring careful testing and validation'
  };
  return descriptions[changeType] || 'Unknown change type';
}

// Classify individual files
function classifyFiles(delta) {
  const classifications = {
    NEW: [],
    MODIFY: [],
    REUSE: [] // Files that exist but don't need changes (not included in delta)
  };

  for (const file of safeArray(delta.files_to_create)) {
    classifications.NEW.push({
      path: file.path,
      type: file.type,
      reason: `New ${file.type} required for feature`,
      estimated_lines: estimateLines(file),
      source_requirements: file.source_requirements || []
    });
  }

  for (const file of safeArray(delta.files_to_modify)) {
    classifications.MODIFY.push({
      path: file.path,
      type: file.type,
      reason: `Existing ${file.type} needs ${safeLength(file.modifications)} modification(s)`,
      modifications: file.modifications,
      estimated_changes: safeLength(file.modifications)
    });
  }

  return classifications;
}

// Estimate lines of code for new files
function estimateLines(file) {
  const estimates = {
    controller: 100 + safeLength(file.endpoints) * 30,
    service: 80 + safeLength(file.methods) * 20,
    repository: 30,
    entity: 50 + safeLength(file.columns) * 5,
    dto: 30,
    event_handler: 60,
    config: 40
  };
  return estimates[file.type] || 50;
}

// Main execution
function main() {
  const params = parseArgs();

  console.log('🔍 Classifying code changes...');
  console.log(`   Delta file: ${params.delta}`);

  // Load delta
  const delta = loadJSON(params.delta);

  // Validate delta structure
  if (!delta.files_to_create && !delta.files_to_modify) {
    console.error('❌ Invalid delta format: missing files_to_create or files_to_modify');
    process.exit(1);
  }

  // Calculate complexity
  const complexity = calculateComplexity(delta);
  const hasModifications = safeLength(delta.files_to_modify) > 0;
  const changeType = classifyChangeType(complexity, hasModifications);
  const qualityTarget = getQualityTarget(changeType);

  // Classify individual files
  const fileClassifications = classifyFiles(delta);

  // Build classification output
  const classification = {
    classified_at: new Date().toISOString(),
    baseline: delta.baseline,
    design: delta.design,
    change_type: changeType,
    change_description: getChangeTypeDescription(changeType),
    complexity_score: complexity,
    quality_target: qualityTarget,
    summary: {
      files_to_create: safeLength(delta.files_to_create),
      files_to_modify: safeLength(delta.files_to_modify),
      migrations_needed: safeLength(delta.migrations_needed),
      total_estimated_lines: fileClassifications.NEW.reduce((sum, f) => sum + f.estimated_lines, 0),
      total_modifications: fileClassifications.MODIFY.reduce((sum, f) => sum + f.estimated_changes, 0)
    },
    file_breakdown: {
      by_type: {
        controllers: {
          new: safeArray(delta.files_to_create).filter(f => f.type === 'controller').length,
          modify: safeArray(delta.files_to_modify).filter(f => f.type === 'controller').length
        },
        services: {
          new: safeArray(delta.files_to_create).filter(f => f.type === 'service').length,
          modify: safeArray(delta.files_to_modify).filter(f => f.type === 'service').length
        },
        repositories: {
          new: safeArray(delta.files_to_create).filter(f => f.type === 'repository').length,
          modify: safeArray(delta.files_to_modify).filter(f => f.type === 'repository').length
        },
        entities: {
          new: safeArray(delta.files_to_create).filter(f => f.type === 'entity').length,
          modify: safeArray(delta.files_to_modify).filter(f => f.type === 'entity').length
        },
        dtos: {
          new: safeArray(delta.files_to_create).filter(f => f.type === 'dto').length,
          modify: 0
        },
        event_handlers: {
          new: safeArray(delta.files_to_create).filter(f => f.type === 'event_handler').length,
          modify: safeArray(delta.files_to_modify).filter(f => f.type === 'event_handler').length
        }
      }
    },
    classifications: fileClassifications
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
  console.log(`   Complexity Score: ${complexity}`);
  console.log(`   Quality Target: ≥${qualityTarget}/100`);
  console.log(`   Files to Create: ${classification.summary.files_to_create}`);
  console.log(`   Files to Modify: ${classification.summary.files_to_modify}`);
  console.log(`   Estimated Lines: ${classification.summary.total_estimated_lines}`);
  console.log(`   Output: ${params.output}`);

  process.exit(0);
}

// Run if called directly
if (require.main === module) {
  main();
}

module.exports = {
  calculateComplexity,
  classifyChangeType,
  getQualityTarget,
  classifyFiles,
  COMPLEXITY_WEIGHTS
};
