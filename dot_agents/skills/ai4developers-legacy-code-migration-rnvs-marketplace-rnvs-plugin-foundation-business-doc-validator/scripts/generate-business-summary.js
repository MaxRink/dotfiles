#!/usr/bin/env node

/**
 * Business Documentation Summary Generator
 *
 * Generates human-readable markdown summary from business-documentation.json
 *
 * Usage:
 *   node generate-business-summary.js \
 *     --input results/NBM/phase4/business-documentation.json \
 *     --output results/NBM/phase4/PHASE4_SUMMARY.md
 *
 * Exit Codes:
 *   0 - Success
 *   2 - Error (invalid inputs, missing files)
 */

const fs = require('fs');
const path = require('path');

class BusinessSummaryGenerator {
  constructor(inputPath, outputPath) {
    this.inputPath = inputPath;
    this.outputPath = outputPath;
    this.businessDoc = null;
  }

  /**
   * Load and parse business-documentation.json
   */
  load() {
    if (!fs.existsSync(this.inputPath)) {
      throw new Error(`business-documentation.json not found at ${this.inputPath}`);
    }

    try {
      const content = fs.readFileSync(this.inputPath, 'utf-8');
      this.businessDoc = JSON.parse(content);
    } catch (error) {
      throw new Error(`Failed to parse business-documentation.json: ${error.message}`);
    }
  }

  /**
   * Generate markdown summary
   */
  generate() {
    const doc = this.businessDoc;
    const validation = doc.validation_report || {};

    let markdown = `# Phase 4 Summary: ${doc.feature_name}\n\n`;

    // Status
    markdown += `**Status**: ${validation.overall_status === 'COMPLETE' ? 'COMPLETE ✅' : 'INCOMPLETE ⚠️'}\n`;
    markdown += `**Overall Quality Score**: ${validation.overall_quality_score}/100\n`;
    markdown += `**Timestamp**: ${doc.timestamp}\n\n`;
    markdown += `---\n\n`;

    // Overview
    markdown += `## Business Overview\n\n`;
    markdown += `**Feature**: ${doc.feature_full_name}\n\n`;
    markdown += `**Business Objective**:\n${doc.overview.business_objective}\n\n`;

    markdown += `**Affected Stakeholders**:\n`;
    for (const stakeholder of doc.overview.affected_stakeholders || []) {
      markdown += `- ${stakeholder}\n`;
    }
    markdown += `\n`;

    markdown += `**Key Business Processes**:\n`;
    for (const process of doc.overview.key_processes || []) {
      markdown += `- ${process}\n`;
    }
    markdown += `\n`;

    if (doc.overview.regulatory_context) {
      markdown += `**Regulatory Context**:\n${doc.overview.regulatory_context}\n\n`;
    }

    markdown += `---\n\n`;

    // Summary Statistics
    markdown += `## Summary Statistics\n\n`;
    markdown += `**Business Rules Enhanced**: ${(doc.business_rules_enhanced || []).length}\n`;
    markdown += `**Business Processes Documented**: ${(doc.business_processes || []).length}\n`;
    markdown += `**Glossary Terms**: ${(doc.glossary || []).length}\n`;
    markdown += `**Departments Involved**: ${(doc.stakeholder_analysis.departments || []).length}\n`;
    markdown += `**Stakeholder Responsibilities**: ${(doc.stakeholder_analysis.responsibilities || []).length}\n\n`;

    markdown += `**Quality Metrics**:\n`;
    markdown += `- Documentation Completeness: ${validation.gate_1_documentation_completeness?.percentage?.toFixed(1) || 'N/A'}%\n`;
    markdown += `- Terminology Consistency: ${validation.gate_2_terminology_consistency?.percentage?.toFixed(1) || 'N/A'}%\n`;
    markdown += `- Stakeholder Coverage: ${validation.gate_3_stakeholder_coverage?.percentage?.toFixed(1) || 'N/A'}%\n`;
    markdown += `- Process Quality: ${validation.gate_4_process_quality?.percentage?.toFixed(1) || 'N/A'}%\n`;
    markdown += `- Overall Quality Score: ${validation.overall_quality_score}/100\n\n`;

    markdown += `---\n\n`;

    // Validation Results
    markdown += `## Validation Results\n\n`;
    markdown += `| Gate | Status | Score | Details |\n`;
    markdown += `|------|--------|-------|----------|\n`;

    const gates = [
      { name: 'Documentation Completeness', key: 'gate_1_documentation_completeness' },
      { name: 'Terminology Consistency', key: 'gate_2_terminology_consistency' },
      { name: 'Stakeholder Coverage', key: 'gate_3_stakeholder_coverage' },
      { name: 'Process Quality', key: 'gate_4_process_quality' },
      { name: 'Schema Validation', key: 'gate_5_schema_validation' }
    ];

    for (const gate of gates) {
      const gateData = validation[gate.key] || {};
      const status = gateData.status === 'PASSED' ? '✅ PASSED' : '❌ FAILED';
      const score = gateData.percentage ? `${gateData.percentage.toFixed(1)}%` : 'N/A';
      const details = gateData.details || '';
      markdown += `| ${gate.name} | ${status} | ${score} | ${details} |\n`;
    }

    markdown += `\n**Overall Status**: ${validation.overall_status}\n`;
    markdown += `**Overall Quality Score**: ${validation.overall_quality_score}/100\n\n`;

    markdown += `---\n\n`;

    // Business Processes
    markdown += `## Business Processes\n\n`;
    for (const process of doc.business_processes || []) {
      markdown += `### ${process.process_name}\n\n`;
      markdown += `**Flow**: ${process.business_flow}${process.kcode ? ` (KCODE ${process.kcode})` : ''}\n\n`;

      if (process.process_steps && process.process_steps.length > 0) {
        markdown += `**Process Steps**:\n`;
        process.process_steps.forEach((step, idx) => {
          markdown += `${idx + 1}. ${step}\n`;
        });
        markdown += `\n`;
      }

      if (process.decision_criteria && process.decision_criteria.length > 0) {
        markdown += `**Decision Criteria**:\n`;
        for (const decision of process.decision_criteria) {
          markdown += `- **${decision.decision}**: ${decision.criteria}\n`;
          if (decision.outcomes) {
            markdown += `  - Yes: ${decision.outcomes.yes || 'N/A'}\n`;
            markdown += `  - No: ${decision.outcomes.no || 'N/A'}\n`;
          }
        }
        markdown += `\n`;
      }

      if (process.exception_scenarios && process.exception_scenarios.length > 0) {
        markdown += `**Exception Scenarios**:\n`;
        for (const exception of process.exception_scenarios) {
          markdown += `- **${exception.scenario}**: ${exception.handling}\n`;
        }
        markdown += `\n`;
      }

      if (process.sla_constraints) {
        markdown += `**SLA Constraints**: ${process.sla_constraints}\n\n`;
      }

      if (process.rules_applied && process.rules_applied.length > 0) {
        markdown += `**Rules Applied**: ${process.rules_applied.join(', ')}\n\n`;
      }

      markdown += `---\n\n`;
    }

    // Enhanced Business Rules (summary table)
    markdown += `## Enhanced Business Rules Summary\n\n`;
    markdown += `Total rules enhanced: ${(doc.business_rules_enhanced || []).length}\n\n`;

    if ((doc.business_rules_enhanced || []).length > 0) {
      markdown += `| Rule ID | Business Objective | Business Owner | Customer Impact |\n`;
      markdown += `|---------|-------------------|----------------|------------------|\n`;

      for (const rule of doc.business_rules_enhanced || []) {
        const objective = (rule.business_objective || '').substring(0, 60) + (rule.business_objective?.length > 60 ? '...' : '');
        const owner = rule.business_owner || 'N/A';
        const impact = (rule.customer_impact || '').substring(0, 50) + (rule.customer_impact?.length > 50 ? '...' : '');
        markdown += `| ${rule.rule_id} | ${objective} | ${owner} | ${impact} |\n`;
      }
      markdown += `\n`;
    }

    markdown += `---\n\n`;

    // Stakeholder Analysis
    markdown += `## Stakeholder Analysis\n\n`;

    if ((doc.stakeholder_analysis.departments || []).length > 0) {
      markdown += `### Departments\n\n`;
      for (const dept of doc.stakeholder_analysis.departments || []) {
        markdown += `**${dept.name}**\n`;
        markdown += `- Role: ${dept.role}\n`;
        if (dept.rules_owned && dept.rules_owned.length > 0) {
          markdown += `- Owns: ${dept.rules_owned.join(', ')}\n`;
        }
        markdown += `\n`;
      }
    }

    if ((doc.stakeholder_analysis.responsibilities || []).length > 0) {
      markdown += `### Responsibilities\n\n`;
      for (const resp of doc.stakeholder_analysis.responsibilities || []) {
        markdown += `- **${resp.responsibility}** (Owner: ${resp.owner})\n`;
        if (resp.escalation_path) {
          markdown += `  - Escalation: ${resp.escalation_path}\n`;
        }
      }
      markdown += `\n`;
    }

    if ((doc.stakeholder_analysis.communication_channels || []).length > 0) {
      markdown += `### Communication Channels\n\n`;
      for (const channel of doc.stakeholder_analysis.communication_channels || []) {
        markdown += `- **${channel.purpose}**: ${channel.channel}`;
        if (channel.frequency) {
          markdown += ` (${channel.frequency})`;
        }
        markdown += `\n`;
      }
      markdown += `\n`;
    }

    markdown += `---\n\n`;

    // Impact Analysis
    markdown += `## Impact Analysis\n\n`;
    markdown += `### Customer Impact\n${doc.impact_analysis.customer_impact}\n\n`;
    markdown += `### Operational Impact\n${doc.impact_analysis.operational_impact}\n\n`;

    if (doc.impact_analysis.regulatory_impact) {
      markdown += `### Regulatory Impact\n${doc.impact_analysis.regulatory_impact}\n\n`;
    }

    if (doc.impact_analysis.financial_impact) {
      markdown += `### Financial Impact\n${doc.impact_analysis.financial_impact}\n\n`;
    }

    if (doc.impact_analysis.risk_assessment) {
      const risks = doc.impact_analysis.risk_assessment;

      if (risks.high_risks && risks.high_risks.length > 0) {
        markdown += `### High Risks\n\n`;
        for (const risk of risks.high_risks) {
          markdown += `- **${risk.risk}**\n`;
          markdown += `  - Mitigation: ${risk.mitigation}\n`;
        }
        markdown += `\n`;
      }

      if (risks.medium_risks && risks.medium_risks.length > 0) {
        markdown += `### Medium Risks\n\n`;
        for (const risk of risks.medium_risks) {
          markdown += `- **${risk.risk}**\n`;
          markdown += `  - Mitigation: ${risk.mitigation}\n`;
        }
        markdown += `\n`;
      }
    }

    markdown += `---\n\n`;

    // Business Glossary
    markdown += `## Business Glossary\n\n`;
    markdown += `Total terms: ${(doc.glossary || []).length}\n\n`;

    if ((doc.glossary || []).length > 0) {
      markdown += `| German Term | English Term | Abbreviation | Definition | Frequency | Used In Rules |\n`;
      markdown += `|-------------|--------------|--------------|------------|-----------|---------------|\n`;

      for (const entry of doc.glossary || []) {
        const definition = (entry.definition || '').substring(0, 40) + (entry.definition?.length > 40 ? '...' : '');
        const abbreviation = entry.abbreviation || '-';
        const frequency = entry.frequency || 0;
        const usedInRules = (entry.used_in_rules || []).length > 3
          ? `${(entry.used_in_rules || []).slice(0, 3).join(', ')}...`
          : (entry.used_in_rules || []).join(', ') || '-';
        markdown += `| ${entry.german_term} | ${entry.english_term} | ${abbreviation} | ${definition} | ${frequency} | ${usedInRules} |\n`;
      }
      markdown += `\n`;
    }

    markdown += `---\n\n`;

    // Recommendations
    markdown += `## Recommendations\n\n`;

    if ((doc.recommendations.migration_strategy || []).length > 0) {
      markdown += `### Migration Strategy\n\n`;
      for (const strategy of doc.recommendations.migration_strategy || []) {
        markdown += `- ${strategy}\n`;
      }
      markdown += `\n`;
    }

    if ((doc.recommendations.risk_mitigation || []).length > 0) {
      markdown += `### Risk Mitigation\n\n`;
      for (const mitigation of doc.recommendations.risk_mitigation || []) {
        markdown += `- ${mitigation}\n`;
      }
      markdown += `\n`;
    }

    if ((doc.recommendations.quality_assurance || []).length > 0) {
      markdown += `### Quality Assurance\n\n`;
      for (const qa of doc.recommendations.quality_assurance || []) {
        markdown += `- ${qa}\n`;
      }
      markdown += `\n`;
    }

    if ((doc.recommendations.stakeholder_actions || []).length > 0) {
      markdown += `### Stakeholder Actions\n\n`;
      for (const action of doc.recommendations.stakeholder_actions || []) {
        markdown += `- **${action.stakeholder}** (Priority: ${action.priority})\n`;
        markdown += `  - Action: ${action.action}\n`;
        if (action.timeline) {
          markdown += `  - Timeline: ${action.timeline}\n`;
        }
      }
      markdown += `\n`;
    }

    if (doc.recommendations.next_phase_readiness) {
      markdown += `### Phase 5 Readiness\n${doc.recommendations.next_phase_readiness}\n\n`;
    }

    markdown += `---\n\n`;

    // Outputs Generated
    markdown += `## Outputs Generated\n\n`;
    markdown += `1. ✅ \`phase4/business-documentation.json\` - Structured business documentation (primary format for LLM consumption)\n`;
    markdown += `2. ✅ \`phase4/PHASE4_SUMMARY.md\` - Human-readable summary (this file)\n`;
    markdown += `3. ✅ \`phase4/doc-quality-report.json\` - Validation report\n\n`;

    markdown += `---\n\n`;

    // Next Steps
    markdown += `## Next Steps\n\n`;
    if (validation.overall_status === 'COMPLETE') {
      markdown += `✅ Phase 4 validation passed with quality score of ${validation.overall_quality_score}/100 (target ≥75)\n`;
      markdown += `✅ All ${(doc.business_rules_enhanced || []).length} business rules enhanced with business context\n`;
      markdown += `✅ Ready to proceed to Phase 5 (Control Flow Mapping)\n\n`;
    } else {
      markdown += `⚠️ Phase 4 validation incomplete with quality score of ${validation.overall_quality_score}/100 (target ≥75)\n`;
      markdown += `⚠️ Review failed validation gates and iterate\n`;
      markdown += `⚠️ Fix identified issues before proceeding to Phase 5\n\n`;
    }

    markdown += `## Inputs Used\n\n`;
    markdown += `- Phase 1: \`${doc.inputs.phase1_analysis}\`\n`;
    markdown += `- Phase 2: \`${doc.inputs.phase2_summary}\`\n`;
    markdown += `- Phase 3: \`${doc.inputs.phase3_ruletable}\`\n`;
    if (doc.inputs.wiki_confluence_available !== undefined) {
      markdown += `- Wiki/Confluence: ${doc.inputs.wiki_confluence_available ? 'Available ✅' : 'Not available ⚠️'}\n`;
    }
    markdown += `\n---\n\n`;

    markdown += `**Phase 4 Status**: ${validation.overall_status === 'COMPLETE' ? 'COMPLETE ✅' : 'INCOMPLETE ⚠️'}\n`;

    return markdown;
  }

  /**
   * Write markdown summary to file
   */
  write(markdown) {
    const outputDir = path.dirname(this.outputPath);
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    fs.writeFileSync(this.outputPath, markdown);
    console.log(`Business documentation summary written to: ${this.outputPath}`);
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
  const required = ['input', 'output'];
  const missing = required.filter(key => !options[key]);

  if (missing.length > 0) {
    console.error('Error: Missing required options:', missing.join(', '));
    console.error('\nUsage:');
    console.error('  node generate-business-summary.js \\');
    console.error('    --input results/NBM/phase4/business-documentation.json \\');
    console.error('    --output results/NBM/phase4/PHASE4_SUMMARY.md');
    process.exit(2);
  }

  try {
    const generator = new BusinessSummaryGenerator(options.input, options.output);
    generator.load();
    const markdown = generator.generate();
    generator.write(markdown);
    process.exit(0);

  } catch (error) {
    console.error('\nError:', error.message);
    process.exit(2);
  }
}

if (require.main === module) {
  main();
}

module.exports = { BusinessSummaryGenerator };
