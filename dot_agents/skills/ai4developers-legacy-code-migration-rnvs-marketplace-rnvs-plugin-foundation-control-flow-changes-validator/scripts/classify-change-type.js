#!/usr/bin/env node
/**
 * Classify Control Flow Change Type
 *
 * Analyzes computed control flow delta to determine change type,
 * complexity score, and quality target.
 *
 * Input:
 *   --delta: computed-control-flow-delta.json
 *   --output: Output file path for classification.json
 *
 * Output: classification.json with change type, complexity, and quality target
 */

const fs = require('fs');
const path = require('path');

// Parse command line arguments
function parseArgs() {
  const args = {};
  for (let i = 2; i < process.argv.length; i += 2) {
    const key = process.argv[i].replace(/^--/, '');
    const value = process.argv[i + 1];
    args[key] = value;
  }
  return args;
}

// Calculate complexity score based on delta changes
function calculateComplexity(delta) {
  const changes = delta.changes || {};

  const complexity =
    (changes.sequences_to_add?.length || 0) * 5 +       // New sequences are complex
    (changes.sequences_to_modify?.length || 0) * 3 +    // Modifications are moderate
    (changes.activities_to_add?.length || 0) * 4 +      // New activities are complex
    (changes.activities_to_modify?.length || 0) * 2 +   // Activity modifications
    (changes.sagas_to_add?.length || 0) * 6 +           // Sagas are very complex
    (changes.sagas_to_modify?.length || 0) * 4 +        // Saga modifications
    (changes.event_flows_to_modify?.length || 0) * 2;   // Event flow changes

  return complexity;
}

// Determine change type based on delta
function determineChangeType(delta, complexity) {
  const changes = delta.changes || {};

  // Check if there are modifications (ENHANCEMENT type)
  const hasModifications =
    (changes.sequences_to_modify?.length || 0) > 0 ||
    (changes.activities_to_modify?.length || 0) > 0 ||
    (changes.sagas_to_modify?.length || 0) > 0;

  // Check if there are additions only
  const hasAdditionsOnly =
    (changes.sequences_to_add?.length || 0) > 0 ||
    (changes.activities_to_add?.length || 0) > 0 ||
    (changes.sagas_to_add?.length || 0) > 0 ||
    (changes.event_flows_to_modify?.length || 0) > 0;

  if (hasModifications) {
    return 'ENHANCEMENT';  // Modifying existing flows
  } else if (complexity < 10) {
    return 'ADDITIVE';     // Simple additions
  } else if (complexity < 30) {
    return 'ENHANCEMENT';  // Many additions = enhancement
  } else {
    return 'COMPLEX';      // Very complex changes
  }
}

// Determine quality target based on change type
function determineQualityTarget(changeType) {
  switch (changeType) {
    case 'ADDITIVE':
      return 80;  // Higher bar for simple additions
    case 'ENHANCEMENT':
      return 75;  // Moderate bar
    case 'COMPLEX':
      return 70;  // Lower bar for complex changes
    default:
      return 75;
  }
}

// Generate change summary
function generateChangeSummary(delta) {
  const changes = delta.changes || {};

  return {
    sequences_added: changes.sequences_to_add?.length || 0,
    sequences_modified: changes.sequences_to_modify?.length || 0,
    activities_added: changes.activities_to_add?.length || 0,
    activities_modified: changes.activities_to_modify?.length || 0,
    sagas_added: changes.sagas_to_add?.length || 0,
    sagas_modified: changes.sagas_to_modify?.length || 0,
    event_flows_modified: changes.event_flows_to_modify?.length || 0,
    total_diagram_changes:
      (changes.sequences_to_add?.length || 0) +
      (changes.sequences_to_modify?.length || 0) +
      (changes.activities_to_add?.length || 0) +
      (changes.activities_to_modify?.length || 0) +
      (changes.sagas_to_add?.length || 0) +
      (changes.event_flows_to_modify?.length || 0)
  };
}

// Generate change description
function generateChangeDescription(changeType, summary) {
  const parts = [];

  if (summary.sequences_added > 0) {
    parts.push(`${summary.sequences_added} new sequence diagram(s)`);
  }
  if (summary.sequences_modified > 0) {
    parts.push(`${summary.sequences_modified} sequence diagram modification(s)`);
  }
  if (summary.activities_added > 0) {
    parts.push(`${summary.activities_added} new activity diagram(s)`);
  }
  if (summary.sagas_added > 0) {
    parts.push(`${summary.sagas_added} new saga choreography diagram(s)`);
  }
  if (summary.event_flows_modified > 0) {
    parts.push(`${summary.event_flows_modified} event architecture update(s)`);
  }

  if (parts.length === 0) {
    return 'No control flow changes detected';
  }

  return `${changeType} change: ${parts.join(', ')}`;
}

// Main function
function main() {
  const args = parseArgs();

  // Validate arguments
  if (!args.delta || !args.output) {
    console.error('Usage: classify-change-type.js --delta <path> --output <path>');
    process.exit(2);
  }

  // Read delta file
  let delta;
  try {
    delta = JSON.parse(fs.readFileSync(args.delta, 'utf8'));
  } catch (e) {
    console.error(`Error reading delta file: ${e.message}`);
    process.exit(2);
  }

  // Calculate complexity
  const complexity = calculateComplexity(delta);

  // Determine change type
  const changeType = determineChangeType(delta, complexity);

  // Determine quality target
  const qualityTarget = determineQualityTarget(changeType);

  // Generate summary
  const changeSummary = generateChangeSummary(delta);

  // Generate description
  const changeDescription = generateChangeDescription(changeType, changeSummary);

  // Build classification object
  const classification = {
    change_type: changeType,
    change_description: changeDescription,
    complexity_score: complexity,
    is_breaking_change: false,  // Control flows rarely break APIs
    quality_target: qualityTarget,
    change_summary: changeSummary,
    classification_rationale: {
      complexity_breakdown: {
        sequences_added_weight: (delta.changes?.sequences_to_add?.length || 0) * 5,
        sequences_modified_weight: (delta.changes?.sequences_to_modify?.length || 0) * 3,
        activities_added_weight: (delta.changes?.activities_to_add?.length || 0) * 4,
        activities_modified_weight: (delta.changes?.activities_to_modify?.length || 0) * 2,
        sagas_added_weight: (delta.changes?.sagas_to_add?.length || 0) * 6,
        event_flows_modified_weight: (delta.changes?.event_flows_to_modify?.length || 0) * 2
      },
      type_determination: changeType === 'ENHANCEMENT'
        ? 'Modifications to existing flows detected'
        : complexity < 10
          ? 'Simple additions with low complexity'
          : 'Complex additions requiring comprehensive design'
    },
    classified_at: new Date().toISOString()
  };

  // Write output
  try {
    const outputDir = path.dirname(args.output);
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    fs.writeFileSync(args.output, JSON.stringify(classification, null, 2));
    console.log(`✅ Classification complete: ${args.output}`);
  } catch (e) {
    console.error(`Error writing output file: ${e.message}`);
    process.exit(2);
  }

  // Display summary
  console.log(`   Change Type: ${changeType}`);
  console.log(`   Complexity Score: ${complexity}`);
  console.log(`   Quality Target: ≥${qualityTarget}/100`);
  console.log(`   Total Diagram Changes: ${changeSummary.total_diagram_changes}`);

  process.exit(0);
}

main();
