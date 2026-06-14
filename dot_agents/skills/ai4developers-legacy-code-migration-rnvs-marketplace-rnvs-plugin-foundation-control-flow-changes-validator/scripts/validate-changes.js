#!/usr/bin/env node
/**
 * Validate Control Flow Changes
 *
 * Performs 5-gate validation on control flow changes with transparent
 * heuristic scoring.
 *
 * Input:
 *   --delta: computed-control-flow-delta.json
 *   --classification: classification.json
 *   --output: Output file path for changes-quality-report.json
 *
 * Output: changes-quality-report.json with 5-gate validation results
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

// Gate 1: Completeness (30%)
function validateCompleteness(delta) {
  const errors = [];
  const warnings = [];
  let score = 0;
  const maxScore = 30;

  const changes = delta.changes || {};

  // Check if at least one delta category has data
  const hasSequences = (changes.sequences_to_add?.length || 0) + (changes.sequences_to_modify?.length || 0) > 0;
  const hasActivities = (changes.activities_to_add?.length || 0) + (changes.activities_to_modify?.length || 0) > 0;
  const hasSagas = (changes.sagas_to_add?.length || 0) > 0;
  const hasEventFlows = (changes.event_flows_to_modify?.length || 0) > 0;

  const populatedCategories = [hasSequences, hasActivities, hasSagas, hasEventFlows].filter(Boolean).length;

  if (populatedCategories === 0) {
    errors.push('No control flow changes detected in any category');
    score = 0;
  } else {
    // Base score for having some data
    score = 10;

    // Check baseline information
    if (delta.baseline?.source) {
      score += 5;
    } else {
      warnings.push('Missing baseline source information');
    }

    // Check requirements linkage
    if (delta.requirements?.control_flow_mapping && delta.requirements?.microservice_changes) {
      score += 5;
    } else {
      warnings.push('Missing requirements linkage');
    }

    // Bonus for each populated category
    score += Math.min(populatedCategories * 2.5, 10);
  }

  return {
    gate_name: 'Completeness',
    weight: 30,
    score: Math.min(score, maxScore),
    max_score: maxScore,
    passed: score >= 20,
    errors,
    warnings,
    details: {
      categories_populated: populatedCategories,
      has_sequences: hasSequences,
      has_activities: hasActivities,
      has_sagas: hasSagas,
      has_event_flows: hasEventFlows
    }
  };
}

// Gate 2: PlantUML Quality (30%)
function validatePlantUMLQuality(delta) {
  const errors = [];
  const warnings = [];
  let score = 0;
  const maxScore = 30;

  const changes = delta.changes || {};

  // Check sequence diagrams
  const sequences = [...(changes.sequences_to_add || []), ...(changes.sequences_to_modify || [])];
  let sequenceScore = 0;

  for (const seq of sequences) {
    let itemScore = 0;

    // Check for diagram name
    if (seq.diagram_name) {
      itemScore += 2;
    } else {
      errors.push(`Sequence missing diagram_name: ${JSON.stringify(seq).substring(0, 50)}`);
    }

    // Check for use case or modifications
    if (seq.use_case || seq.modifications) {
      itemScore += 2;
    } else {
      warnings.push(`Sequence missing use_case or modifications: ${seq.diagram_name}`);
    }

    // Check for rationale
    if (seq.rationale) {
      itemScore += 2;
    } else {
      warnings.push(`Sequence missing rationale: ${seq.diagram_name}`);
    }

    // Check for source_change
    if (seq.source_change || seq.modifications?.rationale) {
      itemScore += 1;
    } else {
      warnings.push(`Sequence missing source traceability: ${seq.diagram_name}`);
    }

    sequenceScore += itemScore;
  }

  // Check activity diagrams
  const activities = [...(changes.activities_to_add || []), ...(changes.activities_to_modify || [])];
  let activityScore = 0;

  for (const act of activities) {
    let itemScore = 0;

    if (act.diagram_name) itemScore += 2;
    if (act.operation) itemScore += 2;
    if (act.rationale) itemScore += 2;
    if (act.source_change) itemScore += 1;

    activityScore += itemScore;
  }

  // Check sagas
  const sagas = changes.sagas_to_add || [];
  let sagaScore = 0;

  for (const saga of sagas) {
    let itemScore = 0;

    if (saga.diagram_name) itemScore += 2;
    if (saga.saga_name) itemScore += 2;
    if (saga.rationale) itemScore += 2;
    if (saga.compensation_required !== undefined) itemScore += 1;

    sagaScore += itemScore;
  }

  // Check event flows
  const eventFlows = changes.event_flows_to_modify || [];
  let eventScore = 0;

  for (const ef of eventFlows) {
    let itemScore = 0;

    if (ef.diagram_name) itemScore += 2;
    if (ef.new_topics?.length > 0 || ef.new_subscriptions?.length > 0) itemScore += 2;
    if (ef.rationale) itemScore += 2;
    if (ef.source_change) itemScore += 1;

    eventScore += itemScore;
  }

  // Normalize scores
  const totalItems = sequences.length + activities.length + sagas.length + eventFlows.length;
  const totalItemScore = sequenceScore + activityScore + sagaScore + eventScore;
  const maxItemScore = totalItems * 7;  // 7 points per item max

  if (totalItems === 0) {
    score = 15;  // Default score if no items to validate
    warnings.push('No diagram changes to validate');
  } else {
    score = Math.round((totalItemScore / maxItemScore) * maxScore);
  }

  return {
    gate_name: 'PlantUML Quality',
    weight: 30,
    score: Math.min(score, maxScore),
    max_score: maxScore,
    passed: score >= 20,
    errors,
    warnings,
    details: {
      sequences_checked: sequences.length,
      activities_checked: activities.length,
      sagas_checked: sagas.length,
      event_flows_checked: eventFlows.length,
      sequence_score: sequenceScore,
      activity_score: activityScore,
      saga_score: sagaScore,
      event_score: eventScore
    }
  };
}

// Gate 3: Documentation Quality (20%)
function validateDocumentation(delta) {
  const errors = [];
  const warnings = [];
  let score = 0;
  const maxScore = 20;

  const changes = delta.changes || {};

  // Check that all changes have rationale
  let rationaleCount = 0;
  let totalChanges = 0;

  const allChanges = [
    ...(changes.sequences_to_add || []),
    ...(changes.sequences_to_modify || []),
    ...(changes.activities_to_add || []),
    ...(changes.activities_to_modify || []),
    ...(changes.sagas_to_add || []),
    ...(changes.event_flows_to_modify || [])
  ];

  for (const change of allChanges) {
    totalChanges++;
    if (change.rationale || change.modifications?.rationale) {
      rationaleCount++;
    }
  }

  if (totalChanges === 0) {
    score = 10;  // Default if no changes
    warnings.push('No changes to validate documentation');
  } else {
    // Rationale coverage
    const rationaleCoverage = rationaleCount / totalChanges;
    score += Math.round(rationaleCoverage * 15);

    if (rationaleCoverage < 1) {
      warnings.push(`Only ${Math.round(rationaleCoverage * 100)}% of changes have rationale`);
    }

    // Baseline documentation
    if (delta.baseline?.assumption) {
      score += 5;
    } else {
      warnings.push('Missing baseline assumption documentation');
    }
  }

  return {
    gate_name: 'Documentation Quality',
    weight: 20,
    score: Math.min(score, maxScore),
    max_score: maxScore,
    passed: score >= 12,
    errors,
    warnings,
    details: {
      total_changes: totalChanges,
      changes_with_rationale: rationaleCount,
      rationale_coverage: totalChanges > 0 ? `${Math.round(rationaleCount / totalChanges * 100)}%` : 'N/A'
    }
  };
}

// Gate 4: Traceability (10%)
function validateTraceability(delta) {
  const errors = [];
  const warnings = [];
  let score = 0;
  const maxScore = 10;

  const changes = delta.changes || {};

  // Check source_change linkage to Phase 7.1
  let sourceCount = 0;
  let totalChanges = 0;

  const allChanges = [
    ...(changes.sequences_to_add || []),
    ...(changes.sequences_to_modify || []),
    ...(changes.activities_to_add || []),
    ...(changes.sagas_to_add || []),
    ...(changes.event_flows_to_modify || [])
  ];

  for (const change of allChanges) {
    totalChanges++;
    if (change.source_change || change.modifications?.source_change) {
      sourceCount++;
    }
  }

  if (totalChanges === 0) {
    score = 5;  // Default if no changes
    warnings.push('No changes to validate traceability');
  } else {
    const sourceCoverage = sourceCount / totalChanges;
    score += Math.round(sourceCoverage * 7);

    if (sourceCoverage < 1) {
      warnings.push(`Only ${Math.round(sourceCoverage * 100)}% of changes have source traceability`);
    }
  }

  // Check requirements linkage
  if (delta.requirements?.microservice_changes) {
    score += 3;
  } else {
    warnings.push('Missing link to Phase 7.1 microservice changes');
  }

  return {
    gate_name: 'Traceability',
    weight: 10,
    score: Math.min(score, maxScore),
    max_score: maxScore,
    passed: score >= 6,
    errors,
    warnings,
    details: {
      total_changes: totalChanges,
      changes_with_source: sourceCount,
      source_coverage: totalChanges > 0 ? `${Math.round(sourceCount / totalChanges * 100)}%` : 'N/A',
      has_requirements_link: !!delta.requirements?.microservice_changes
    }
  };
}

// Gate 5: Schema Validation (10%)
function validateSchema(delta) {
  const errors = [];
  const warnings = [];
  let score = 0;
  const maxScore = 10;

  // Check required top-level fields
  if (delta.baseline) {
    score += 2;
  } else {
    errors.push('Missing baseline section');
  }

  if (delta.requirements) {
    score += 2;
  } else {
    errors.push('Missing requirements section');
  }

  if (delta.changes) {
    score += 3;
  } else {
    errors.push('Missing changes section');
  }

  // Check changes structure
  if (delta.changes) {
    const expectedArrays = [
      'sequences_to_add',
      'sequences_to_modify',
      'activities_to_add',
      'activities_to_modify',
      'sagas_to_add',
      'event_flows_to_modify'
    ];

    let validArrays = 0;
    for (const arr of expectedArrays) {
      if (Array.isArray(delta.changes[arr])) {
        validArrays++;
      }
    }

    if (validArrays === expectedArrays.length) {
      score += 3;
    } else {
      warnings.push(`Only ${validArrays}/${expectedArrays.length} expected arrays present`);
      score += Math.round((validArrays / expectedArrays.length) * 3);
    }
  }

  return {
    gate_name: 'Schema Validation',
    weight: 10,
    score: Math.min(score, maxScore),
    max_score: maxScore,
    passed: score >= 6,
    errors,
    warnings,
    details: {
      has_baseline: !!delta.baseline,
      has_requirements: !!delta.requirements,
      has_changes: !!delta.changes
    }
  };
}

// Generate recommendations based on validation results
function generateRecommendations(gates) {
  const recommendations = [];

  for (const gate of gates) {
    if (!gate.passed) {
      switch (gate.gate_name) {
        case 'Completeness':
          recommendations.push('Add more control flow changes to cover the microservice modifications');
          break;
        case 'PlantUML Quality':
          recommendations.push('Ensure all diagram entries have diagram_name, use_case/modifications, and rationale');
          break;
        case 'Documentation Quality':
          recommendations.push('Add rationale explaining WHY each control flow change is needed');
          break;
        case 'Traceability':
          recommendations.push('Add source_change field linking each change to Phase 7.1 modifications');
          break;
        case 'Schema Validation':
          recommendations.push('Ensure delta JSON has baseline, requirements, and changes sections');
          break;
      }
    }

    // Add specific recommendations from warnings
    for (const warning of gate.warnings.slice(0, 2)) {
      recommendations.push(`[${gate.gate_name}] ${warning}`);
    }
  }

  return recommendations.slice(0, 10);  // Top 10 recommendations
}

// Main function
function main() {
  const args = parseArgs();

  // Validate arguments
  if (!args.delta || !args.classification || !args.output) {
    console.error('Usage: validate-changes.js --delta <path> --classification <path> --output <path>');
    process.exit(2);
  }

  // Read input files
  let delta, classification;

  try {
    delta = JSON.parse(fs.readFileSync(args.delta, 'utf8'));
  } catch (e) {
    console.error(`Error reading delta file: ${e.message}`);
    process.exit(2);
  }

  try {
    classification = JSON.parse(fs.readFileSync(args.classification, 'utf8'));
  } catch (e) {
    console.error(`Error reading classification file: ${e.message}`);
    process.exit(2);
  }

  // Run all 5 gates
  const gates = [
    validateCompleteness(delta),
    validatePlantUMLQuality(delta),
    validateDocumentation(delta),
    validateTraceability(delta),
    validateSchema(delta)
  ];

  // Calculate overall score
  const overallScore = gates.reduce((sum, gate) => sum + gate.score, 0);
  const gatesPassed = gates.filter(g => g.passed).length;

  // Determine status based on quality target
  const qualityTarget = classification.quality_target || 75;
  let status;

  if (overallScore >= qualityTarget) {
    status = 'COMPLETE';
  } else if (overallScore >= qualityTarget - 15) {
    status = 'PARTIAL';
  } else {
    status = 'INCOMPLETE';
  }

  // Collect all errors and warnings
  const allErrors = gates.flatMap(g => g.errors);
  const allWarnings = gates.flatMap(g => g.warnings);

  // Generate recommendations
  const recommendations = generateRecommendations(gates);

  // Build quality report
  const report = {
    overall_status: status,
    overall_quality_score: overallScore,
    quality_target: qualityTarget,
    gates_passed: gatesPassed,
    total_gates: 5,
    validation_gates: gates,
    errors: allErrors,
    warnings: allWarnings,
    recommendations,
    validated_at: new Date().toISOString()
  };

  // Write output
  try {
    const outputDir = path.dirname(args.output);
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    fs.writeFileSync(args.output, JSON.stringify(report, null, 2));
    console.log(`✅ Validation complete: ${args.output}`);
  } catch (e) {
    console.error(`Error writing output file: ${e.message}`);
    process.exit(2);
  }

  // Display summary
  console.log(`   Status: ${status}`);
  console.log(`   Quality Score: ${overallScore}/${100}`);
  console.log(`   Quality Target: ${qualityTarget}`);
  console.log(`   Gates Passed: ${gatesPassed}/5`);

  // Exit code based on status
  if (status === 'COMPLETE') {
    process.exit(0);
  } else {
    process.exit(1);
  }
}

main();
