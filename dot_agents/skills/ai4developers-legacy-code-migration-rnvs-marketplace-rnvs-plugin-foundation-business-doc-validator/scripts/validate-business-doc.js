#!/usr/bin/env node

/**
 * Business Documentation Validator - 5-Gate Quality System
 *
 * Validates Phase 4 business documentation outputs for completeness,
 * terminology consistency, stakeholder coverage, process quality, and schema compliance.
 *
 * Usage:
 *   node validate-business-doc.js \
 *     --phase4-dir results/NBM/phase4 \
 *     --phase3-dir results/NBM/phase3 \
 *     --phase2-dir results/NBM/phase2 \
 *     --phase1-dir results/NBM/phase1 \
 *     --output results/NBM/phase4/doc-quality-report.json \
 *     --feature NBM
 *
 * Exit Codes:
 *   0 - Validation passed (COMPLETE, score >= 75)
 *   1 - Validation failed (INCOMPLETE, score < 75)
 *   2 - Script error (invalid inputs, missing files)
 */

const fs = require('fs');
const path = require('path');

class BusinessDocValidator {
  constructor(phase4Dir, phase3Dir, phase2Dir, phase1Dir, feature) {
    this.phase4Dir = phase4Dir;
    this.phase3Dir = phase3Dir;
    this.phase2Dir = phase2Dir;
    this.phase1Dir = phase1Dir;
    this.feature = feature;

    // Loaded data
    this.businessDoc = null;
    this.ruletable = null;
    this.phase2Summary = null;
    this.phase1Analysis = null;

    // Validation thresholds
    this.THRESHOLDS = {
      GATE_1_DOCUMENTATION_COMPLETENESS: 80,  // >= 80%
      GATE_2_TERMINOLOGY_CONSISTENCY: 90,     // >= 90%
      GATE_3_STAKEHOLDER_COVERAGE: 70,        // >= 70%
      GATE_4_PROCESS_QUALITY: 75,             // >= 75%
      OVERALL_QUALITY_SCORE: 75               // >= 75 for COMPLETE status
    };

    // Gate weights for overall score calculation
    this.GATE_WEIGHTS = {
      GATE_1: 0.25,  // 25% - Completeness is critical
      GATE_2: 0.20,  // 20% - Terminology consistency
      GATE_3: 0.20,  // 20% - Stakeholder coverage
      GATE_4: 0.25,  // 25% - Process quality most important
      GATE_5: 10     // 10 points if passed, 0 if failed
    };
  }

  /**
   * Load and parse business-documentation.json
   */
  loadBusinessDoc() {
    const docPath = path.join(this.phase4Dir, 'business-documentation.json');

    if (!fs.existsSync(docPath)) {
      throw new Error(`business-documentation.json not found at ${docPath}`);
    }

    try {
      const content = fs.readFileSync(docPath, 'utf-8');
      this.businessDoc = JSON.parse(content);
    } catch (error) {
      throw new Error(`Failed to parse business-documentation.json: ${error.message}`);
    }
  }

  /**
   * Load Phase 3 ruletable.json for rule comparison
   */
  loadRuletable() {
    const ruletablePath = path.join(this.phase3Dir, 'ruletable.json');

    if (!fs.existsSync(ruletablePath)) {
      throw new Error(`Phase 3 ruletable.json not found at ${ruletablePath}`);
    }

    try {
      const content = fs.readFileSync(ruletablePath, 'utf-8');
      this.ruletable = JSON.parse(content);
    } catch (error) {
      throw new Error(`Failed to parse ruletable.json: ${error.message}`);
    }
  }

  /**
   * Load Phase 2 PHASE2_SUMMARY.md for flow references
   */
  loadPhase2() {
    const summaryPath = path.join(this.phase2Dir, 'PHASE2_SUMMARY.md');

    if (!fs.existsSync(summaryPath)) {
      throw new Error(`Phase 2 PHASE2_SUMMARY.md not found at ${summaryPath}`);
    }

    try {
      this.phase2Summary = fs.readFileSync(summaryPath, 'utf-8');
    } catch (error) {
      throw new Error(`Failed to read Phase 2 summary: ${error.message}`);
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
      this.phase1Analysis = JSON.parse(content);
    } catch (error) {
      throw new Error(`Failed to parse Phase 1 analysis.json: ${error.message}`);
    }
  }

  /**
   * Extract flow list from Phase 2 summary
   */
  extractFlowsFromPhase2() {
    const flows = new Set();
    const lines = this.phase2Summary.split('\n');

    for (const line of lines) {
      const match = line.match(/flow-([a-z0-9-]+)\.puml/i);
      if (match) {
        const flowName = match[1]
          .split('-')
          .map(word => word.charAt(0).toUpperCase() + word.slice(1))
          .join(' ');
        flows.add(flowName);
      }
    }

    return Array.from(flows);
  }

  /**
   * Gate 1: Documentation Completeness (≥80%)
   *
   * Validates that:
   * - All required sections are present
   * - All rules from Phase 3 have business objectives documented
   * - All flows from Phase 2 have process documentation
   * - Glossary consolidates terms from all phases
   */
  validateGate1_DocumentationCompleteness() {
    const gate = {
      status: 'PENDING',
      percentage: 0,
      details: '',
      errors: [],
      warnings: []
    };

    let completenessScore = 0;
    let maxScore = 0;

    // Check 1: Required sections present (30 points)
    maxScore += 30;
    const requiredSections = [
      'overview',
      'business_rules_enhanced',
      'business_processes',
      'stakeholder_analysis',
      'impact_analysis',
      'glossary',
      'recommendations'
    ];

    let sectionsPresent = 0;
    const missingSections = [];

    for (const section of requiredSections) {
      if (this.businessDoc[section]) {
        sectionsPresent++;
      } else {
        missingSections.push(section);
      }
    }

    completenessScore += (sectionsPresent / requiredSections.length) * 30;

    if (missingSections.length > 0) {
      gate.errors.push(`Missing required sections: ${missingSections.join(', ')}`);
    }

    // Check 2: All Phase 3 rules have business objectives (40 points)
    maxScore += 40;
    const phase3Rules = this.ruletable.rules || [];
    const enhancedRules = this.businessDoc.business_rules_enhanced || [];

    const phase3RuleIds = new Set(phase3Rules.map(r => r.rule_id));
    const enhancedRuleIds = new Set(enhancedRules.map(r => r.rule_id));

    let rulesWithObjectives = 0;
    const missingRuleObjectives = [];

    for (const ruleId of phase3RuleIds) {
      if (enhancedRuleIds.has(ruleId)) {
        const enhancedRule = enhancedRules.find(r => r.rule_id === ruleId);
        if (enhancedRule && enhancedRule.business_objective &&
            enhancedRule.business_objective.length >= 20) {
          rulesWithObjectives++;
        } else {
          missingRuleObjectives.push(ruleId);
        }
      } else {
        missingRuleObjectives.push(ruleId);
      }
    }

    if (phase3RuleIds.size > 0) {
      completenessScore += (rulesWithObjectives / phase3RuleIds.size) * 40;
    }

    if (missingRuleObjectives.length > 0 && missingRuleObjectives.length <= 5) {
      gate.errors.push(`Rules missing business objectives: ${missingRuleObjectives.slice(0, 5).join(', ')}${missingRuleObjectives.length > 5 ? ' and ' + (missingRuleObjectives.length - 5) + ' more' : ''}`);
    } else if (missingRuleObjectives.length > 5) {
      gate.errors.push(`${missingRuleObjectives.length} rules missing business objectives`);
    }

    // Check 3: All Phase 2 flows have process documentation (30 points)
    maxScore += 30;
    const phase2Flows = this.extractFlowsFromPhase2();
    const documentedProcesses = this.businessDoc.business_processes || [];

    const documentedFlows = new Set(documentedProcesses.map(p => p.process_name));
    let flowsDocumented = 0;
    const missingFlowDocs = [];

    for (const flow of phase2Flows) {
      let found = false;
      for (const docFlow of documentedFlows) {
        if (docFlow.includes(flow) || flow.includes(docFlow.split('(')[0].trim())) {
          found = true;
          break;
        }
      }
      if (found) {
        flowsDocumented++;
      } else {
        missingFlowDocs.push(flow);
      }
    }

    if (phase2Flows.length > 0) {
      completenessScore += (flowsDocumented / phase2Flows.length) * 30;
    }

    if (missingFlowDocs.length > 0) {
      gate.warnings.push(`Flows without process documentation: ${missingFlowDocs.join(', ')}`);
    }

    // Calculate final percentage
    gate.percentage = maxScore > 0 ? (completenessScore / maxScore) * 100 : 0;
    gate.status = gate.percentage >= this.THRESHOLDS.GATE_1_DOCUMENTATION_COMPLETENESS ? 'PASSED' : 'FAILED';

    gate.details = `${sectionsPresent}/${requiredSections.length} sections present, ` +
                  `${rulesWithObjectives}/${phase3RuleIds.size} rules with objectives, ` +
                  `${flowsDocumented}/${phase2Flows.length} flows documented`;

    return gate;
  }

  /**
   * Gate 2: Terminology Consistency (≥90%)
   *
   * Validates that:
   * - German terms in glossary match Phase 3 ruletable
   * - No conflicting translations
   * - All key terms are defined
   * - Terminology usage is consistent
   */
  validateGate2_TerminologyConsistency() {
    const gate = {
      status: 'PENDING',
      percentage: 0,
      details: '',
      errors: [],
      warnings: []
    };

    let consistencyScore = 0;
    let maxScore = 0;

    // Check 1: Glossary contains Phase 3 terms (50 points)
    maxScore += 50;

    // Extract all german_terms from Phase 3 ruletable
    const phase3Terms = new Set();
    for (const rule of this.ruletable.rules || []) {
      if (rule.german_terms && Array.isArray(rule.german_terms)) {
        rule.german_terms.forEach(term => phase3Terms.add(term));
      }
    }

    const glossary = this.businessDoc.glossary || [];
    const glossaryTerms = new Set(glossary.map(entry => entry.german_term));

    let termsInGlossary = 0;
    const missingTerms = [];

    for (const term of phase3Terms) {
      if (glossaryTerms.has(term)) {
        termsInGlossary++;
      } else {
        missingTerms.push(term);
      }
    }

    if (phase3Terms.size > 0) {
      consistencyScore += (termsInGlossary / phase3Terms.size) * 50;
    }

    if (missingTerms.length > 0 && missingTerms.length <= 5) {
      gate.warnings.push(`Phase 3 terms missing from glossary: ${missingTerms.slice(0, 5).join(', ')}`);
    } else if (missingTerms.length > 5) {
      gate.warnings.push(`${missingTerms.length} Phase 3 terms missing from glossary`);
    }

    // Check 2: No duplicate translations (25 points)
    maxScore += 25;
    const translationMap = new Map(); // german_term -> english_term
    const conflictingTranslations = [];

    for (const entry of glossary) {
      if (entry.german_term && entry.english_term) {
        if (translationMap.has(entry.german_term)) {
          const existing = translationMap.get(entry.german_term);
          if (existing !== entry.english_term) {
            conflictingTranslations.push(
              `${entry.german_term}: "${existing}" vs "${entry.english_term}"`
            );
          }
        } else {
          translationMap.set(entry.german_term, entry.english_term);
        }
      }
    }

    if (conflictingTranslations.length === 0) {
      consistencyScore += 25;
    } else {
      gate.errors.push(`Conflicting translations: ${conflictingTranslations.join(', ')}`);
    }

    // Check 3: All glossary entries have proper definitions (25 points)
    maxScore += 25;
    let termsWithDefinitions = 0;
    const termsWithoutDefinitions = [];

    for (const entry of glossary) {
      if (entry.definition && entry.definition.length >= 20) {
        termsWithDefinitions++;
      } else {
        termsWithoutDefinitions.push(entry.german_term || entry.english_term || 'unknown');
      }
    }

    if (glossary.length > 0) {
      consistencyScore += (termsWithDefinitions / glossary.length) * 25;
    }

    if (termsWithoutDefinitions.length > 0) {
      gate.errors.push(`Terms without proper definitions: ${termsWithoutDefinitions.slice(0, 3).join(', ')}${termsWithoutDefinitions.length > 3 ? ' and ' + (termsWithoutDefinitions.length - 3) + ' more' : ''}`);
    }

    // Calculate final percentage
    gate.percentage = maxScore > 0 ? (consistencyScore / maxScore) * 100 : 0;
    gate.status = gate.percentage >= this.THRESHOLDS.GATE_2_TERMINOLOGY_CONSISTENCY ? 'PASSED' : 'FAILED';

    gate.details = `${termsInGlossary}/${phase3Terms.size} Phase 3 terms in glossary, ` +
                  `${conflictingTranslations.length} conflicts, ` +
                  `${termsWithDefinitions}/${glossary.length} terms with definitions`;

    return gate;
  }

  /**
   * Gate 3: Stakeholder Coverage (≥70%)
   *
   * Validates that:
   * - Critical rules have business owners assigned
   * - Department responsibilities are documented
   * - Communication channels are defined
   */
  validateGate3_StakeholderCoverage() {
    const gate = {
      status: 'PENDING',
      percentage: 0,
      details: '',
      errors: [],
      warnings: []
    };

    let coverageScore = 0;
    let maxScore = 0;

    // Check 1: Critical rules have business owners (60 points)
    maxScore += 60;

    const criticalRules = (this.ruletable.rules || []).filter(
      r => r.business_impact === 'critical'
    );

    const enhancedRules = this.businessDoc.business_rules_enhanced || [];
    const enhancedRuleMap = new Map(
      enhancedRules.map(r => [r.rule_id, r])
    );

    let criticalRulesWithOwners = 0;
    const criticalRulesWithoutOwners = [];

    for (const rule of criticalRules) {
      const enhanced = enhancedRuleMap.get(rule.rule_id);
      if (enhanced && enhanced.business_owner && enhanced.business_owner.length >= 3) {
        criticalRulesWithOwners++;
      } else {
        criticalRulesWithoutOwners.push(rule.rule_id);
      }
    }

    if (criticalRules.length > 0) {
      coverageScore += (criticalRulesWithOwners / criticalRules.length) * 60;
    } else {
      // No critical rules, full score
      coverageScore += 60;
    }

    if (criticalRulesWithoutOwners.length > 0) {
      gate.errors.push(`Critical rules without business owners: ${criticalRulesWithoutOwners.slice(0, 5).join(', ')}${criticalRulesWithoutOwners.length > 5 ? ` and ${criticalRulesWithoutOwners.length - 5} more` : ''}`);
    }

    // Check 2: Stakeholder analysis has departments and responsibilities (25 points)
    maxScore += 25;

    const stakeholderAnalysis = this.businessDoc.stakeholder_analysis || {};
    const departments = stakeholderAnalysis.departments || [];
    const responsibilities = stakeholderAnalysis.responsibilities || [];

    if (departments.length >= 2 && responsibilities.length >= 2) {
      coverageScore += 25;
    } else if (departments.length >= 1 || responsibilities.length >= 1) {
      coverageScore += 12.5;
      gate.warnings.push('Incomplete stakeholder analysis: need at least 2 departments and 2 responsibilities');
    } else {
      gate.errors.push('No departments or responsibilities documented');
    }

    // Check 3: Communication channels defined (15 points)
    maxScore += 15;

    const communicationChannels = stakeholderAnalysis.communication_channels || [];

    if (communicationChannels.length >= 1) {
      coverageScore += 15;
    } else {
      gate.warnings.push('No communication channels defined');
    }

    // Calculate final percentage
    gate.percentage = maxScore > 0 ? (coverageScore / maxScore) * 100 : 0;
    gate.status = gate.percentage >= this.THRESHOLDS.GATE_3_STAKEHOLDER_COVERAGE ? 'PASSED' : 'FAILED';

    gate.details = `${criticalRulesWithOwners}/${criticalRules.length} critical rules with owners, ` +
                  `${departments.length} departments, ` +
                  `${responsibilities.length} responsibilities, ` +
                  `${communicationChannels.length} communication channels`;

    return gate;
  }

  /**
   * Gate 4: Process Quality (≥75%)
   *
   * Validates that:
   * - All flows documented as business processes
   * - Process steps clearly defined
   * - Decision criteria explained in business language
   * - Exception scenarios documented
   */
  validateGate4_ProcessQuality() {
    const gate = {
      status: 'PENDING',
      percentage: 0,
      details: '',
      errors: [],
      warnings: []
    };

    let qualityScore = 0;
    let maxScore = 0;

    const businessProcesses = this.businessDoc.business_processes || [];

    if (businessProcesses.length === 0) {
      gate.errors.push('No business processes documented');
      gate.percentage = 0;
      gate.status = 'FAILED';
      gate.details = '0 processes documented';
      return gate;
    }

    // Check 1: Process steps quality (40 points)
    maxScore += 40;
    let processesWithGoodSteps = 0;

    for (const process of businessProcesses) {
      const steps = process.process_steps || [];
      // Good process has at least 3 steps, each with meaningful description (≥15 chars)
      const goodSteps = steps.filter(step => step && step.length >= 15);
      if (goodSteps.length >= 3) {
        processesWithGoodSteps++;
      }
    }

    qualityScore += (processesWithGoodSteps / businessProcesses.length) * 40;

    // Check 2: Decision criteria documented (30 points)
    maxScore += 30;
    let processesWithDecisionCriteria = 0;

    for (const process of businessProcesses) {
      const criteria = process.decision_criteria || [];
      // Good decision criteria array has at least one well-defined decision
      if (criteria.length >= 1) {
        processesWithDecisionCriteria++;
      }
    }

    qualityScore += (processesWithDecisionCriteria / businessProcesses.length) * 30;

    // Check 3: Exception scenarios documented (20 points)
    maxScore += 20;
    let processesWithExceptions = 0;

    for (const process of businessProcesses) {
      const exceptions = process.exception_scenarios || [];
      if (exceptions.length >= 1) {
        processesWithExceptions++;
      }
    }

    qualityScore += (processesWithExceptions / businessProcesses.length) * 20;

    // Check 4: Rules applied referenced (10 points)
    maxScore += 10;
    let processesWithRules = 0;

    for (const process of businessProcesses) {
      const rules = process.rules_applied || [];
      if (rules.length >= 1) {
        processesWithRules++;
      }
    }

    qualityScore += (processesWithRules / businessProcesses.length) * 10;

    // Calculate final percentage
    gate.percentage = maxScore > 0 ? (qualityScore / maxScore) * 100 : 0;
    gate.status = gate.percentage >= this.THRESHOLDS.GATE_4_PROCESS_QUALITY ? 'PASSED' : 'FAILED';

    gate.details = `${businessProcesses.length} processes: ` +
                  `${processesWithGoodSteps} with good steps, ` +
                  `${processesWithDecisionCriteria} with decision criteria, ` +
                  `${processesWithExceptions} with exceptions, ` +
                  `${processesWithRules} with rules`;

    return gate;
  }

  /**
   * Gate 5: JSON Schema Validation (Pass/Fail)
   *
   * Validates that:
   * - business-documentation.json is valid JSON
   * - All required fields are present
   * - Field types match schema
   */
  validateGate5_SchemaValidation() {
    const gate = {
      status: 'PENDING',
      valid_json: false,
      required_fields_present: false,
      field_types_valid: false,
      details: '',
      schema_errors: [],
      errors: [],
      warnings: []
    };

    // Check 1: Valid JSON (already validated in loadBusinessDoc)
    gate.valid_json = true;

    // Check 2: Required top-level fields
    const requiredFields = [
      'feature_name',
      'feature_full_name',
      'phase',
      'timestamp',
      'inputs',
      'overview',
      'business_rules_enhanced',
      'business_processes',
      'stakeholder_analysis',
      'impact_analysis',
      'glossary',
      'recommendations',
      'validation_report'
    ];

    const missingFields = [];
    for (const field of requiredFields) {
      if (!this.businessDoc[field]) {
        missingFields.push(field);
      }
    }

    gate.required_fields_present = missingFields.length === 0;

    if (missingFields.length > 0) {
      gate.schema_errors.push(`Missing required fields: ${missingFields.join(', ')}`);
    }

    // Check 3: Field types
    const typeErrors = [];

    if (typeof this.businessDoc.feature_name !== 'string') {
      typeErrors.push('feature_name must be string');
    }

    if (typeof this.businessDoc.phase !== 'number' || this.businessDoc.phase !== 4) {
      typeErrors.push('phase must be number with value 4');
    }

    if (!Array.isArray(this.businessDoc.business_rules_enhanced)) {
      typeErrors.push('business_rules_enhanced must be array');
    }

    if (!Array.isArray(this.businessDoc.business_processes)) {
      typeErrors.push('business_processes must be array');
    }

    if (!Array.isArray(this.businessDoc.glossary)) {
      typeErrors.push('glossary must be array');
    }

    gate.field_types_valid = typeErrors.length === 0;

    if (typeErrors.length > 0) {
      gate.schema_errors.push(...typeErrors);
    }

    // Overall status
    gate.status = gate.valid_json && gate.required_fields_present && gate.field_types_valid
                  ? 'PASSED'
                  : 'FAILED';

    gate.details = gate.status === 'PASSED'
                   ? 'Valid JSON schema'
                   : `Schema errors: ${gate.schema_errors.join(', ')}`;

    return gate;
  }

  /**
   * Calculate overall quality score
   */
  calculateOverallScore(gate1, gate2, gate3, gate4, gate5) {
    const score = (
      gate1.percentage * this.GATE_WEIGHTS.GATE_1 +
      gate2.percentage * this.GATE_WEIGHTS.GATE_2 +
      gate3.percentage * this.GATE_WEIGHTS.GATE_3 +
      gate4.percentage * this.GATE_WEIGHTS.GATE_4 +
      (gate5.status === 'PASSED' ? this.GATE_WEIGHTS.GATE_5 : 0)
    );

    return Math.round(score * 10) / 10; // Round to 1 decimal place
  }

  /**
   * Run all validation gates and generate report
   */
  validate() {
    console.error('Loading input files...');
    this.loadBusinessDoc();
    this.loadRuletable();
    this.loadPhase2();
    this.loadPhase1();

    console.error('Running validation gates...');

    const gate1 = this.validateGate1_DocumentationCompleteness();
    console.error(`Gate 1 (Documentation Completeness): ${gate1.status} - ${gate1.percentage.toFixed(1)}%`);

    const gate2 = this.validateGate2_TerminologyConsistency();
    console.error(`Gate 2 (Terminology Consistency): ${gate2.status} - ${gate2.percentage.toFixed(1)}%`);

    const gate3 = this.validateGate3_StakeholderCoverage();
    console.error(`Gate 3 (Stakeholder Coverage): ${gate3.status} - ${gate3.percentage.toFixed(1)}%`);

    const gate4 = this.validateGate4_ProcessQuality();
    console.error(`Gate 4 (Process Quality): ${gate4.status} - ${gate4.percentage.toFixed(1)}%`);

    const gate5 = this.validateGate5_SchemaValidation();
    console.error(`Gate 5 (Schema Validation): ${gate5.status}`);

    const overallScore = this.calculateOverallScore(gate1, gate2, gate3, gate4, gate5);
    const overallStatus = overallScore >= this.THRESHOLDS.OVERALL_QUALITY_SCORE ? 'COMPLETE' : 'INCOMPLETE';

    console.error(`\nOverall Quality Score: ${overallScore}/100`);
    console.error(`Overall Status: ${overallStatus}`);

    const report = {
      feature: this.feature,
      phase: 4,
      timestamp: new Date().toISOString(),
      validation_gates: {
        gate_1_documentation_completeness: gate1,
        gate_2_terminology_consistency: gate2,
        gate_3_stakeholder_coverage: gate3,
        gate_4_process_quality: gate4,
        gate_5_schema_validation: gate5
      },
      overall_status: overallStatus,
      overall_quality_score: overallScore,
      recommendations: this.generateRecommendations(gate1, gate2, gate3, gate4, gate5, overallStatus)
    };

    return report;
  }

  /**
   * Generate recommendations based on validation results
   */
  generateRecommendations(gate1, gate2, gate3, gate4, gate5, overallStatus) {
    const recommendations = [];

    if (overallStatus === 'COMPLETE') {
      recommendations.push('All validation gates passed');
      recommendations.push(`Documentation quality exceeds minimum thresholds (${this.calculateOverallScore(gate1, gate2, gate3, gate4, gate5)}/100)`);
      recommendations.push('Ready for Phase 5');
    } else {
      if (gate1.status === 'FAILED') {
        recommendations.push(`Gate 1 FAILED: Improve documentation completeness (${gate1.percentage.toFixed(1)}% < ${this.THRESHOLDS.GATE_1_DOCUMENTATION_COMPLETENESS}%)`);
        recommendations.push('Action: Document business objectives for all Phase 3 rules');
        recommendations.push('Action: Create process documentation for all Phase 2 flows');
      }

      if (gate2.status === 'FAILED') {
        recommendations.push(`Gate 2 FAILED: Improve terminology consistency (${gate2.percentage.toFixed(1)}% < ${this.THRESHOLDS.GATE_2_TERMINOLOGY_CONSISTENCY}%)`);
        recommendations.push('Action: Add missing Phase 3 terms to glossary');
        recommendations.push('Action: Resolve conflicting translations');
      }

      if (gate3.status === 'FAILED') {
        recommendations.push(`Gate 3 FAILED: Improve stakeholder coverage (${gate3.percentage.toFixed(1)}% < ${this.THRESHOLDS.GATE_3_STAKEHOLDER_COVERAGE}%)`);
        recommendations.push('Action: Assign business owners to critical rules');
        recommendations.push('Action: Document department responsibilities');
      }

      if (gate4.status === 'FAILED') {
        recommendations.push(`Gate 4 FAILED: Improve process quality (${gate4.percentage.toFixed(1)}% < ${this.THRESHOLDS.GATE_4_PROCESS_QUALITY}%)`);
        recommendations.push('Action: Add detailed process steps for all flows');
        recommendations.push('Action: Document decision criteria in business language');
        recommendations.push('Action: Add exception scenarios');
      }

      if (gate5.status === 'FAILED') {
        recommendations.push('Gate 5 FAILED: Fix JSON schema errors');
        recommendations.push('Action: Ensure all required fields are present');
        recommendations.push('Action: Validate field types match schema');
      }
    }

    return recommendations;
  }
}

/**
 * Main execution
 */
function main() {
  const args = process.argv.slice(2);
  const options = {};

  // Parse command-line arguments
  for (let i = 0; i < args.length; i += 2) {
    const key = args[i].replace(/^--/, '');
    const value = args[i + 1];
    options[key] = value;
  }

  // Validate required options
  const required = ['phase4-dir', 'phase3-dir', 'phase2-dir', 'phase1-dir', 'output', 'feature'];
  const missing = required.filter(key => !options[key]);

  if (missing.length > 0) {
    console.error('Error: Missing required options:', missing.join(', '));
    console.error('\nUsage:');
    console.error('  node validate-business-doc.js \\');
    console.error('    --phase4-dir results/NBM/phase4 \\');
    console.error('    --phase3-dir results/NBM/phase3 \\');
    console.error('    --phase2-dir results/NBM/phase2 \\');
    console.error('    --phase1-dir results/NBM/phase1 \\');
    console.error('    --output results/NBM/phase4/doc-quality-report.json \\');
    console.error('    --feature NBM');
    process.exit(2);
  }

  try {
    const validator = new BusinessDocValidator(
      options['phase4-dir'],
      options['phase3-dir'],
      options['phase2-dir'],
      options['phase1-dir'],
      options['feature']
    );

    const report = validator.validate();

    // Write report to output file
    const outputDir = path.dirname(options['output']);
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    fs.writeFileSync(options['output'], JSON.stringify(report, null, 2));
    console.error(`\nValidation report written to: ${options['output']}`);

    // Exit with appropriate code
    process.exit(report.overall_status === 'COMPLETE' ? 0 : 1);

  } catch (error) {
    console.error('\nValidation Error:', error.message);
    process.exit(2);
  }
}

if (require.main === module) {
  main();
}

module.exports = { BusinessDocValidator };
