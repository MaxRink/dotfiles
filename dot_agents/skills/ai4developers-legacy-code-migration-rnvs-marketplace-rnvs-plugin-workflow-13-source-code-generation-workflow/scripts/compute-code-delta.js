#!/usr/bin/env node

/**
 * compute-code-delta.js
 *
 * Maps Phase 7.1 design changes to actual code files that need to be
 * created or modified. Compares Phase 6 baseline (existing code structure)
 * with Phase 7.1 delta model (required changes).
 *
 * Usage:
 *   node compute-code-delta.js --phase6 <path> --phase7.1 <path> --output <path>
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

  if (!params.phase6 || !params['phase7.1'] || !params.output) {
    console.error('Usage: node compute-code-delta.js --phase6 <path> --phase7.1 <path> --output <path>');
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

// Safe array access with default
function safeArray(value) {
  return Array.isArray(value) ? value : [];
}

// Extract base package from Phase 6 analysis
function extractBasePackage(phase6) {
  // Try to extract from existing code structure
  const serviceMetadata = phase6.service_metadata || {};
  const basePackage = serviceMetadata.base_package ||
                      phase6.base_package ||
                      'de.telekom.vnrm.business';
  return basePackage;
}

// Map endpoint to controller file
function endpointToControllerPath(endpoint, basePackage, existingControllers) {
  const path_parts = (endpoint.path || '').split('/').filter(p => p && !p.startsWith('{'));
  const resource = path_parts[path_parts.length - 1] || 'default';
  const controllerName = capitalize(resource) + 'Controller';

  // Check if controller already exists
  const existingController = existingControllers.find(c =>
    c.name === controllerName || c.handles_path === endpoint.path
  );

  if (existingController) {
    return {
      path: existingController.file_path,
      exists: true,
      controller_name: existingController.name
    };
  }

  // Generate new controller path
  const packagePath = basePackage.replace(/\./g, '/');
  return {
    path: `src/main/java/${packagePath}/controller/${controllerName}.java`,
    exists: false,
    controller_name: controllerName
  };
}

// Map table to repository file
function tableToRepositoryPath(table, basePackage, existingRepos) {
  const tableName = table.table_name || table.name || 'unknown';
  const entityName = capitalize(camelCase(tableName));
  const repoName = entityName + 'Repository';

  // Check if repository already exists
  const existingRepo = existingRepos.find(r =>
    r.name === repoName || r.entity_name === entityName
  );

  if (existingRepo) {
    return {
      path: existingRepo.file_path,
      exists: true,
      repository_name: existingRepo.name
    };
  }

  const packagePath = basePackage.replace(/\./g, '/');
  return {
    path: `src/main/java/${packagePath}/repository/${repoName}.java`,
    exists: false,
    repository_name: repoName,
    entity_name: entityName
  };
}

// Map event to handler file
function eventToHandlerPath(event, basePackage, existingHandlers) {
  const topicName = event.topic_name || event.name || 'unknown';
  const handlerName = capitalize(camelCase(topicName.replace(/[.-]/g, '_'))) + 'Handler';

  const existingHandler = existingHandlers.find(h =>
    h.name === handlerName || h.handles_topic === topicName
  );

  if (existingHandler) {
    return {
      path: existingHandler.file_path,
      exists: true,
      handler_name: existingHandler.name
    };
  }

  const packagePath = basePackage.replace(/\./g, '/');
  return {
    path: `src/main/java/${packagePath}/event/${handlerName}.java`,
    exists: false,
    handler_name: handlerName
  };
}

// Helper: capitalize first letter
function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

// Helper: convert snake_case to CamelCase
function camelCase(str) {
  return str.split('_').map(capitalize).join('');
}

// Compute files to create (NEW)
function computeFilesToCreate(phase6, phase7_1, basePackage) {
  const filesToCreate = [];
  const existingControllers = safeArray(phase6.api_contracts).flatMap(c => safeArray(c.controllers));
  const existingRepos = safeArray(phase6.database_schema?.repositories);
  const existingHandlers = safeArray(phase6.event_flows?.handlers);

  // New endpoints -> New controllers
  const endpointsToAdd = safeArray(phase7_1.changes?.api_changes?.endpoints_to_add);
  const newControllers = new Map();

  for (const endpoint of endpointsToAdd) {
    const controllerInfo = endpointToControllerPath(endpoint, basePackage, existingControllers);

    if (!controllerInfo.exists) {
      if (!newControllers.has(controllerInfo.path)) {
        newControllers.set(controllerInfo.path, {
          path: controllerInfo.path,
          type: 'controller',
          controller_name: controllerInfo.controller_name,
          endpoints: [],
          source_requirements: []
        });
      }
      const controller = newControllers.get(controllerInfo.path);
      controller.endpoints.push({
        method: endpoint.method,
        path: endpoint.path,
        description: endpoint.description || ''
      });
      if (endpoint.rnvs_source) {
        controller.source_requirements.push(endpoint.rnvs_source);
      }
    }
  }

  filesToCreate.push(...newControllers.values());

  // New tables -> New entities and repositories
  const tablesToAdd = safeArray(phase7_1.changes?.database_changes?.tables_to_add);

  for (const table of tablesToAdd) {
    const repoInfo = tableToRepositoryPath(table, basePackage, existingRepos);

    if (!repoInfo.exists) {
      // Entity file
      const packagePath = basePackage.replace(/\./g, '/');
      filesToCreate.push({
        path: `src/main/java/${packagePath}/entity/${repoInfo.entity_name}.java`,
        type: 'entity',
        entity_name: repoInfo.entity_name,
        table_name: table.table_name || table.name,
        columns: safeArray(table.columns),
        source_requirements: table.rnvs_source ? [table.rnvs_source] : []
      });

      // Repository file
      filesToCreate.push({
        path: repoInfo.path,
        type: 'repository',
        repository_name: repoInfo.repository_name,
        entity_name: repoInfo.entity_name,
        source_requirements: table.rnvs_source ? [table.rnvs_source] : []
      });
    }
  }

  // New Horizon events -> New event handlers
  // NOTE: VNRM uses Horizon (Telekom Event Bus), NOT Kafka
  const topicsToAdd = safeArray(phase7_1.changes?.event_changes?.topics_to_add);

  for (const topic of topicsToAdd) {
    const handlerInfo = eventToHandlerPath(topic, basePackage, existingHandlers);

    if (!handlerInfo.exists) {
      filesToCreate.push({
        path: handlerInfo.path,
        type: 'event_handler',
        handler_name: handlerInfo.handler_name,
        topic_name: topic.topic_name || topic.name,
        source_requirements: topic.rnvs_source ? [topic.rnvs_source] : []
      });
    }
  }

  // DTOs for new endpoints
  for (const endpoint of endpointsToAdd) {
    if (endpoint.request_schema) {
      const dtoName = capitalize(camelCase(endpoint.operation_id || 'default')) + 'Request';
      const packagePath = basePackage.replace(/\./g, '/');
      filesToCreate.push({
        path: `src/main/java/${packagePath}/dto/${dtoName}.java`,
        type: 'dto',
        dto_name: dtoName,
        schema: endpoint.request_schema,
        source_requirements: endpoint.rnvs_source ? [endpoint.rnvs_source] : []
      });
    }
    if (endpoint.response_schema) {
      const dtoName = capitalize(camelCase(endpoint.operation_id || 'default')) + 'Response';
      const packagePath = basePackage.replace(/\./g, '/');
      filesToCreate.push({
        path: `src/main/java/${packagePath}/dto/${dtoName}.java`,
        type: 'dto',
        dto_name: dtoName,
        schema: endpoint.response_schema,
        source_requirements: endpoint.rnvs_source ? [endpoint.rnvs_source] : []
      });
    }
  }

  return filesToCreate;
}

// Compute files to modify (MODIFY)
function computeFilesToModify(phase6, phase7_1, basePackage) {
  const filesToModify = [];
  const existingControllers = safeArray(phase6.api_contracts).flatMap(c => safeArray(c.controllers));
  const existingServices = safeArray(phase6.service_layer?.services);
  const existingRepos = safeArray(phase6.database_schema?.repositories);

  // Modified endpoints -> Modify existing controllers
  const endpointsToModify = safeArray(phase7_1.changes?.api_changes?.endpoints_to_modify);
  const controllerMods = new Map();

  for (const endpoint of endpointsToModify) {
    const controllerInfo = endpointToControllerPath(endpoint, basePackage, existingControllers);

    if (controllerInfo.exists) {
      if (!controllerMods.has(controllerInfo.path)) {
        controllerMods.set(controllerInfo.path, {
          path: controllerInfo.path,
          type: 'controller',
          modifications: []
        });
      }
      const controller = controllerMods.get(controllerInfo.path);
      controller.modifications.push({
        modification_type: 'modify_method',
        method: endpoint.method,
        path: endpoint.path,
        changes: endpoint.changes || 'Update endpoint implementation',
        source_requirement: endpoint.rnvs_source
      });
    }
  }

  filesToModify.push(...controllerMods.values());

  // New endpoints that need to be added to existing controllers
  const endpointsToAdd = safeArray(phase7_1.changes?.api_changes?.endpoints_to_add);

  for (const endpoint of endpointsToAdd) {
    const controllerInfo = endpointToControllerPath(endpoint, basePackage, existingControllers);

    if (controllerInfo.exists) {
      if (!controllerMods.has(controllerInfo.path)) {
        controllerMods.set(controllerInfo.path, {
          path: controllerInfo.path,
          type: 'controller',
          modifications: []
        });
        filesToModify.push(controllerMods.get(controllerInfo.path));
      }
      const controller = controllerMods.get(controllerInfo.path);
      controller.modifications.push({
        modification_type: 'add_method',
        method: endpoint.method,
        path: endpoint.path,
        description: endpoint.description,
        source_requirement: endpoint.rnvs_source
      });
    }
  }

  // New columns -> Modify existing entities
  const columnsToAdd = safeArray(phase7_1.changes?.database_changes?.columns_to_add);
  const entityMods = new Map();

  for (const column of columnsToAdd) {
    const tableName = column.table_name;
    const entityName = capitalize(camelCase(tableName));
    const packagePath = basePackage.replace(/\./g, '/');
    const entityPath = `src/main/java/${packagePath}/entity/${entityName}.java`;

    if (!entityMods.has(entityPath)) {
      entityMods.set(entityPath, {
        path: entityPath,
        type: 'entity',
        modifications: []
      });
    }
    const entity = entityMods.get(entityPath);
    entity.modifications.push({
      modification_type: 'add_column',
      column_name: column.column_name,
      column_type: column.data_type,
      nullable: column.nullable,
      source_requirement: column.rnvs_source
    });
  }

  filesToModify.push(...entityMods.values());

  return filesToModify;
}

// Compute migrations needed
function computeMigrations(phase7_1) {
  const migrations = [];

  // New tables
  const tablesToAdd = safeArray(phase7_1.changes?.database_changes?.tables_to_add);
  if (tablesToAdd.length > 0) {
    migrations.push({
      type: 'flyway',
      version: 'V{N}__add_tables_for_{feature}.sql',
      operations: tablesToAdd.map(t => `CREATE TABLE ${t.table_name || t.name}`),
      tables: tablesToAdd
    });
  }

  // New columns
  const columnsToAdd = safeArray(phase7_1.changes?.database_changes?.columns_to_add);
  if (columnsToAdd.length > 0) {
    migrations.push({
      type: 'flyway',
      version: 'V{N}__add_columns_for_{feature}.sql',
      operations: columnsToAdd.map(c => `ALTER TABLE ${c.table_name} ADD COLUMN ${c.column_name}`),
      columns: columnsToAdd
    });
  }

  // New indexes
  const indexesToAdd = safeArray(phase7_1.changes?.database_changes?.indexes_to_add);
  if (indexesToAdd.length > 0) {
    migrations.push({
      type: 'flyway',
      version: 'V{N}__add_indexes_for_{feature}.sql',
      operations: indexesToAdd.map(i => `CREATE INDEX ${i.index_name} ON ${i.table_name}`),
      indexes: indexesToAdd
    });
  }

  return migrations;
}

// Main execution
function main() {
  const params = parseArgs();

  console.log('🔍 Computing code delta...');
  console.log(`   Phase 6 (baseline): ${params.phase6}`);
  console.log(`   Phase 7.1 (design): ${params['phase7.1']}`);

  // Load inputs
  const phase6 = loadJSON(params.phase6);
  const phase7_1 = loadJSON(params['phase7.1']);

  // Extract base package
  const basePackage = extractBasePackage(phase6);
  console.log(`   Base package: ${basePackage}`);

  // Compute deltas
  const filesToCreate = computeFilesToCreate(phase6, phase7_1, basePackage);
  const filesToModify = computeFilesToModify(phase6, phase7_1, basePackage);
  const migrationsNeeded = computeMigrations(phase7_1);

  // Build delta output
  const delta = {
    computed_at: new Date().toISOString(),
    baseline: {
      source: params.phase6,
      service_name: phase6.service_metadata?.service_name || phase7_1.baseline?.service_name || 'Unknown',
      base_package: basePackage
    },
    design: {
      source: params['phase7.1'],
      feature_name: phase7_1.requirements?.feature_name || phase7_1.feature_name || 'Unknown',
      change_type: phase7_1.change_type || 'ENHANCEMENT'
    },
    files_to_create: filesToCreate,
    files_to_modify: filesToModify,
    migrations_needed: migrationsNeeded
  };

  // Write output
  const outputDir = path.dirname(params.output);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  fs.writeFileSync(params.output, JSON.stringify(delta, null, 2), 'utf-8');

  // Summary
  console.log('✅ Code delta computed successfully');
  console.log(`   Files to create: ${filesToCreate.length}`);
  console.log(`   Files to modify: ${filesToModify.length}`);
  console.log(`   Migrations needed: ${migrationsNeeded.length}`);
  console.log(`   Output: ${params.output}`);

  process.exit(0);
}

// Run if called directly
if (require.main === module) {
  main();
}

module.exports = {
  computeFilesToCreate,
  computeFilesToModify,
  computeMigrations,
  extractBasePackage
};
