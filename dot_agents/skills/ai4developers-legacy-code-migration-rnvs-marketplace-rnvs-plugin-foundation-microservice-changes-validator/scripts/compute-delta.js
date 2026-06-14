#!/usr/bin/env node

/**
 * compute-delta.js
 *
 * Compares Phase 6 baseline (existing VNRM microservice) with Phase 5 requirements
 * (RNVS migration needs) to compute the delta (what needs to change).
 *
 * Usage:
 *   node compute-delta.js --phase6 <path> --phase5 <path> --output <path>
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

  if (!params.phase6 || !params.phase5 || !params.output) {
    console.error('Usage: node compute-delta.js --phase6 <path> --phase5 <path> --output <path>');
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

// Compare API endpoints
function computeApiChanges(phase6, phase5) {
  const phase6Endpoints = safeArray(phase6.api_contracts).flatMap(c =>
    safeArray(c.endpoints).map(e => ({
      path: e.path || '',
      method: e.method || '',
      schema: e.request_schema || e.request || {}
    }))
  );

  const phase5Endpoints = safeArray(phase5.component_mappings).flatMap(m =>
    safeArray(m.api_endpoints).map(e => ({
      path: e.path || '',
      method: e.method || '',
      schema: e.request || {},
      description: e.description || '',
      maps_from: e.maps_from || ''
    }))
  );

  const endpoints_to_add = phase5Endpoints.filter(req =>
    !phase6Endpoints.some(existing =>
      existing.path === req.path && existing.method === req.method
    )
  );

  const endpoints_to_modify = phase5Endpoints.filter(req =>
    phase6Endpoints.some(existing =>
      existing.path === req.path &&
      existing.method === req.method &&
      JSON.stringify(existing.schema) !== JSON.stringify(req.schema)
    )
  );

  return {
    endpoints_to_add,
    endpoints_to_modify,
    endpoints_to_deprecate: [] // User specifies manually if needed
  };
}

// Compare database tables
function computeDatabaseChanges(phase6, phase5) {
  const phase6Tables = safeArray(phase6.database_schema?.tables).map(t => t.name || t.table_name || '');

  const phase5Tables = new Set();
  safeArray(phase5.control_flows).forEach(flow => {
    safeArray(flow.vnrm_flow?.database_operations).forEach(op => {
      if (op.table_name) {
        phase5Tables.add(op.table_name);
      }
    });
  });

  const tables_to_add = Array.from(phase5Tables).filter(table =>
    !phase6Tables.includes(table)
  ).map(table => ({
    table_name: table,
    purpose: `Required for ${phase5.feature_name || 'feature'} functionality`,
    source: 'Inferred from Phase 5 database operations'
  }));

  return {
    tables_to_add,
    columns_to_add: [], // Detailed analysis would require schema introspection
    indexes_to_add: []
  };
}

// Compare Kafka events
function computeEventChanges(phase6, phase5) {
  const phase6Topics = safeArray(phase6.event_flows?.topics_published).map(t => t.topic_name || '');

  const phase5Topics = new Set();
  safeArray(phase5.control_flows).forEach(flow => {
    safeArray(flow.vnrm_flow?.events_published).forEach(event => {
      if (event.topic_name) {
        phase5Topics.add(event.topic_name);
      }
    });
  });

  const topics_to_add = Array.from(phase5Topics).filter(topic =>
    !phase6Topics.includes(topic)
  ).map(topic => ({
    topic_name: topic,
    description: `Event for ${phase5.feature_name || 'feature'} functionality`,
    source: 'Inferred from Phase 5 events'
  }));

  // Subscriptions
  const phase6Subscriptions = safeArray(phase6.event_flows?.topics_subscribed).map(t => t.topic_name || '');

  const phase5Subscriptions = new Set();
  safeArray(phase5.control_flows).forEach(flow => {
    safeArray(flow.vnrm_flow?.events_consumed).forEach(event => {
      if (event.topic_name) {
        phase5Subscriptions.add(event.topic_name);
      }
    });
  });

  const subscriptions_to_add = Array.from(phase5Subscriptions).filter(topic =>
    !phase6Subscriptions.includes(topic)
  ).map(topic => ({
    topic_name: topic,
    source_service: 'Unknown - requires analysis',
    description: `Subscription needed for ${phase5.feature_name || 'feature'}`
  }));

  return {
    topics_to_add,
    subscriptions_to_add
  };
}

// Compare state machines
function computeStateMachineChanges(phase6, phase5) {
  const phase6States = safeArray(phase6.state_machines).flatMap(sm =>
    safeArray(sm.states)
  );

  // Infer states from Phase 5 control flows (simplified heuristic)
  const phase5States = new Set();
  safeArray(phase5.control_flows).forEach(flow => {
    if (flow.vnrm_flow?.state_transitions) {
      safeArray(flow.vnrm_flow.state_transitions).forEach(transition => {
        if (transition.from_state) phase5States.add(transition.from_state);
        if (transition.to_state) phase5States.add(transition.to_state);
      });
    }
  });

  const new_states = Array.from(phase5States).filter(state =>
    !phase6States.includes(state)
  );

  return {
    new_states,
    new_transitions: [] // Would require detailed state machine analysis
  };
}

// Compare service dependencies
function computeDependencyChanges(phase6, phase5) {
  const phase6Deps = safeArray(phase6.integration_patterns?.internal_dependencies).map(d =>
    d.target_service || d.service_name || ''
  );

  const phase5Deps = new Set();
  safeArray(phase5.control_flows).forEach(flow => {
    safeArray(flow.vnrm_flow?.microservices).forEach(service => {
      if (service.service_name) {
        phase5Deps.add(service.service_name);
      }
    });
  });

  const new_internal_dependencies = Array.from(phase5Deps).filter(dep =>
    !phase6Deps.includes(dep)
  ).map(dep => ({
    target_service: dep,
    communication_pattern: 'Unknown - requires analysis',
    purpose: `Required for ${phase5.feature_name || 'feature'} integration`
  }));

  return {
    new_internal_dependencies
  };
}

// Main execution
function main() {
  const params = parseArgs();

  console.log('🔍 Computing delta...');
  console.log(`   Phase 6 (baseline): ${params.phase6}`);
  console.log(`   Phase 5 (requirements): ${params.phase5}`);

  // Load inputs
  const phase6 = loadJSON(params.phase6);
  const phase5 = loadJSON(params.phase5);

  // Compute deltas
  const api_changes = computeApiChanges(phase6, phase5);
  const database_changes = computeDatabaseChanges(phase6, phase5);
  const event_changes = computeEventChanges(phase6, phase5);
  const state_machine_changes = computeStateMachineChanges(phase6, phase5);
  const dependency_changes = computeDependencyChanges(phase6, phase5);

  // Build delta output
  const delta = {
    computed_at: new Date().toISOString(),
    baseline: {
      source: params.phase6,
      service_name: phase6.service_metadata?.service_name || 'Unknown',
      service_version: phase6.service_metadata?.service_version || 'Unknown'
    },
    requirements: {
      source: params.phase5,
      feature_name: phase5.feature_name || 'Unknown'
    },
    changes: {
      api_changes,
      database_changes,
      event_changes,
      state_machine_changes,
      dependency_changes
    }
  };

  // Write output
  const outputDir = path.dirname(params.output);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  fs.writeFileSync(params.output, JSON.stringify(delta, null, 2), 'utf-8');

  // Summary
  console.log('✅ Delta computed successfully');
  console.log(`   API changes: +${api_changes.endpoints_to_add.length} ~${api_changes.endpoints_to_modify.length}`);
  console.log(`   Database: +${database_changes.tables_to_add.length} tables`);
  console.log(`   Events: +${event_changes.topics_to_add.length} topics, +${event_changes.subscriptions_to_add.length} subscriptions`);
  console.log(`   States: +${state_machine_changes.new_states.length} states`);
  console.log(`   Dependencies: +${dependency_changes.new_internal_dependencies.length} services`);
  console.log(`   Output: ${params.output}`);

  process.exit(0);
}

// Run if called directly
if (require.main === module) {
  main();
}

module.exports = { computeApiChanges, computeDatabaseChanges, computeEventChanges, computeStateMachineChanges, computeDependencyChanges };
