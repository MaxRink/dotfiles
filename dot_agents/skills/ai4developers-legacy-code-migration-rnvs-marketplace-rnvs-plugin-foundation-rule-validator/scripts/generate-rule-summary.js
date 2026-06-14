#!/usr/bin/env node

/**
 * Business Rule Summary Generator
 *
 * Generates human-readable PHASE3_SUMMARY.md from ruletable.json.
 * Creates markdown tables, statistics, and recommendations for business rules.
 *
 * Usage:
 *   node generate-rule-summary.js \
 *     --input results/NBM/phase3/ruletable.json \
 *     --output results/NBM/phase3/PHASE3_SUMMARY.md
 *
 * Exit Codes:
 *   0 - Success
 *   1 - Error
 */

const fs = require('fs');
const path = require('path');

class RuleSummaryGenerator {
  constructor(inputPath, outputPath) {
    this.inputPath = inputPath;
    this.outputPath = outputPath;
    this.data = null;
  }

  /**
   * Load ruletable.json
   */
  loadRuletable() {
    if (!fs.existsSync(this.inputPath)) {
      throw new Error(`Input file not found: ${this.inputPath}`);
    }

    try {
      const content = fs.readFileSync(this.inputPath, 'utf-8');
      this.data = JSON.parse(content);
    } catch (error) {
      throw new Error(`Failed to parse ruletable.json: ${error.message}`);
    }
  }

  /**
   * Generate markdown summary
   */
  generateSummary() {
    const summary = this.data.summary || {};
    const rules = this.data.rules || [];
    const recommendations = this.data.recommendations || {};
    const validation = this.data.validation_report || null;

    let md = '';

    // Header
    md += `# Phase 3 Summary: ${this.data.feature_name || 'Unknown Feature'}\n\n`;

    // Status
    const status = validation && validation.overall_status === 'COMPLETE' ? 'COMPLETE ✅' : 'IN PROGRESS ⚠️';
    const qualityScore = validation ? validation.overall_quality_score : 'N/A';
    const timestamp = this.data.timestamp || new Date().toISOString();

    md += `**Status**: ${status}\n`;
    md += `**Overall Quality Score**: ${qualityScore}/100\n`;
    md += `**Timestamp**: ${timestamp}\n\n`;

    md += `---\n\n`;

    // Summary Statistics
    md += `## Summary Statistics\n\n`;
    md += `**Total Rules Extracted**: ${summary.total_rules || rules.length}\n\n`;

    // By Type
    if (summary.by_type) {
      md += `**By Type**:\n`;
      md += `- Validation Rules: ${summary.by_type.validation || 0}\n`;
      md += `- Business Logic Rules: ${summary.by_type.business_logic || 0}\n`;
      md += `- Integration Rules: ${summary.by_type.integration || 0}\n`;
      md += `- Compliance Rules: ${summary.by_type.compliance || 0}\n\n`;
    }

    // By Confidence
    if (summary.by_confidence) {
      md += `**By Confidence**:\n`;
      md += `- Very High (5): ${summary.by_confidence.very_high || 0}\n`;
      md += `- High (4): ${summary.by_confidence.high || 0}\n`;
      md += `- Medium (3): ${summary.by_confidence.medium || 0}\n`;
      md += `- Low (2): ${summary.by_confidence.low || 0}\n`;
      md += `- Very Low (1): ${summary.by_confidence.very_low || 0}\n\n`;
    }

    // By Flow (if available)
    if (summary.by_flow && Object.keys(summary.by_flow).length > 0) {
      md += `**By Business Flow**:\n`;
      for (const [flow, count] of Object.entries(summary.by_flow)) {
        md += `- ${flow}: ${count} rules\n`;
      }
      md += `\n`;
    }

    // Quality Metrics (if validation report available)
    if (summary.quality_metrics) {
      md += `**Quality Metrics**:\n`;
      md += `- Rule Completeness: ${summary.quality_metrics.rule_completeness}%\n`;
      md += `- Confidence Quality: ${summary.quality_metrics.confidence_quality}%\n`;
      md += `- Source Traceability: ${summary.quality_metrics.source_traceability}%\n`;
      md += `- Categorization Completeness: ${summary.quality_metrics.categorization_completeness}%\n`;
      md += `- Overall Quality Score: ${summary.quality_metrics.overall_quality_score}/100\n\n`;
    }

    md += `---\n\n`;

    // Validation Results (if available)
    if (validation) {
      md += `## Validation Results\n\n`;
      md += `| Gate | Status | Score | Details |\n`;
      md += `|------|--------|-------|----------|\n`;

      const gates = validation.validation_gates || {};

      if (gates.gate_1_rule_completeness) {
        const g1 = gates.gate_1_rule_completeness;
        md += `| **Gate 1: Rule Completeness** | ${g1.status} | ${g1.percentage}% | ${g1.components_with_rules}/${g1.components_in_phase1} components, ${g1.flows_with_rules}/${g1.flows_in_phase2} flows |\n`;
      }

      if (gates.gate_2_confidence_quality) {
        const g2 = gates.gate_2_confidence_quality;
        md += `| **Gate 2: Confidence Quality** | ${g2.status} | ${g2.percentage}% | ${g2.high_confidence_rules}/${g2.total_rules} high confidence rules |\n`;
      }

      if (gates.gate_3_source_traceability) {
        const g3 = gates.gate_3_source_traceability;
        md += `| **Gate 3: Source Traceability** | ${g3.status} | ${g3.percentage}% | ${g3.rules_with_valid_sources}/${g3.total_rules} rules with valid sources |\n`;
      }

      if (gates.gate_4_categorization_completeness) {
        const g4 = gates.gate_4_categorization_completeness;
        md += `| **Gate 4: Categorization** | ${g4.status} | ${g4.percentage}% | ${g4.rules_fully_categorized}/${g4.total_rules} fully categorized |\n`;
      }

      if (gates.gate_5_json_schema) {
        const g5 = gates.gate_5_json_schema;
        md += `| **Gate 5: JSON Schema** | ${g5.status} | - | ${g5.valid_json ? 'Valid JSON' : 'Invalid JSON'} |\n`;
      }

      md += `\n`;
      md += `**Overall Status**: ${validation.overall_status}\n`;
      md += `**Overall Quality Score**: ${validation.overall_quality_score}/100\n\n`;

      md += `---\n\n`;
    }

    // Business Rules Table
    md += `## Business Rules Table\n\n`;

    if (rules.length === 0) {
      md += `*No rules extracted yet.*\n\n`;
    } else {
      md += `| Rule ID | Description | Type | Confidence | Business Impact | Source | Flow |\n`;
      md += `|---------|-------------|------|------------|-----------------|--------|------|\n`;

      for (const rule of rules) {
        const ruleId = rule.rule_id || 'Unknown';
        const description = this.truncate(rule.description || '', 80);
        const type = rule.type || 'Unknown';
        const confidence = rule.confidence || '?';
        const impact = rule.business_impact || '?';
        const source = this.truncate(rule.source_location || 'Unknown', 40);
        const flow = this.truncate(rule.business_flow || 'N/A', 30);

        md += `| ${ruleId} | ${description} | ${type} | ${confidence} | ${impact} | ${source} | ${flow} |\n`;
      }

      md += `\n`;
    }

    md += `---\n\n`;

    // Recommendations
    md += `## Recommendations\n\n`;

    if (recommendations.rules_needing_validation && recommendations.rules_needing_validation.length > 0) {
      md += `### Rules Needing Validation (Low Confidence)\n\n`;
      recommendations.rules_needing_validation.forEach(rule => {
        md += `- ${rule}\n`;
      });
      md += `\n`;
    }

    if (recommendations.critical_rules && recommendations.critical_rules.length > 0) {
      md += `### Critical Rules for Testing\n\n`;
      recommendations.critical_rules.forEach(rule => {
        md += `- ${rule}\n`;
      });
      md += `\n`;
    }

    if (recommendations.compliance_rules && recommendations.compliance_rules.length > 0) {
      md += `### Compliance Rules (Regulatory)\n\n`;
      recommendations.compliance_rules.forEach(rule => {
        md += `- ${rule}\n`;
      });
      md += `\n`;
    }

    if (recommendations.flow_coverage) {
      const coverage = recommendations.flow_coverage;
      if (coverage.complete && coverage.complete.length > 0) {
        md += `### Complete Flow Coverage\n\n`;
        coverage.complete.forEach(flow => {
          md += `- ✅ ${flow}\n`;
        });
        md += `\n`;
      }
      if (coverage.partial && coverage.partial.length > 0) {
        md += `### Partial Flow Coverage\n\n`;
        coverage.partial.forEach(flow => {
          md += `- ⚠️ ${flow}\n`;
        });
        md += `\n`;
      }
      if (coverage.missing && coverage.missing.length > 0) {
        md += `### Missing Flow Coverage\n\n`;
        coverage.missing.forEach(flow => {
          md += `- ❌ ${flow}\n`;
        });
        md += `\n`;
      }
    }

    // General recommendations from validation
    if (validation && validation.recommendations) {
      md += `### Validation Recommendations\n\n`;
      validation.recommendations.forEach(rec => {
        md += `- ${rec}\n`;
      });
      md += `\n`;
    }

    md += `---\n\n`;

    // Outputs Generated
    md += `## Outputs Generated\n\n`;
    md += `1. ✅ \`phase3/ruletable.json\` - Structured business rules (primary format for LLM consumption)\n`;
    md += `2. ✅ \`phase3/PHASE3_SUMMARY.md\` - Human-readable summary (this file)\n`;

    if (validation) {
      md += `3. ✅ \`phase3/rule-quality-report.json\` - Validation report\n`;
    }

    md += `\n---\n\n`;

    // Next Steps
    md += `## Next Steps\n\n`;

    if (validation && validation.overall_status === 'COMPLETE') {
      md += `✅ Phase 3 validation passed with quality score of ${validation.overall_quality_score}/100 (target ≥75)\n`;
      md += `✅ All ${rules.length} business rules extracted and validated\n`;
      md += `✅ Ready to proceed to Phase 4 (Business Logic Analysis)\n\n`;
    } else {
      md += `⚠️ Phase 3 validation incomplete - iteration required\n`;
      md += `⚠️ Review failed gates and improve rule extraction\n`;
      md += `⚠️ Re-run validation after fixes\n\n`;
    }

    // Inputs Used
    md += `## Inputs Used\n\n`;

    if (this.data.inputs) {
      md += `- Phase 1: \`${this.data.inputs.phase1_analysis || 'phase1/analysis.json'}\`\n`;
      md += `- Phase 2: \`${this.data.inputs.phase2_summary || 'phase2/PHASE2_SUMMARY.md'}\`\n`;

      if (this.data.inputs.phase2_flows && this.data.inputs.phase2_flows.length > 0) {
        md += `- Phase 2 Flows: ${this.data.inputs.phase2_flows.length} flow diagrams analyzed\n`;
      }
    }

    md += `\n---\n\n`;

    // Footer
    md += `**Phase 3 Status**: ${status}\n`;

    return md;
  }

  /**
   * Truncate string with ellipsis
   */
  truncate(str, maxLength) {
    if (str.length <= maxLength) {
      return str;
    }
    return str.substring(0, maxLength - 3) + '...';
  }

  /**
   * Generate and write summary
   */
  generate() {
    console.log(`Generating summary from: ${this.inputPath}`);

    this.loadRuletable();
    const summary = this.generateSummary();

    // Write summary to output file
    const outputDir = path.dirname(this.outputPath);
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    fs.writeFileSync(this.outputPath, summary, 'utf-8');

    console.log(`Summary written to: ${this.outputPath}`);
    console.log(`\nSummary Stats:`);
    console.log(`  Total Rules: ${this.data.rules.length}`);
    console.log(`  Feature: ${this.data.feature_name}`);

    return summary;
  }
}

// Main execution
function main() {
  const args = process.argv.slice(2);

  // Parse command-line arguments
  const config = {
    input: null,
    output: null
  };

  for (let i = 0; i < args.length; i += 2) {
    const key = args[i];
    const value = args[i + 1];

    switch (key) {
      case '--input':
        config.input = value;
        break;
      case '--output':
        config.output = value;
        break;
    }
  }

  // Validate required parameters
  if (!config.input || !config.output) {
    console.error('Error: Missing required parameters');
    console.error('Usage: node generate-rule-summary.js \\');
    console.error('  --input <path-to-ruletable.json> \\');
    console.error('  --output <path-to-PHASE3_SUMMARY.md>');
    process.exit(1);
  }

  try {
    const generator = new RuleSummaryGenerator(config.input, config.output);
    generator.generate();

    console.log('\n✓ Summary generation complete');
    process.exit(0);

  } catch (error) {
    console.error(`\nSummary generation error: ${error.message}`);
    process.exit(1);
  }
}

// Run if executed directly
if (require.main === module) {
  main();
}

module.exports = { RuleSummaryGenerator };
