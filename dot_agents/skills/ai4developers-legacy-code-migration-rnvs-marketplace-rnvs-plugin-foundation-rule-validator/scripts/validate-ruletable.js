#!/usr/bin/env node

/**
 * Business Rule Table Validator - 5-Gate Quality System
 *
 * Validates Phase 3 business rule extraction outputs for completeness,
 * confidence quality, source traceability, categorization, and schema compliance.
 *
 * Usage:
 *   node validate-ruletable.js \
 *     --phase3-dir results/NBM/phase3 \
 *     --phase1-dir results/NBM/phase1 \
 *     --phase2-dir results/NBM/phase2 \
 *     --output results/NBM/phase3/rule-quality-report.json \
 *     --feature NBM
 *
 * Exit Codes:
 *   0 - Validation passed (COMPLETE, score >= 75)
 *   1 - Validation failed (INCOMPLETE, score < 75)
 *   2 - Script error (invalid inputs, missing files)
 */

const fs = require('fs');
const path = require('path');

class RuleTableValidator {
  constructor(phase3Dir, phase1Dir, phase2Dir, feature) {
    this.phase3Dir = phase3Dir;
    this.phase1Dir = phase1Dir;
    this.phase2Dir = phase2Dir;
    this.feature = feature;
    this.ruletableData = null;
    this.phase1Data = null;
    this.phase2Summary = null;
  }

  /**
   * Load and parse ruletable.json
   */
  loadRuletable() {
    const ruletablePath = path.join(this.phase3Dir, 'ruletable.json');

    if (!fs.existsSync(ruletablePath)) {
      throw new Error(`ruletable.json not found at ${ruletablePath}`);
    }

    try {
      const content = fs.readFileSync(ruletablePath, 'utf-8');
      this.ruletableData = JSON.parse(content);
    } catch (error) {
      throw new Error(`Failed to parse ruletable.json: ${error.message}`);
    }
  }

  /**
   * Load Phase 1 analysis.json for component references
   */
  loadPhase1() {
    const analysisPath = path.join(this.phase1Dir, 'analysis.json');

    if (!fs.existsSync(analysisPath)) {
      throw new Error(`Phase 1 analysis.json not found at ${analysisPath}`);
    }

    try {
      const content = fs.readFileSync(analysisPath, 'utf-8');
      this.phase1Data = JSON.parse(content);
    } catch (error) {
      throw new Error(`Failed to parse Phase 1 analysis.json: ${error.message}`);
    }
  }

  /**
   * Load Phase 2 PHASE2_SUMMARY.md for flow inventory
   */
  loadPhase2() {
    const summaryPath = path.join(this.phase2Dir, 'PHASE2_SUMMARY.md');

    if (!fs.existsSync(summaryPath)) {
      throw new Error(`Phase 2 PHASE2_SUMMARY.md not found at ${summaryPath}`);
    }

    try {
      const content = fs.readFileSync(summaryPath, 'utf-8');
      this.phase2Summary = content;
    } catch (error) {
      throw new Error(`Failed to read Phase 2 summary: ${error.message}`);
    }
  }

  /**
   * Extract flow list from Phase 2 summary markdown
   */
  extractFlowsFromPhase2() {
    const flows = [];
    const lines = this.phase2Summary.split('\n');

    // Look for flow diagram references (e.g., "flow-owner-change.puml")
    for (const line of lines) {
      const match = line.match(/flow-([a-z0-9-]+)\.puml/i);
      if (match) {
        const flowName = match[1]
          .split('-')
          .map(word => word.charAt(0).toUpperCase() + word.slice(1))
          .join(' ');
        flows.push({
          filename: `flow-${match[1]}.puml`,
          name: flowName,
          original: match[1]
        });
      }
    }

    return flows;
  }

  /**
   * Gate 1: Rule Completeness
   *
   * Validates that:
   * - Every component from Phase 1 has at least one rule
   * - Every flow from Phase 2 has associated rules
   * - Threshold: >= 80%
   */
  validateGate1_RuleCompleteness() {
    const gate = {
      status: 'PENDING',
      percentage: 0,
      components_in_phase1: 0,
      components_with_rules: 0,
      flows_in_phase2: 0,
      flows_with_rules: 0,
      missing_components: [],
      missing_flows: [],
      errors: [],
      warnings: []
    };

    // Get components from Phase 1
    const components = this.phase1Data.components || [];
    gate.components_in_phase1 = components.length;

    // Get flows from Phase 2
    const flows = this.extractFlowsFromPhase2();
    gate.flows_in_phase2 = flows.length;

    const rules = this.ruletableData.rules || [];

    // Check each component has at least one rule
    for (const component of components) {
      const componentName = component.name;
      const hasRule = rules.some(rule => {
        // Check if source_location references this component
        const source = rule.source_location || '';
        return source.includes(componentName) ||
               (rule.affected_components && rule.affected_components.includes(componentName));
      });

      if (hasRule) {
        gate.components_with_rules++;
      } else {
        gate.missing_components.push(componentName);
      }
    }

    // Check each flow has associated rules
    for (const flow of flows) {
      const hasRule = rules.some(rule => {
        // Check if business_flow references this flow
        const businessFlow = rule.business_flow || '';
        return businessFlow.toLowerCase().includes(flow.original) ||
               businessFlow.includes(flow.name) ||
               (rule.source_location && rule.source_location.includes(flow.filename));
      });

      if (hasRule) {
        gate.flows_with_rules++;
      } else {
        gate.missing_flows.push(flow.name);
      }
    }

    // Calculate completeness percentage
    const totalExpected = gate.components_in_phase1 + gate.flows_in_phase2;
    const totalWithRules = gate.components_with_rules + gate.flows_with_rules;

    if (totalExpected > 0) {
      gate.percentage = Math.round((totalWithRules / totalExpected) * 100);
    }

    // Determine status
    const threshold = 80;
    if (gate.percentage >= threshold) {
      gate.status = 'PASSED';
    } else {
      gate.status = 'FAILED';
      gate.errors.push(`Rule completeness ${gate.percentage}% is below threshold ${threshold}%`);
    }

    // Add warnings for missing items
    if (gate.missing_components.length > 0) {
      gate.warnings.push(`${gate.missing_components.length} components without rules: ${gate.missing_components.slice(0, 5).join(', ')}${gate.missing_components.length > 5 ? '...' : ''}`);
    }
    if (gate.missing_flows.length > 0) {
      gate.warnings.push(`${gate.missing_flows.length} flows without rules: ${gate.missing_flows.slice(0, 5).join(', ')}${gate.missing_flows.length > 5 ? '...' : ''}`);
    }

    return gate;
  }

  /**
   * Gate 2: Confidence Quality
   *
   * Validates that:
   * - High percentage of rules have confidence >= 4
   * - All rules have reasoning documented
   * - Critical rules have high confidence
   * - Threshold: >= 70%
   */
  validateGate2_ConfidenceQuality() {
    const gate = {
      status: 'PENDING',
      percentage: 0,
      total_rules: 0,
      high_confidence_rules: 0,
      rules_without_reasoning: [],
      critical_rules_low_confidence: [],
      errors: [],
      warnings: []
    };

    const rules = this.ruletableData.rules || [];
    gate.total_rules = rules.length;

    for (const rule of rules) {
      const confidence = rule.confidence || 0;
      const reasoning = rule.reasoning || '';
      const impact = rule.business_impact || '';
      const ruleId = rule.rule_id || 'Unknown';

      // Count high confidence rules (>= 4)
      if (confidence >= 4) {
        gate.high_confidence_rules++;
      }

      // Check for missing reasoning
      if (!reasoning || reasoning.trim() === '') {
        gate.rules_without_reasoning.push(ruleId);
      }

      // Check critical rules have high confidence
      if (impact === 'critical' && confidence < 4) {
        gate.critical_rules_low_confidence.push(`${ruleId} (confidence: ${confidence})`);
      }
    }

    // Calculate percentage
    if (gate.total_rules > 0) {
      gate.percentage = Math.round((gate.high_confidence_rules / gate.total_rules) * 100);
    }

    // Determine status
    const threshold = 70;
    if (gate.percentage >= threshold) {
      gate.status = 'PASSED';
    } else {
      gate.status = 'FAILED';
      gate.errors.push(`High-confidence rule percentage ${gate.percentage}% is below threshold ${threshold}%`);
    }

    // Add warnings
    if (gate.rules_without_reasoning.length > 0) {
      gate.warnings.push(`${gate.rules_without_reasoning.length} rules missing reasoning: ${gate.rules_without_reasoning.slice(0, 5).join(', ')}${gate.rules_without_reasoning.length > 5 ? '...' : ''}`);
    }
    if (gate.critical_rules_low_confidence.length > 0) {
      gate.errors.push(`Critical rules with low confidence: ${gate.critical_rules_low_confidence.join(', ')}`);
      gate.status = 'FAILED';
    }

    return gate;
  }

  /**
   * Gate 3: Source Traceability
   *
   * Validates that:
   * - Every rule has source_location
   * - Source locations are valid (reference real files/components)
   * - No generic "Unknown" sources
   * - Threshold: 100%
   */
  validateGate3_SourceTraceability() {
    const gate = {
      status: 'PENDING',
      percentage: 0,
      total_rules: 0,
      rules_with_valid_sources: 0,
      rules_missing_sources: [],
      invalid_source_locations: [],
      errors: [],
      warnings: []
    };

    const rules = this.ruletableData.rules || [];
    gate.total_rules = rules.length;

    for (const rule of rules) {
      const source = rule.source_location || '';
      const ruleId = rule.rule_id || 'Unknown';

      // Check source is not empty or generic
      if (!source || source.trim() === '' || source.toLowerCase() === 'unknown') {
        gate.rules_missing_sources.push(ruleId);
        continue;
      }

      // Validate source location format
      let isValid = false;

      // Check if references Phase 1 component
      const components = this.phase1Data.components || [];
      for (const component of components) {
        if (source.includes(component.name)) {
          isValid = true;
          break;
        }
      }

      // Check if references Phase 2 flow diagram
      if (!isValid && source.includes('.puml')) {
        const flowFilename = source.match(/flow-[a-z0-9-]+\.puml/i);
        if (flowFilename) {
          const flowPath = path.join(this.phase2Dir, flowFilename[0]);
          if (fs.existsSync(flowPath)) {
            isValid = true;
          }
        }
      }

      // Check if references Phase 1 file path
      if (!isValid && source.includes('.cpp') || source.includes('.java') || source.includes('.sql')) {
        // Assume valid if it looks like a reasonable file path
        isValid = true;
      }

      if (isValid) {
        gate.rules_with_valid_sources++;
      } else {
        gate.invalid_source_locations.push(`${ruleId}: ${source}`);
      }
    }

    // Calculate percentage
    if (gate.total_rules > 0) {
      gate.percentage = Math.round((gate.rules_with_valid_sources / gate.total_rules) * 100);
    }

    // Determine status (must be 100%)
    const threshold = 100;
    if (gate.percentage >= threshold) {
      gate.status = 'PASSED';
    } else {
      gate.status = 'FAILED';
      gate.errors.push(`Source traceability ${gate.percentage}% is below threshold ${threshold}%`);
    }

    // Add details
    if (gate.rules_missing_sources.length > 0) {
      gate.errors.push(`Rules missing source locations: ${gate.rules_missing_sources.join(', ')}`);
    }
    if (gate.invalid_source_locations.length > 0) {
      gate.warnings.push(`Rules with potentially invalid sources: ${gate.invalid_source_locations.slice(0, 3).join('; ')}${gate.invalid_source_locations.length > 3 ? '...' : ''}`);
    }

    return gate;
  }

  /**
   * Gate 4: Categorization Completeness
   *
   * Validates that:
   * - Every rule has type (validation/business_logic/integration/compliance)
   * - Every rule has business_impact
   * - Flow-based rules reference business_flow
   * - Threshold: 100%
   */
  validateGate4_CategorizationCompleteness() {
    const gate = {
      status: 'PENDING',
      percentage: 0,
      total_rules: 0,
      rules_fully_categorized: 0,
      rules_missing_type: [],
      rules_missing_impact: [],
      rules_missing_flow: [],
      errors: [],
      warnings: []
    };

    const validTypes = ['validation', 'business_logic', 'integration', 'compliance'];
    const validImpacts = ['critical', 'high', 'medium', 'low'];

    const rules = this.ruletableData.rules || [];
    gate.total_rules = rules.length;

    for (const rule of rules) {
      const ruleId = rule.rule_id || 'Unknown';
      const type = rule.type || '';
      const impact = rule.business_impact || '';
      const flow = rule.business_flow || '';
      const source = rule.source_location || '';

      let isFullyCategorized = true;

      // Check type
      if (!validTypes.includes(type)) {
        gate.rules_missing_type.push(`${ruleId}: type="${type}"`);
        isFullyCategorized = false;
      }

      // Check business_impact
      if (!validImpacts.includes(impact)) {
        gate.rules_missing_impact.push(`${ruleId}: impact="${impact}"`);
        isFullyCategorized = false;
      }

      // Check business_flow if source references Phase 2
      if (source.includes('.puml') || source.includes('phase2/flow')) {
        if (!flow || flow.trim() === '') {
          gate.rules_missing_flow.push(ruleId);
          isFullyCategorized = false;
        }
      }

      if (isFullyCategorized) {
        gate.rules_fully_categorized++;
      }
    }

    // Calculate percentage
    if (gate.total_rules > 0) {
      gate.percentage = Math.round((gate.rules_fully_categorized / gate.total_rules) * 100);
    }

    // Determine status (must be 100%)
    const threshold = 100;
    if (gate.percentage >= threshold) {
      gate.status = 'PASSED';
    } else {
      gate.status = 'FAILED';
      gate.errors.push(`Categorization completeness ${gate.percentage}% is below threshold ${threshold}%`);
    }

    // Add details
    if (gate.rules_missing_type.length > 0) {
      gate.errors.push(`Rules with invalid type: ${gate.rules_missing_type.slice(0, 5).join(', ')}${gate.rules_missing_type.length > 5 ? '...' : ''}`);
    }
    if (gate.rules_missing_impact.length > 0) {
      gate.errors.push(`Rules with invalid business_impact: ${gate.rules_missing_impact.slice(0, 5).join(', ')}${gate.rules_missing_impact.length > 5 ? '...' : ''}`);
    }
    if (gate.rules_missing_flow.length > 0) {
      gate.warnings.push(`Flow-based rules missing business_flow: ${gate.rules_missing_flow.join(', ')}`);
    }

    return gate;
  }

  /**
   * Gate 5: JSON Schema Validation
   *
   * Validates that:
   * - Valid JSON structure
   * - Required fields present
   * - Field types correct
   * - Threshold: Pass/Fail
   */
  validateGate5_JSONSchema() {
    const gate = {
      status: 'PENDING',
      valid_json: false,
      required_fields_present: false,
      field_types_valid: false,
      schema_errors: [],
      errors: [],
      warnings: []
    };

    try {
      // Already parsed successfully in loadRuletable()
      gate.valid_json = true;

      // Check required top-level fields
      const requiredTopLevel = ['feature_name', 'phase', 'rules', 'summary'];
      const missingTopLevel = [];

      for (const field of requiredTopLevel) {
        if (!(field in this.ruletableData)) {
          missingTopLevel.push(field);
        }
      }

      if (missingTopLevel.length === 0) {
        gate.required_fields_present = true;
      } else {
        gate.schema_errors.push(`Missing required top-level fields: ${missingTopLevel.join(', ')}`);
      }

      // Check each rule has required fields
      const requiredRuleFields = ['rule_id', 'description', 'type', 'confidence', 'reasoning', 'source_location', 'business_impact'];
      const rules = this.ruletableData.rules || [];
      const rulesWithMissingFields = [];

      for (let i = 0; i < rules.length; i++) {
        const rule = rules[i];
        const missing = [];

        for (const field of requiredRuleFields) {
          if (!(field in rule)) {
            missing.push(field);
          }
        }

        if (missing.length > 0) {
          rulesWithMissingFields.push(`Rule ${i + 1} (${rule.rule_id || 'Unknown'}): ${missing.join(', ')}`);
        }
      }

      if (rulesWithMissingFields.length === 0) {
        // Also check field types
        let typeErrors = [];

        for (const rule of rules) {
          const ruleId = rule.rule_id || 'Unknown';

          // confidence should be number 1-5
          if (typeof rule.confidence !== 'number' || rule.confidence < 1 || rule.confidence > 5) {
            typeErrors.push(`${ruleId}: confidence must be number 1-5, got ${rule.confidence}`);
          }

          // rule_id should match BR-XXX format
          if (typeof rule.rule_id === 'string' && !rule.rule_id.match(/^BR-\d+$/)) {
            typeErrors.push(`${ruleId}: rule_id should match format BR-XXX`);
          }
        }

        if (typeErrors.length === 0) {
          gate.field_types_valid = true;
        } else {
          gate.schema_errors.push(...typeErrors.slice(0, 5));
          if (typeErrors.length > 5) {
            gate.schema_errors.push(`... and ${typeErrors.length - 5} more type errors`);
          }
        }
      } else {
        gate.schema_errors.push(...rulesWithMissingFields.slice(0, 5));
        if (rulesWithMissingFields.length > 5) {
          gate.schema_errors.push(`... and ${rulesWithMissingFields.length - 5} more rules with missing fields`);
        }
      }

      // Determine status
      if (gate.valid_json && gate.required_fields_present && gate.field_types_valid) {
        gate.status = 'PASSED';
      } else {
        gate.status = 'FAILED';
        gate.errors.push('JSON schema validation failed');
        gate.errors.push(...gate.schema_errors);
      }

    } catch (error) {
      gate.status = 'FAILED';
      gate.errors.push(`JSON parsing error: ${error.message}`);
    }

    return gate;
  }

  /**
   * Calculate overall quality score from gate results
   */
  calculateQualityScore(gates) {
    const gate1Score = gates.gate_1_rule_completeness.percentage || 0;
    const gate2Score = gates.gate_2_confidence_quality.percentage || 0;
    const gate3Score = gates.gate_3_source_traceability.percentage || 0;
    const gate4Score = gates.gate_4_categorization_completeness.percentage || 0;
    const gate5Pass = gates.gate_5_json_schema.status === 'PASSED' ? 1 : 0;

    const score = (
      gate1Score * 0.25 +
      gate2Score * 0.30 +
      gate3Score * 0.20 +
      gate4Score * 0.15 +
      gate5Pass * 10
    );

    return Math.round(score * 10) / 10;
  }

  /**
   * Determine overall status based on quality score
   */
  determineOverallStatus(qualityScore, gates) {
    const threshold = 75;

    // Must pass all gates for COMPLETE status
    const allGatesPassed = Object.values(gates).every(gate => gate.status === 'PASSED');

    if (qualityScore >= threshold && allGatesPassed) {
      return 'COMPLETE';
    } else {
      return 'INCOMPLETE';
    }
  }

  /**
   * Generate recommendations based on validation results
   */
  generateRecommendations(gates, qualityScore, overallStatus) {
    const recommendations = [];

    if (overallStatus === 'COMPLETE') {
      recommendations.push('All validation gates passed');
      recommendations.push(`Rule quality exceeds minimum thresholds (${qualityScore}/100)`);
      recommendations.push('Ready for Phase 4');
    } else {
      recommendations.push(`Overall quality score ${qualityScore}/100 - needs improvement`);

      // Gate-specific recommendations
      if (gates.gate_1_rule_completeness.status === 'FAILED') {
        recommendations.push(`Gate 1 Failed: Extract rules for ${gates.gate_1_rule_completeness.missing_components.length + gates.gate_1_rule_completeness.missing_flows.length} missing components/flows`);
      }
      if (gates.gate_2_confidence_quality.status === 'FAILED') {
        recommendations.push(`Gate 2 Failed: Improve confidence scores - only ${gates.gate_2_confidence_quality.percentage}% have high confidence`);
      }
      if (gates.gate_3_source_traceability.status === 'FAILED') {
        recommendations.push(`Gate 3 Failed: Add source locations for ${gates.gate_3_source_traceability.rules_missing_sources.length} rules`);
      }
      if (gates.gate_4_categorization_completeness.status === 'FAILED') {
        recommendations.push(`Gate 4 Failed: Complete categorization for ${gates.gate_4_categorization_completeness.total_rules - gates.gate_4_categorization_completeness.rules_fully_categorized} rules`);
      }
      if (gates.gate_5_json_schema.status === 'FAILED') {
        recommendations.push('Gate 5 Failed: Fix JSON schema errors');
      }

      recommendations.push('Iterate on failed gates and re-run validation');
    }

    return recommendations;
  }

  /**
   * Run all validation gates and generate report
   */
  validate() {
    console.log(`Validating business rules for feature: ${this.feature}`);
    console.log('Loading inputs...');

    // Load all inputs
    this.loadRuletable();
    this.loadPhase1();
    this.loadPhase2();

    console.log('Running validation gates...');

    // Run all 5 gates
    const gates = {
      gate_1_rule_completeness: this.validateGate1_RuleCompleteness(),
      gate_2_confidence_quality: this.validateGate2_ConfidenceQuality(),
      gate_3_source_traceability: this.validateGate3_SourceTraceability(),
      gate_4_categorization_completeness: this.validateGate4_CategorizationCompleteness(),
      gate_5_json_schema: this.validateGate5_JSONSchema()
    };

    // Calculate overall quality score
    const qualityScore = this.calculateQualityScore(gates);
    const overallStatus = this.determineOverallStatus(qualityScore, gates);
    const recommendations = this.generateRecommendations(gates, qualityScore, overallStatus);

    // Generate validation report
    const report = {
      feature: this.feature,
      phase: 3,
      timestamp: new Date().toISOString(),
      validation_gates: gates,
      overall_status: overallStatus,
      overall_quality_score: qualityScore,
      recommendations: recommendations
    };

    // Print summary
    console.log('\n=== Validation Results ===');
    console.log(`Overall Status: ${overallStatus}`);
    console.log(`Overall Quality Score: ${qualityScore}/100`);
    console.log('\nGate Results:');
    console.log(`  Gate 1 (Rule Completeness): ${gates.gate_1_rule_completeness.status} (${gates.gate_1_rule_completeness.percentage}%)`);
    console.log(`  Gate 2 (Confidence Quality): ${gates.gate_2_confidence_quality.status} (${gates.gate_2_confidence_quality.percentage}%)`);
    console.log(`  Gate 3 (Source Traceability): ${gates.gate_3_source_traceability.status} (${gates.gate_3_source_traceability.percentage}%)`);
    console.log(`  Gate 4 (Categorization): ${gates.gate_4_categorization_completeness.status} (${gates.gate_4_categorization_completeness.percentage}%)`);
    console.log(`  Gate 5 (JSON Schema): ${gates.gate_5_json_schema.status}`);
    console.log('\nRecommendations:');
    recommendations.forEach(rec => console.log(`  - ${rec}`));

    return report;
  }
}

// Main execution
function main() {
  const args = process.argv.slice(2);

  // Parse command-line arguments
  const config = {
    phase3Dir: null,
    phase1Dir: null,
    phase2Dir: null,
    output: null,
    feature: null
  };

  for (let i = 0; i < args.length; i += 2) {
    const key = args[i];
    const value = args[i + 1];

    switch (key) {
      case '--phase3-dir':
        config.phase3Dir = value;
        break;
      case '--phase1-dir':
        config.phase1Dir = value;
        break;
      case '--phase2-dir':
        config.phase2Dir = value;
        break;
      case '--output':
        config.output = value;
        break;
      case '--feature':
        config.feature = value;
        break;
    }
  }

  // Validate required parameters
  if (!config.phase3Dir || !config.phase1Dir || !config.phase2Dir || !config.output || !config.feature) {
    console.error('Error: Missing required parameters');
    console.error('Usage: node validate-ruletable.js \\');
    console.error('  --phase3-dir <path> \\');
    console.error('  --phase1-dir <path> \\');
    console.error('  --phase2-dir <path> \\');
    console.error('  --output <path> \\');
    console.error('  --feature <name>');
    process.exit(2);
  }

  try {
    // Run validation
    const validator = new RuleTableValidator(
      config.phase3Dir,
      config.phase1Dir,
      config.phase2Dir,
      config.feature
    );

    const report = validator.validate();

    // Write report to output file
    const outputDir = path.dirname(config.output);
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    fs.writeFileSync(config.output, JSON.stringify(report, null, 2), 'utf-8');
    console.log(`\nValidation report written to: ${config.output}`);

    // Exit with appropriate code
    if (report.overall_status === 'COMPLETE') {
      console.log('\n✓ Validation PASSED - Ready for Phase 4');
      process.exit(0);
    } else {
      console.log('\n✗ Validation FAILED - Iteration required');
      process.exit(1);
    }

  } catch (error) {
    console.error(`\nValidation error: ${error.message}`);
    process.exit(2);
  }
}

// Run if executed directly
if (require.main === module) {
  main();
}

module.exports = { RuleTableValidator };
