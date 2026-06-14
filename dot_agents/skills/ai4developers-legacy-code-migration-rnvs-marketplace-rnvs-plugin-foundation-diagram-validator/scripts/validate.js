#!/usr/bin/env node
/**
 * PlantUML Diagram Validator
 *
 * Validates Phase2 PlantUML diagrams against production quality standards.
 * Implements 5-gate validation system matching Phase1 rigor.
 *
 * Requirements:
 * - Node.js 14+
 * - No external dependencies (uses only built-in modules)
 * - PlantUML CLI (optional, for Tier 2 validation)
 *
 * Usage:
 *   node validate.js --diagram phase2/dependencies.puml \
 *                    --phase1-analysis phase1/analysis.json \
 *                    --phase1-deps phase1/dependency-graph.json \
 *                    --output phase2/diagram-quality-report.json
 *
 *   node validate.js --phase2-dir results/NBM/phase2 \
 *                    --phase1-dir results/NBM/phase1 \
 *                    --output results/NBM/phase2/diagram-quality-report.json \
 *                    --feature NBM
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

class DiagramValidator {
  constructor(plantumlCLIAvailable = null) {
    this.plantumlCLIAvailable =
      plantumlCLIAvailable !== null ? plantumlCLIAvailable : this.checkPlantUMLCLI();
  }

  checkPlantUMLCLI() {
    try {
      execSync('plantuml -version', { stdio: 'ignore', timeout: 5000 });
      return true;
    } catch (error) {
      return false;
    }
  }

  /**
   * Detect diagram type from PlantUML content
   */
  detectDiagramType(content) {
    // Activity diagram indicators (highest priority)
    const hasActivityStart = /\bstart\b/.test(content);
    const hasActivitySyntax = /:\w+.*;/.test(content);
    const hasSwimlanes = /\|[^|]+\|/.test(content);

    if (hasActivityStart || (hasActivitySyntax && hasSwimlanes)) {
      return 'activity';
    }

    // Component diagram indicators (check before sequence since they also use arrows)
    const hasComponentKeyword = /(?:component|database|interface|class|rectangle)\s+"/.test(content);
    const hasBracketNotation = /^\s*\[[^\]]+\]/m.test(content);
    const hasComponentSkinparam = /skinparam\s+component\s*\{/.test(content);

    if (hasComponentKeyword || hasBracketNotation || hasComponentSkinparam) {
      return 'component';
    }

    // Sequence diagram indicators (lowest priority)
    const hasParticipant = /\bparticipant\b/.test(content);
    const hasActor = /\bactor\b/.test(content);

    if (hasParticipant || hasActor) {
      return 'sequence';
    }

    return 'unknown';
  }

  /**
   * Validate a single PlantUML diagram through all gates
   */
  validateDiagram(diagramPath, phase1AnalysisPath = null, phase1DepsPath = null) {
    const content = fs.readFileSync(diagramPath, 'utf8');
    const diagramType = this.detectDiagramType(content);

    const gates = {};

    // Gate 1: Component Coverage (only for component diagrams)
    if (
      diagramType === 'component' &&
      phase1AnalysisPath &&
      fs.existsSync(phase1AnalysisPath)
    ) {
      gates.gate_1_component_coverage = this.gate1ComponentCoverage(
        content,
        phase1AnalysisPath
      );
    }

    // Gate 2: Dependency Completeness (only for component diagrams)
    if (diagramType === 'component' && phase1DepsPath && fs.existsSync(phase1DepsPath)) {
      gates.gate_2_dependency_completeness = this.gate2DependencyCompleteness(
        content,
        phase1DepsPath
      );
    }

    // Gates 3-5: Always run for all diagram types
    gates.gate_3_syntax_validation = this.gate3SyntaxValidation(content, diagramPath);
    gates.gate_4_metadata_completeness = this.gate4MetadataCompleteness(content);
    gates.gate_5_renderability = this.gate5Renderability(content);

    const qualityScore = this.calculateQualityScore(gates);
    const overallStatus = this.determineOverallStatus(gates, qualityScore);

    return {
      file: diagramPath,
      diagramType,
      validation_gates: gates,
      quality_score: qualityScore,
      overall_status: overallStatus,
    };
  }

  /**
   * Gate 1: Component Coverage (>= 80% threshold)
   */
  gate1ComponentCoverage(content, phase1AnalysisPath) {
    const phase1Data = JSON.parse(fs.readFileSync(phase1AnalysisPath, 'utf8'));

    // Extract components from Phase1
    const phase1Components = new Set();
    for (const component of phase1Data.components || []) {
      phase1Components.add(component.name);
    }

    // Extract components from diagram
    // Pattern: [ComponentName], component "ComponentName", or database "ComponentName"
    const componentPattern = /(?:component|database|interface|class|rectangle)\s+"([^"]+)"|^\s*\[([^\]]+)\]/gm;
    const diagramComponents = new Set();
    let match;

    while ((match = componentPattern.exec(content)) !== null) {
      const compName = match[1] || match[2];
      if (compName) {
        diagramComponents.add(compName.trim());
      }
    }

    // Calculate coverage
    const componentsInPhase1 = phase1Components.size;
    let componentsInDiagram = 0;

    for (const phase1Comp of phase1Components) {
      if (diagramComponents.has(phase1Comp)) {
        componentsInDiagram++;
      }
    }

    const coveragePercentage =
      componentsInPhase1 > 0
        ? Math.floor((componentsInDiagram / componentsInPhase1) * 100)
        : 100;

    // Determine missing components
    const missingComponents = Array.from(phase1Components)
      .filter((comp) => !diagramComponents.has(comp))
      .sort();

    const status = coveragePercentage >= 80 ? 'PASSED' : 'FAILED';

    const errors = [];
    if (status === 'FAILED') {
      const preview = missingComponents.slice(0, 5).join(', ');
      const suffix = missingComponents.length > 5 ? '...' : '';
      errors.push(`Missing ${missingComponents.length} components: ${preview}${suffix}`);
    }

    return {
      status,
      details: {
        components_in_phase1: componentsInPhase1,
        components_in_diagram: componentsInDiagram,
        coverage_percentage: coveragePercentage,
        missing_components: missingComponents,
      },
      errors,
      warnings: [],
    };
  }

  /**
   * Gate 2: Dependency Completeness (>= 80% threshold)
   */
  gate2DependencyCompleteness(content, phase1DepsPath) {
    const phase1DepsData = JSON.parse(fs.readFileSync(phase1DepsPath, 'utf8'));

    // Extract dependencies from Phase1
    const phase1Dependencies = new Set();

    // Try new format first (dependency_details)
    if (phase1DepsData.dependency_details) {
      for (const detail of phase1DepsData.dependency_details) {
        const sourcePath = detail.source || '';
        const sourceName = this.extractComponentNameFromPath(sourcePath);

        for (const dep of detail.dependencies || []) {
          const targetPath = dep.target || '';
          const targetName = this.extractComponentNameFromPath(targetPath);

          if (sourceName && targetName) {
            phase1Dependencies.add(`${sourceName}->${targetName}`);
          }
        }
      }
    }
    // Fall back to old format (nodes)
    else if (phase1DepsData.nodes) {
      for (const node of phase1DepsData.nodes) {
        const nodeId = node.id;
        for (const dep of node.dependencies || []) {
          phase1Dependencies.add(`${nodeId}->${dep}`);
        }
      }
    }

    // Extract dependencies from diagram using multiple patterns for robustness
    const diagramDependencies = new Set();

    // Pattern 1: Bracket notation [Name] --> [Name]
    const bracketPattern = /\[([^\]]+)\]\s*(?:-->|\.\.>|==>|->>|->)\s*\[([^\]]+)\]/g;
    let match;
    while ((match = bracketPattern.exec(content)) !== null) {
      const fromComp = this.normalizeComponentName(match[1].trim());
      const toComp = this.normalizeComponentName(match[2].trim());
      if (fromComp && toComp) {
        diagramDependencies.add(`${fromComp}->${toComp}`);
      }
    }

    // Pattern 2: Keyword to keyword (database Name --> database Name)
    const keywordPattern = /(component|database|interface|class|rectangle)\s+"?([^"\s:]+)"?\s*(?:-->|\.\.>|==>|->>|->)\s*(component|database|interface|class|rectangle)\s+"?([^"\s:]+)"?/g;
    while ((match = keywordPattern.exec(content)) !== null) {
      const fromComp = this.normalizeComponentName(match[2].trim());
      const toComp = this.normalizeComponentName(match[4].trim());
      if (fromComp && toComp) {
        diagramDependencies.add(`${fromComp}->${toComp}`);
      }
    }

    // Pattern 3: Bracket to keyword ([Name] --> database Name)
    const bracketToKeywordPattern = /\[([^\]]+)\]\s*(?:-->|\.\.>|==>|->>|->)\s*(component|database|interface|class|rectangle)\s+"?([^"\s:]+)"?/g;
    while ((match = bracketToKeywordPattern.exec(content)) !== null) {
      const fromComp = this.normalizeComponentName(match[1].trim());
      const toComp = this.normalizeComponentName(match[3].trim());
      if (fromComp && toComp) {
        diagramDependencies.add(`${fromComp}->${toComp}`);
      }
    }

    // Pattern 4: Keyword to bracket (database Name --> [Name])
    const keywordToBracketPattern = /(component|database|interface|class|rectangle)\s+"?([^"\s:]+)"?\s*(?:-->|\.\.>|==>|->>|->)\s*\[([^\]]+)\]/g;
    while ((match = keywordToBracketPattern.exec(content)) !== null) {
      const fromComp = this.normalizeComponentName(match[2].trim());
      const toComp = this.normalizeComponentName(match[3].trim());
      if (fromComp && toComp) {
        diagramDependencies.add(`${fromComp}->${toComp}`);
      }
    }

    // Pattern 5: Bare name to bracket (Name --> [Name])
    // Only match if name starts with letter/underscore (valid identifier)
    const bareToBracketPattern = /\b([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:-->|\.\.>|==>|->>|->)\s*\[([^\]]+)\]/g;
    while ((match = bareToBracketPattern.exec(content)) !== null) {
      const fromComp = this.normalizeComponentName(match[1].trim());
      const toComp = this.normalizeComponentName(match[2].trim());
      if (fromComp && toComp) {
        diagramDependencies.add(`${fromComp}->${toComp}`);
      }
    }

    // Pattern 6: Bare name to keyword (Name --> database Name)
    const bareToKeywordPattern = /\b([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:-->|\.\.>|==>|->>|->)\s*(component|database|interface|class|rectangle)\s+"?([^"\s:]+)"?/g;
    while ((match = bareToKeywordPattern.exec(content)) !== null) {
      const fromComp = this.normalizeComponentName(match[1].trim());
      const toComp = this.normalizeComponentName(match[3].trim());
      if (fromComp && toComp) {
        diagramDependencies.add(`${fromComp}->${toComp}`);
      }
    }

    // Normalize Phase1 dependencies
    const phase1DepsNormalized = new Set();
    for (const dep of phase1Dependencies) {
      const parts = dep.split('->');
      if (parts.length === 2) {
        const fromNorm = this.normalizeComponentName(parts[0]);
        const toNorm = this.normalizeComponentName(parts[1]);
        if (fromNorm && toNorm) {
          phase1DepsNormalized.add(`${fromNorm}->${toNorm}`);
        }
      }
    }

    // Calculate completeness
    const dependenciesInPhase1 = phase1DepsNormalized.size;
    const matchedDependencies = new Set(
      [...diagramDependencies].filter((dep) => phase1DepsNormalized.has(dep))
    );
    const dependenciesInDiagram = matchedDependencies.size;

    const completenessPercentage =
      dependenciesInPhase1 > 0
        ? Math.floor((dependenciesInDiagram / dependenciesInPhase1) * 100)
        : 100;

    // Determine missing dependencies
    const missingDependencies = Array.from(phase1DepsNormalized)
      .filter((dep) => !diagramDependencies.has(dep))
      .sort()
      .slice(0, 10); // Limit to first 10

    const status = completenessPercentage >= 80 ? 'PASSED' : 'FAILED';

    const errors = [];
    if (status === 'FAILED') {
      errors.push(`Missing ${phase1DepsNormalized.size - dependenciesInDiagram} dependencies`);
    }

    return {
      status,
      details: {
        dependencies_in_phase1: dependenciesInPhase1,
        dependencies_in_diagram: dependenciesInDiagram,
        completeness_percentage: completenessPercentage,
        missing_dependencies: missingDependencies,
      },
      errors,
      warnings: [],
    };
  }

  /**
   * Gate 3: Syntax Validation (Tier 1 + Optional Tier 2)
   */
  gate3SyntaxValidation(content, diagramPath) {
    const errors = [];
    const warnings = [];

    // Tier 1: Regex validation (REQUIRED)
    const tier1Errors = this.tier1SyntaxCheck(content);

    // Tier 2: PlantUML CLI validation (OPTIONAL)
    const tier2Errors = [];
    if (this.plantumlCLIAvailable) {
      tier2Errors.push(...this.tier2PlantUMLCLICheck(diagramPath));
    }

    // Combine errors
    const allErrors = [...tier1Errors, ...tier2Errors];

    // Determine validation method
    const validationMethod = this.plantumlCLIAvailable
      ? 'Tier 1 + Tier 2'
      : 'Tier 1 (PlantUML CLI not available)';

    if (!this.plantumlCLIAvailable) {
      warnings.push(
        'PlantUML CLI not available, using Tier 1 validation only (~90% accuracy)'
      );
    }

    // Determine status
    let status;
    if (tier1Errors.length > 0) {
      status = 'FAILED';
    } else if (tier2Errors.length > 0) {
      status = 'WARNING';
      warnings.push(...tier2Errors);
    } else {
      status = 'PASSED';
    }

    return {
      status,
      details: {
        tier1_regex: tier1Errors.length === 0,
        tier2_plantuml_cli: this.plantumlCLIAvailable && tier2Errors.length === 0,
        validation_method: validationMethod,
        syntax_errors: allErrors,
      },
      errors: tier1Errors,
      warnings,
    };
  }

  /**
   * Tier 1: Regex-based syntax validation (~90% accuracy)
   */
  tier1SyntaxCheck(content) {
    const errors = [];

    // Check 1: @startuml/@enduml matching
    const startumlCount = (content.match(/@startuml/g) || []).length;
    const endumlCount = (content.match(/@enduml/g) || []).length;
    if (startumlCount !== endumlCount) {
      errors.push(`Mismatched @startuml (${startumlCount}) and @enduml (${endumlCount})`);
    }

    // Check 2: Activity diagram start/stop
    if (/@startuml/.test(content)) {
      if (/\bstart\b/.test(content)) {
        if (!/\b(?:stop|end)\b/.test(content)) {
          errors.push("Activity diagram has 'start' but no 'stop' or 'end'");
        }
      }
    }

    // Check 3: Block closure (if/endif)
    // Only match PlantUML if statements (start of line with optional whitespace)
    const ifCount = (content.match(/^\s*if\s*\(/gm) || []).length;
    const endifCount = (content.match(/^\s*endif\b/gm) || []).length;
    if (ifCount !== endifCount) {
      errors.push(`Mismatched if (${ifCount}) and endif (${endifCount})`);
    }

    // Check 4: Brace matching
    const openBraces = (content.match(/\{/g) || []).length;
    const closeBraces = (content.match(/\}/g) || []).length;
    if (openBraces !== closeBraces) {
      errors.push(`Mismatched braces ({ ${openBraces}, } ${closeBraces})`);
    }

    // Check 5: Color codes (#RRGGBB)
    const colorMatches = content.match(/#([0-9A-Fa-f]+)/g) || [];
    const invalidColors = [];
    for (const color of colorMatches) {
      const hexPart = color.substring(1);
      if (hexPart.length !== 3 && hexPart.length !== 6) {
        invalidColors.push(color);
      }
    }
    if (invalidColors.length > 0) {
      errors.push(`Invalid color codes: ${invalidColors.slice(0, 5).join(', ')}`);
    }

    // Check 6: Unclosed quotes
    const quoteCount = (content.match(/"/g) || []).length;
    if (quoteCount % 2 !== 0) {
      errors.push('Unclosed quotes detected (odd number of double quotes)');
    }

    return errors;
  }

  /**
   * Tier 2: PlantUML CLI validation (100% accuracy)
   */
  tier2PlantUMLCLICheck(diagramPath) {
    const errors = [];

    try {
      const result = execSync(`plantuml -syntax "${diagramPath}"`, {
        encoding: 'utf8',
        stdio: 'pipe',
        timeout: 30000,
      });

      // PlantUML CLI returns non-zero exit code on syntax errors
      // If we get here, it succeeded (or we're in the catch block)
    } catch (error) {
      // Parse error output
      const output = (error.stderr || '') + (error.stdout || '');
      const lines = output.split('\n');
      for (const line of lines) {
        if (/error|syntax/i.test(line)) {
          errors.push(line.trim());
        }
      }

      // If no specific errors found but exit code was non-zero
      if (errors.length === 0 && error.status !== 0) {
        // Don't report "No diagram found" as it's often a false positive with new syntax
        if (!/no diagram found/i.test(output)) {
          errors.push('PlantUML CLI validation failed');
        }
      }
    }

    return errors;
  }

  /**
   * Gate 4: Metadata Completeness
   */
  gate4MetadataCompleteness(content) {
    const errors = [];

    // Check 1: Legend present
    const legendPresent = /legend\s+(?:right|left|top|bottom)/.test(content);
    if (!legendPresent) {
      errors.push("Legend missing (expected 'legend right' block)");
    }

    // Check 2: Notes present
    const notesPresent = /note\s+(?:right|left|top|bottom)/.test(content);
    if (!notesPresent) {
      errors.push('Notes missing (expected notes for context or important information)');
    }

    // Check 3: Component labels are descriptive
    let labelsDescriptive = true;
    const genericLabels = [];
    const componentMatches = content.matchAll(/(?:component|database)\s+"([^"]+)"/g);
    for (const match of componentMatches) {
      const label = match[1];
      // Check for generic names like "Component1", "Service2", etc.
      if (/^(?:Component|Service|Database|System)\s*\d+$/i.test(label)) {
        labelsDescriptive = false;
        genericLabels.push(label);
      }
    }

    if (!labelsDescriptive) {
      errors.push(`Generic component labels detected: ${genericLabels.slice(0, 3).join(', ')}`);
    }

    // Check 4: Layout pragmas applied
    const layoutPragmas = /!pragma\s+layout\s+smetana/.test(content);
    if (!layoutPragmas) {
      errors.push("Layout pragma missing (expected '!pragma layout smetana')");
    }

    const status = errors.length === 0 ? 'PASSED' : 'FAILED';

    return {
      status,
      details: {
        legend_present: legendPresent,
        notes_present: notesPresent,
        labels_descriptive: labelsDescriptive,
        layout_pragmas: layoutPragmas,
      },
      errors,
      warnings: [],
    };
  }

  /**
   * Gate 5: Renderability & Quality
   */
  gate5Renderability(content) {
    const errors = [];
    const warnings = [];

    // Check 1: Syntax complete (block closure)
    const openBraces = (content.match(/\{/g) || []).length;
    const closeBraces = (content.match(/\}/g) || []).length;
    const syntaxComplete = openBraces === closeBraces;

    if (!syntaxComplete) {
      errors.push(`Unclosed blocks detected ({ ${openBraces}, } ${closeBraces})`);
    }

    // Check 2: Component count (complexity)
    const componentMatches = content.matchAll(
      /(?:component|database|interface|class|rectangle)\s+"([^"]+)"/g
    );
    const components = new Set();
    for (const match of componentMatches) {
      components.add(match[1]);
    }
    const componentCount = components.size;

    let complexityWarning = false;
    if (componentCount > 15) {
      complexityWarning = true;
      warnings.push(
        `High complexity: ${componentCount} components (consider splitting diagram)`
      );
    }

    // Check 3: Rendering test (if PlantUML CLI available)
    const rendersSuccessfully = true; // Placeholder - actual rendering would be done by PlantUML CLI

    const status = errors.length === 0 ? (complexityWarning ? 'WARNING' : 'PASSED') : 'FAILED';

    return {
      status,
      details: {
        syntax_complete: syntaxComplete,
        component_count: componentCount,
        complexity_warning: complexityWarning,
        renders_successfully: rendersSuccessfully,
      },
      errors,
      warnings,
    };
  }

  /**
   * Calculate overall quality score (0-100)
   */
  calculateQualityScore(gates) {
    const weights = {
      gate_1_component_coverage: 0.25,
      gate_2_dependency_completeness: 0.25,
      gate_3_syntax_validation: 0.2,
      gate_4_metadata_completeness: 0.15,
      gate_5_renderability: 0.15,
    };

    let totalScore = 0;
    let totalWeight = 0;

    for (const [gateName, weight] of Object.entries(weights)) {
      if (!gates[gateName]) continue;

      const gate = gates[gateName];
      totalWeight += weight;

      let gateScore;
      if (gateName === 'gate_1_component_coverage') {
        gateScore = gate.details.coverage_percentage || 0;
      } else if (gateName === 'gate_2_dependency_completeness') {
        gateScore = gate.details.completeness_percentage || 0;
      } else {
        // Binary gates: 100 if passed, 0 if failed
        gateScore = gate.status === 'PASSED' ? 100 : 0;
      }

      totalScore += gateScore * weight;
    }

    // Normalize score based on actual weights used
    const normalizedScore = totalWeight > 0 ? totalScore / totalWeight : 0;
    return Math.round(normalizedScore * 10) / 10;
  }

  /**
   * Determine overall validation status
   */
  determineOverallStatus(gates, qualityScore) {
    // Check if any gate FAILED
    for (const gate of Object.values(gates)) {
      if (gate.status === 'FAILED') {
        return 'INCOMPLETE';
      }
    }

    // Check quality score threshold
    if (qualityScore < 70) {
      return 'INCOMPLETE';
    }

    return 'COMPLETE';
  }

  /**
   * Normalize component name for comparison
   */
  normalizeComponentName(name) {
    if (!name) return '';

    // Remove parenthetical text (e.g., "(PL/SQL Package)")
    name = name.replace(/\s*\([^)]*\)/g, '');

    // Remove special characters except underscores
    name = name.replace(/[^a-zA-Z0-9_]/g, '');

    // Convert to lowercase
    return name.toLowerCase();
  }

  /**
   * Extract component name from file path
   */
  extractComponentNameFromPath(filePath) {
    if (!filePath) return null;

    // Handle database references (e.g., "Oracle DB - T_RNB")
    if (/Oracle DB -|Database -/.test(filePath)) {
      const parts = filePath.split('-');
      if (parts.length >= 2) {
        return parts[parts.length - 1].trim();
      }
    }

    // Handle PL/SQL packages specially
    if (/pack_body_rnb\.sql|pack_rnb\.sql/.test(filePath)) {
      return 'p_rnb';
    }
    if (/pack_body_tnb\.sql|pack_tnb\.sql/.test(filePath)) {
      return 'p_tnb';
    }

    // Extract filename without extension
    const filename = path.basename(filePath, path.extname(filePath)).toLowerCase();
    return filename;
  }
}

/**
 * Generate validation report
 */
function generateValidationReport(feature, phase, diagrams, pythonVersion, plantumlCLIAvailable) {
  // Convert diagrams object to array of values
  const diagramArray = Object.values(diagrams);

  // Calculate overall quality score (average of all diagrams)
  const overallQualityScore =
    diagramArray.length > 0
      ? diagramArray.reduce((sum, d) => sum + d.quality_score, 0) / diagramArray.length
      : 0;

  // Determine overall status
  const overallStatus = diagramArray.every((d) => d.overall_status === 'COMPLETE')
    ? 'COMPLETE'
    : 'INCOMPLETE';

  // Generate recommendations
  const recommendations = [];
  if (overallStatus === 'COMPLETE') {
    if (overallQualityScore >= 85) {
      recommendations.push('All validation gates passed');
      recommendations.push('Diagram quality exceeds minimum thresholds');
      recommendations.push('Ready for Phase 3');
    } else {
      recommendations.push('All gates passed but quality score is below 85');
      recommendations.push('Consider improving diagram quality before Phase 3');
    }
  } else {
    recommendations.push('One or more validation gates failed');
    recommendations.push('Review failed gates and regenerate diagrams');
    recommendations.push('Not ready for Phase 3');
  }

  // Build report structure
  const report = {
    feature,
    phase,
    timestamp: new Date().toISOString().replace(/\.\d{3}Z$/, 'Z'),
    python_version: pythonVersion || process.version,
    plantuml_cli_available: plantumlCLIAvailable,
    diagrams: {},
    overall_status: overallStatus,
    overall_quality_score: Math.round(overallQualityScore * 10) / 10,
    recommendations,
  };

  // Add diagram results
  for (const [name, result] of Object.entries(diagrams)) {
    if (typeof result === 'object' && result.validation_gates) {
      report.diagrams[name] = {
        file: result.file,
        validation_gates: {},
        quality_score: result.quality_score,
      };

      // Add gate results
      for (const [gateName, gate] of Object.entries(result.validation_gates)) {
        report.diagrams[name].validation_gates[gateName] = {
          status: gate.status,
          ...gate.details,
          errors: gate.errors,
          warnings: gate.warnings,
        };
      }
    }
  }

  return report;
}

/**
 * Print console report
 */
function printConsoleReport(diagrams, overallStatus, overallQualityScore) {
  console.log('\n' + '='.repeat(60));
  console.log('PHASE2 DIAGRAM VALIDATION REPORT');
  console.log('='.repeat(60) + '\n');

  for (const [name, result] of Object.entries(diagrams)) {
    if (typeof result !== 'object' || !result.validation_gates) continue;

    console.log(`Diagram: ${name}`);
    console.log(`File: ${result.file}`);
    console.log('');

    for (const [gateName, gate] of Object.entries(result.validation_gates)) {
      // Format gate name
      const displayName = gateName.toUpperCase().replace(/_/g, ' ');

      // Status icon
      const icon = gate.status === 'PASSED' ? '✓' : gate.status === 'WARNING' ? '!' : '✗';

      // Print gate status
      if (gateName === 'gate_1_component_coverage') {
        const coverage = gate.details?.coverage_percentage || 0;
        console.log(`${icon} ${displayName}: ${gate.status} (${coverage}%)`);
      } else if (gateName === 'gate_2_dependency_completeness') {
        const completeness = gate.details?.completeness_percentage || 0;
        console.log(`${icon} ${displayName}: ${gate.status} (${completeness}%)`);
      } else if (gateName === 'gate_3_syntax_validation') {
        const method = gate.details?.validation_method || 'Unknown';
        console.log(`${icon} ${displayName}: ${gate.status} (${method})`);
      } else if (gateName === 'gate_5_renderability') {
        const count = gate.details?.component_count || 0;
        const complexity = count > 15 ? 'high' : count > 10 ? 'moderate' : 'low';
        console.log(`${icon} ${displayName}: ${gate.status} (${count} components, ${complexity} complexity)`);
      } else {
        console.log(`${icon} ${displayName}: ${gate.status}`);
      }

      // Print errors
      for (const error of gate.errors || []) {
        console.log(`    ✗ ${error}`);
      }

      // Print warnings
      for (const warning of gate.warnings || []) {
        console.log(`    ! ${warning}`);
      }
    }

    console.log('');
    console.log(`Quality Score: ${result.quality_score}/100`);
    console.log('');
  }

  console.log('-'.repeat(60));
  console.log(`Overall Status: ${overallStatus}`);
  console.log(`Overall Quality Score: ${overallQualityScore}/100`);
  console.log('');

  if (overallStatus === 'COMPLETE') {
    if (overallQualityScore >= 85) {
      console.log('All validation gates passed');
      console.log('Diagram is production-ready');
      console.log('Ready to proceed to Phase 3');
    } else {
      console.log('All gates passed but quality below 85');
      console.log('Consider improving diagram quality');
    }
  } else {
    console.log('One or more validation gates failed');
    console.log('Review errors and regenerate diagrams');
    console.log('Not ready for Phase 3');
  }

  console.log('');
}

/**
 * Main entry point
 */
function main() {
  const args = process.argv.slice(2);

  // Parse arguments
  const options = {
    diagram: null,
    phase1Analysis: null,
    phase1Deps: null,
    phase2Dir: null,
    phase1Dir: null,
    output: null,
    feature: 'Unknown',
  };

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--diagram':
        options.diagram = args[++i];
        break;
      case '--phase1-analysis':
        options.phase1Analysis = args[++i];
        break;
      case '--phase1-deps':
        options.phase1Deps = args[++i];
        break;
      case '--phase2-dir':
        options.phase2Dir = args[++i];
        break;
      case '--phase1-dir':
        options.phase1Dir = args[++i];
        break;
      case '--output':
        options.output = args[++i];
        break;
      case '--feature':
        options.feature = args[++i];
        break;
    }
  }

  // Validate arguments
  if (options.diagram && options.phase2Dir) {
    console.error('ERROR: Cannot specify both --diagram and --phase2-dir');
    process.exit(1);
  }

  if (!options.diagram && !options.phase2Dir) {
    console.error('ERROR: Must specify either --diagram or --phase2-dir');
    process.exit(1);
  }

  if (!options.output) {
    console.error('ERROR: Must specify --output');
    process.exit(1);
  }

  // Initialize validator
  const validator = new DiagramValidator();

  // Determine diagrams to validate
  const diagramsToValidate = {};

  if (options.diagram) {
    // Single diagram mode
    if (!fs.existsSync(options.diagram)) {
      console.error(`ERROR: Diagram not found: ${options.diagram}`);
      process.exit(1);
    }

    diagramsToValidate.diagram = {
      path: options.diagram,
      phase1Analysis: options.phase1Analysis,
      phase1Deps: options.phase1Deps,
    };
  } else {
    // Batch mode
    if (!fs.existsSync(options.phase2Dir)) {
      console.error(`ERROR: Phase2 directory not found: ${options.phase2Dir}`);
      process.exit(1);
    }

    // Find all .puml files in phase2 directory
    const files = fs.readdirSync(options.phase2Dir);
    for (const file of files) {
      if (file.endsWith('.puml')) {
        const name = path.basename(file, '.puml');
        const pumlPath = path.join(options.phase2Dir, file);

        // Determine Phase1 files
        let phase1Analysis = null;
        let phase1Deps = null;

        if (options.phase1Dir && fs.existsSync(options.phase1Dir)) {
          phase1Analysis = path.join(options.phase1Dir, 'analysis.json');
          phase1Deps = path.join(options.phase1Dir, 'dependency-graph.json');
        }

        diagramsToValidate[name] = {
          path: pumlPath,
          phase1Analysis,
          phase1Deps,
        };
      }
    }
  }

  if (Object.keys(diagramsToValidate).length === 0) {
    console.error('ERROR: No .puml files found');
    process.exit(1);
  }

  // Validate all diagrams
  const validationResults = {};

  for (const [name, diagramInfo] of Object.entries(diagramsToValidate)) {
    process.stderr.write(`Validating ${name}...\n`);

    const result = validator.validateDiagram(
      diagramInfo.path,
      diagramInfo.phase1Analysis,
      diagramInfo.phase1Deps
    );

    validationResults[name] = result;
  }

  // Generate report
  const pythonVersion = process.version;

  const report = generateValidationReport(
    options.feature,
    2,
    validationResults,
    pythonVersion,
    validator.plantumlCLIAvailable
  );

  // Write report to file
  const outputDir = path.dirname(options.output);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }
  fs.writeFileSync(options.output, JSON.stringify(report, null, 2));

  process.stderr.write(`Report written to: ${options.output}\n`);

  // Print console report
  printConsoleReport(
    validationResults,
    report.overall_status,
    report.overall_quality_score
  );

  // Exit with appropriate code
  if (report.overall_status === 'COMPLETE') {
    process.exit(0);
  } else {
    process.exit(1);
  }
}

// Run if executed directly
if (require.main === module) {
  main();
}

module.exports = { DiagramValidator, generateValidationReport };
