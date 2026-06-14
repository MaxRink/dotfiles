#!/usr/bin/env node
/**
 * Dependency Map Generator
 *
 * Generates dependency_map.md from Phase1 analysis results.
 * This markdown file is required by Phase3 for migration planning.
 *
 * Requirements:
 * - Node.js 14+
 * - No external dependencies (uses only built-in modules)
 *
 * Usage:
 *   node generate-dependency-map.js --phase1-analysis phase1/analysis.json \
 *                                   --phase1-deps phase1/dependency-graph.json \
 *                                   --output phase2/dependency_map.md \
 *                                   --feature NBM
 */

const fs = require('fs');
const path = require('path');

/**
 * Load Phase1 analysis and dependency graph data
 */
function loadPhase1Data(analysisPath, depsPath) {
  const analysisData = JSON.parse(fs.readFileSync(analysisPath, 'utf8'));
  const depsData = JSON.parse(fs.readFileSync(depsPath, 'utf8'));
  return { analysisData, depsData };
}

/**
 * Extract component information from analysis.json
 *
 * Returns: Object of component_name -> {type, description, files, responsibilities}
 */
function extractComponents(analysisData) {
  const components = {};

  for (const component of analysisData.components || []) {
    const name = component.name;
    components[name] = {
      type: component.type || 'unknown',
      description: component.description || 'No description',
      files: component.files || [],
      responsibilities: component.responsibilities || [],
    };
  }

  return components;
}

/**
 * Extract dependency relationships from dependency-graph.json
 *
 * Returns: Object of component_name -> [list of dependencies]
 */
function extractDependencies(depsData) {
  const dependencies = {};

  for (const node of depsData.nodes || []) {
    const component = node.id;
    const deps = node.dependencies || [];
    if (deps.length > 0) {
      dependencies[component] = deps;
    }
  }

  return dependencies;
}

/**
 * Extract database interactions from components and dependencies
 *
 * Returns: Object of component_name -> [list of databases]
 */
function extractDatabaseInteractions(components, dependencies) {
  // Identify database components
  const databases = new Set(
    Object.entries(components)
      .filter(([name, info]) => info.type === 'database')
      .map(([name]) => name)
  );

  // Find components that depend on databases
  const dbInteractions = {};

  for (const [component, deps] of Object.entries(dependencies)) {
    const dbDeps = deps.filter((dep) => databases.has(dep));
    if (dbDeps.length > 0) {
      dbInteractions[component] = dbDeps;
    }
  }

  return dbInteractions;
}

/**
 * Generate dependency_map.md markdown content
 *
 * Args:
 *   feature: Feature name (e.g., "NBM")
 *   components: Component information
 *   dependencies: Component dependencies
 *   dbInteractions: Database interactions
 *
 * Returns: Markdown content as string
 */
function generateDependencyMapMarkdown(feature, components, dependencies, dbInteractions) {
  const lines = [];

  // Header
  lines.push(`# Dependency Map: ${feature}`);
  lines.push('');
  lines.push('**Generated from Phase1 Analysis**');
  lines.push('');
  lines.push(
    'This document provides a comprehensive mapping of components, their dependencies, and database interactions discovered during Phase1 code analysis.'
  );
  lines.push('');

  // Table of Contents
  lines.push('## Table of Contents');
  lines.push('');
  lines.push('1. [Component Overview](#component-overview)');
  lines.push('2. [Dependency Matrix](#dependency-matrix)');
  lines.push('3. [Database Interactions](#database-interactions)');
  lines.push('4. [Component Details](#component-details)');
  lines.push('');

  // Section 1: Component Overview
  lines.push('## Component Overview');
  lines.push('');
  lines.push(`**Total Components**: ${Object.keys(components).length}`);
  lines.push('');

  // Count by type
  const typeCounts = {};
  for (const info of Object.values(components)) {
    typeCounts[info.type] = (typeCounts[info.type] || 0) + 1;
  }

  lines.push('**Component Types**:');
  lines.push('');
  for (const [compType, count] of Object.entries(typeCounts).sort()) {
    const capitalizedType = compType.charAt(0).toUpperCase() + compType.slice(1);
    lines.push(`- **${capitalizedType}**: ${count}`);
  }
  lines.push('');

  // Component listing table
  lines.push('| Component | Type | Description |');
  lines.push('|-----------|------|-------------|');

  for (const name of Object.keys(components).sort()) {
    const info = components[name];
    const compType = info.type.charAt(0).toUpperCase() + info.type.slice(1);
    let description = info.description;
    // Truncate long descriptions
    if (description.length > 80) {
      description = description.substring(0, 77) + '...';
    }
    lines.push(`| ${name} | ${compType} | ${description} |`);
  }

  lines.push('');

  // Section 2: Dependency Matrix
  lines.push('## Dependency Matrix');
  lines.push('');
  lines.push('This matrix shows which components depend on which other components.');
  lines.push('');

  if (Object.keys(dependencies).length > 0) {
    lines.push('| Component | Depends On | Count |');
    lines.push('|-----------|------------|-------|');

    for (const component of Object.keys(dependencies).sort()) {
      const deps = dependencies[component];
      let depList = deps.sort().join(', ');
      // Truncate long dependency lists
      if (depList.length > 60) {
        depList = depList.substring(0, 57) + '...';
      }
      lines.push(`| ${component} | ${depList} | ${deps.length} |`);
    }

    lines.push('');

    // Dependency statistics
    const totalDeps = Object.values(dependencies).reduce((sum, deps) => sum + deps.length, 0);
    const avgDeps = totalDeps / Object.keys(dependencies).length;

    lines.push('**Dependency Statistics**:');
    lines.push('');
    lines.push(`- **Total Dependencies**: ${totalDeps}`);
    lines.push(`- **Average per Component**: ${avgDeps.toFixed(1)}`);
    lines.push(`- **Components with Dependencies**: ${Object.keys(dependencies).length}`);
    lines.push('');
  } else {
    lines.push('*No dependencies detected*');
    lines.push('');
  }

  // Section 3: Database Interactions
  lines.push('## Database Interactions');
  lines.push('');

  // Identify databases
  const databases = Object.entries(components)
    .filter(([name, info]) => info.type === 'database')
    .map(([name]) => name);

  if (databases.length > 0) {
    lines.push(`**Databases**: ${databases.length}`);
    lines.push('');

    for (const db of databases.sort()) {
      lines.push(`- ${db}`);
    }

    lines.push('');
    lines.push('**Component-Database Interactions**:');
    lines.push('');

    if (Object.keys(dbInteractions).length > 0) {
      lines.push('| Component | Accesses Database(s) |');
      lines.push('|-----------|----------------------|');

      for (const component of Object.keys(dbInteractions).sort()) {
        const dbList = dbInteractions[component].sort().join(', ');
        lines.push(`| ${component} | ${dbList} |`);
      }

      lines.push('');
    } else {
      lines.push('*No database interactions detected*');
      lines.push('');
    }
  } else {
    lines.push('*No databases detected*');
    lines.push('');
  }

  // Section 4: Component Details
  lines.push('## Component Details');
  lines.push('');

  for (const name of Object.keys(components).sort()) {
    const info = components[name];

    // Component header
    lines.push(`### ${name}`);
    lines.push('');

    // Type and description
    const capitalizedType = info.type.charAt(0).toUpperCase() + info.type.slice(1);
    lines.push(`**Type**: ${capitalizedType}`);
    lines.push('');
    lines.push(`**Description**: ${info.description}`);
    lines.push('');

    // Responsibilities
    if (info.responsibilities && info.responsibilities.length > 0) {
      lines.push('**Responsibilities**:');
      lines.push('');
      for (const resp of info.responsibilities) {
        lines.push(`- ${resp}`);
      }
      lines.push('');
    }

    // Dependencies
    if (dependencies[name]) {
      const deps = dependencies[name];
      lines.push(`**Dependencies** (${deps.length}):`);
      lines.push('');
      for (const dep of deps.sort()) {
        lines.push(`- ${dep}`);
      }
      lines.push('');
    } else {
      lines.push('**Dependencies**: None');
      lines.push('');
    }

    // Database interactions
    if (dbInteractions[name]) {
      const dbs = dbInteractions[name];
      lines.push(`**Database Access**: ${dbs.sort().join(', ')}`);
      lines.push('');
    }

    // Files
    if (info.files && info.files.length > 0) {
      const fileCount = info.files.length;
      lines.push(`**Files** (${fileCount}):`);
      lines.push('');
      // Show first 5 files, then "and X more"
      const sortedFiles = info.files.sort();
      for (const filePath of sortedFiles.slice(0, 5)) {
        lines.push(`- \`${filePath}\``);
      }
      if (fileCount > 5) {
        lines.push(`- *... and ${fileCount - 5} more files*`);
      }
      lines.push('');
    }

    // Separator
    lines.push('---');
    lines.push('');
  }

  return lines.join('\n');
}

/**
 * Main entry point
 */
function main() {
  const args = process.argv.slice(2);

  // Parse arguments
  const options = {
    phase1Analysis: null,
    phase1Deps: null,
    output: null,
    feature: null,
  };

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--phase1-analysis':
        options.phase1Analysis = args[++i];
        break;
      case '--phase1-deps':
        options.phase1Deps = args[++i];
        break;
      case '--output':
        options.output = args[++i];
        break;
      case '--feature':
        options.feature = args[++i];
        break;
      case '--help':
        console.log(`
Usage:
  node generate-dependency-map.js --phase1-analysis <path> \\
                                  --phase1-deps <path> \\
                                  --output <path> \\
                                  --feature <name>

Example:
  node generate-dependency-map.js --phase1-analysis results/NBM/phase1/analysis.json \\
                                  --phase1-deps results/NBM/phase1/dependency-graph.json \\
                                  --output results/NBM/phase2/dependency_map.md \\
                                  --feature NBM
`);
        process.exit(0);
        break;
    }
  }

  // Validate required arguments
  if (!options.phase1Analysis) {
    console.error('ERROR: --phase1-analysis is required');
    process.exit(1);
  }
  if (!options.phase1Deps) {
    console.error('ERROR: --phase1-deps is required');
    process.exit(1);
  }
  if (!options.output) {
    console.error('ERROR: --output is required');
    process.exit(1);
  }
  if (!options.feature) {
    console.error('ERROR: --feature is required');
    process.exit(1);
  }

  // Validate input files exist
  if (!fs.existsSync(options.phase1Analysis)) {
    console.error(`ERROR: Phase1 analysis not found: ${options.phase1Analysis}`);
    process.exit(1);
  }

  if (!fs.existsSync(options.phase1Deps)) {
    console.error(`ERROR: Phase1 dependency graph not found: ${options.phase1Deps}`);
    process.exit(1);
  }

  // Load Phase1 data
  process.stderr.write('Loading Phase1 data...\n');
  const { analysisData, depsData } = loadPhase1Data(
    options.phase1Analysis,
    options.phase1Deps
  );

  // Extract information
  process.stderr.write('Extracting components...\n');
  const components = extractComponents(analysisData);

  process.stderr.write('Extracting dependencies...\n');
  const dependencies = extractDependencies(depsData);

  process.stderr.write('Extracting database interactions...\n');
  const dbInteractions = extractDatabaseInteractions(components, dependencies);

  // Generate markdown
  process.stderr.write('Generating dependency_map.md...\n');
  const markdownContent = generateDependencyMapMarkdown(
    options.feature,
    components,
    dependencies,
    dbInteractions
  );

  // Write output
  const outputDir = path.dirname(options.output);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }
  fs.writeFileSync(options.output, markdownContent, 'utf8');

  // Calculate statistics
  const totalDeps = Object.values(dependencies).reduce((sum, deps) => sum + deps.length, 0);
  const totalDbInteractions = Object.values(dbInteractions).reduce(
    (sum, dbs) => sum + dbs.length,
    0
  );

  process.stderr.write(`Dependency map written to: ${options.output}\n`);
  process.stderr.write(`   Components: ${Object.keys(components).length}\n`);
  process.stderr.write(`   Dependencies: ${totalDeps}\n`);
  process.stderr.write(`   Database interactions: ${totalDbInteractions}\n`);
}

// Run if executed directly
if (require.main === module) {
  main();
}

module.exports = {
  loadPhase1Data,
  extractComponents,
  extractDependencies,
  extractDatabaseInteractions,
  generateDependencyMapMarkdown,
};
