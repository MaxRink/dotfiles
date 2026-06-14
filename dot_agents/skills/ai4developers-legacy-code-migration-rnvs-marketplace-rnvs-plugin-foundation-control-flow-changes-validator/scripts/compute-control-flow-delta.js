#!/usr/bin/env node
/**
 * Compute Control Flow Delta
 *
 * Analyzes Phase 7.1 microservice changes to determine which control flows
 * need to be added or modified.
 *
 * Input:
 *   --phase7.1: Phase 7.1 microservice-changes-design.json (what microservices changed)
 *   --phase5: Phase 5 control-flow-mapping.json (RNVS → VNRM flow requirements)
 *   --output: Output file path for computed-control-flow-delta.json
 *
 * Output: computed-control-flow-delta.json with control flow changes needed
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

// Slugify use case name for diagram filename
function slugify(text) {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

// Extract participants from a use case and endpoint
function extractParticipants(useCase, endpoint) {
  const participants = new Set();

  // Add the service from the endpoint
  if (endpoint.service_name) {
    participants.add(endpoint.service_name);
  }

  // Extract participants from use case if available
  if (useCase.participants) {
    useCase.participants.forEach(p => participants.add(p));
  }

  // Extract from microservices_involved if available
  if (useCase.microservices_involved) {
    useCase.microservices_involved.forEach(p => participants.add(p));
  }

  return Array.from(participants);
}

// Find use cases that involve a specific service
function findUseCasesForService(serviceName, controlFlowMapping) {
  const useCases = [];

  if (controlFlowMapping.use_cases) {
    for (const useCase of controlFlowMapping.use_cases) {
      const involved = useCase.microservices_involved || useCase.participants || [];
      if (involved.some(s => s.includes(serviceName) || serviceName.includes(s))) {
        useCases.push(useCase);
      }
    }
  }

  // Also check control_flows array
  if (controlFlowMapping.control_flows) {
    for (const flow of controlFlowMapping.control_flows) {
      const involved = flow.services || flow.participants || [];
      if (involved.some(s => s.includes(serviceName) || serviceName.includes(s))) {
        useCases.push({
          name: flow.name || flow.flow_name,
          description: flow.description,
          microservices_involved: involved
        });
      }
    }
  }

  return useCases;
}

// Check if a new endpoint warrants a new sequence diagram
function shouldCreateNewSequence(endpoint) {
  // POST/PUT endpoints usually represent new use cases
  if (endpoint.method === 'POST' && !endpoint.path.includes('{')) {
    return true;
  }
  // If marked as new use case
  if (endpoint.is_new_use_case) {
    return true;
  }
  return false;
}

// Generate interaction strings for an endpoint
function generateInteractions(endpoint) {
  const interactions = [];
  const method = endpoint.method || 'POST';
  const path = endpoint.path || '/unknown';
  const service = endpoint.service_name || 'service';

  interactions.push({
    from: 'client',
    to: service,
    message: `${method} ${path}`,
    type: 'request'
  });

  interactions.push({
    from: service,
    to: 'client',
    message: endpoint.response_description || 'response',
    type: 'response'
  });

  return interactions;
}

// Check if changes require a saga (distributed transaction)
function requiresDistributedTransaction(microserviceChanges) {
  const changes = microserviceChanges.changes || {};

  // Check if multiple services are involved in transactional operations
  const servicesInvolved = new Set();

  if (changes.api_changes?.endpoints_to_add) {
    changes.api_changes.endpoints_to_add.forEach(ep => {
      if (ep.service_name) servicesInvolved.add(ep.service_name);
      if (ep.calls_services) {
        ep.calls_services.forEach(s => servicesInvolved.add(s));
      }
    });
  }

  if (changes.dependency_changes?.new_internal_dependencies) {
    changes.dependency_changes.new_internal_dependencies.forEach(dep => {
      if (dep.target_service) servicesInvolved.add(dep.target_service);
    });
  }

  // If 2+ services with transactional operations, saga is needed
  return servicesInvolved.size >= 2 && changes.database_changes?.tables_to_add?.length > 0;
}

// Determine saga name based on changes
function determineSagaName(microserviceChanges) {
  const baseline = microserviceChanges.baseline || {};
  return `${baseline.service_name || 'service'}-saga`;
}

// Check if table has complex business logic
function hasComplexBusinessLogic(table) {
  // Tables with many business rules or complex constraints need activity diagrams
  if (table.business_rules_count > 3) return true;
  if (table.constraints?.length > 3) return true;
  if (table.complex_validation) return true;
  return false;
}

// Main function
function main() {
  const args = parseArgs();

  // Validate arguments
  if (!args['phase7.1'] || !args.phase5 || !args.output) {
    console.error('Usage: compute-control-flow-delta.js --phase7.1 <path> --phase5 <path> --output <path>');
    process.exit(2);
  }

  // Read input files
  let microserviceChanges, controlFlowMapping;

  try {
    microserviceChanges = JSON.parse(fs.readFileSync(args['phase7.1'], 'utf8'));
  } catch (e) {
    console.error(`Error reading Phase 7.1 file: ${e.message}`);
    process.exit(2);
  }

  try {
    controlFlowMapping = JSON.parse(fs.readFileSync(args.phase5, 'utf8'));
  } catch (e) {
    console.error(`Error reading Phase 5 file: ${e.message}`);
    process.exit(2);
  }

  // Initialize delta structure
  const delta = {
    baseline: {
      source: 'No baseline - first-time control flow design in CHANGE workflow',
      assumption: 'Phase 8 was not run previously',
      phase7_1_source: args['phase7.1'],
      phase5_source: args.phase5
    },
    requirements: {
      control_flow_mapping: args.phase5,
      microservice_changes: args['phase7.1']
    },
    changes: {
      sequences_to_add: [],
      sequences_to_modify: [],
      activities_to_add: [],
      activities_to_modify: [],
      sagas_to_add: [],
      event_flows_to_modify: []
    },
    computed_at: new Date().toISOString()
  };

  const changes = microserviceChanges.changes || {};

  // Process API endpoint additions
  if (changes.api_changes?.endpoints_to_add) {
    for (const endpoint of changes.api_changes.endpoints_to_add) {
      const affectedUseCases = findUseCasesForService(
        endpoint.service_name || microserviceChanges.baseline?.service_name || 'service',
        controlFlowMapping
      );

      if (shouldCreateNewSequence(endpoint)) {
        delta.changes.sequences_to_add.push({
          diagram_name: `sequence-${slugify(endpoint.operation_id || endpoint.path)}.puml`,
          use_case: endpoint.description || `New ${endpoint.method} endpoint`,
          participants: extractParticipants(affectedUseCases[0] || {}, endpoint),
          rationale: `Phase 7.1 added ${endpoint.method} ${endpoint.path}`,
          source_change: `endpoints_to_add: ${endpoint.operation_id || endpoint.path}`
        });
      } else {
        // Modify existing sequence
        delta.changes.sequences_to_modify.push({
          diagram_name: affectedUseCases[0]?.sequence_diagram || 'sequence-main.puml',
          modifications: {
            new_participants: [endpoint.service_name].filter(Boolean),
            new_interactions: generateInteractions(endpoint),
            rationale: `Add ${endpoint.operation_id || endpoint.method + ' ' + endpoint.path} call`
          }
        });
      }
    }
  }

  // Process API endpoint modifications
  if (changes.api_changes?.endpoints_to_modify) {
    for (const endpoint of changes.api_changes.endpoints_to_modify) {
      delta.changes.sequences_to_modify.push({
        diagram_name: `sequence-${slugify(endpoint.path)}.puml`,
        modifications: {
          type: 'endpoint_schema_change',
          endpoint: `${endpoint.method} ${endpoint.path}`,
          changes: endpoint.schema_changes || 'Request/response schema modified',
          rationale: `Phase 7.1 modified ${endpoint.operation_id || endpoint.path}`
        }
      });
    }
  }

  // Process Kafka topic additions
  if (changes.event_changes?.topics_to_add) {
    for (const topic of changes.event_changes.topics_to_add) {
      delta.changes.event_flows_to_modify.push({
        diagram_name: 'event-architecture.puml',
        new_topics: [topic.topic_name],
        new_subscriptions: (topic.subscriptions_to_add || []).map(s => ({
          consumer: s.consumer_service || s.consumer,
          topic: topic.topic_name
        })),
        rationale: `Phase 7.1 added Kafka topic ${topic.topic_name}`,
        source_change: `topics_to_add: ${topic.topic_name}`
      });
    }
  }

  // Process event subscription additions
  if (changes.event_changes?.subscriptions_to_add) {
    for (const sub of changes.event_changes.subscriptions_to_add) {
      delta.changes.event_flows_to_modify.push({
        diagram_name: 'event-architecture.puml',
        new_subscriptions: [{
          consumer: sub.consumer_service || sub.consumer,
          topic: sub.topic_name || sub.topic
        }],
        rationale: `Phase 7.1 added subscription for ${sub.consumer_service || sub.consumer}`,
        source_change: `subscriptions_to_add: ${sub.consumer_service || sub.consumer}`
      });
    }
  }

  // Process database table additions
  if (changes.database_changes?.tables_to_add) {
    for (const table of changes.database_changes.tables_to_add) {
      if (hasComplexBusinessLogic(table)) {
        delta.changes.activities_to_add.push({
          diagram_name: `activity-${slugify(table.table_name || table.name)}.puml`,
          operation: table.purpose || `${table.table_name || table.name} operations`,
          table_name: table.table_name || table.name,
          rationale: `Phase 7.1 added table ${table.table_name || table.name} with complex business logic`,
          source_change: `tables_to_add: ${table.table_name || table.name}`
        });
      }
    }
  }

  // Process state machine changes
  if (changes.state_machine_changes?.new_states || changes.state_machine_changes?.new_transitions) {
    const states = changes.state_machine_changes.new_states || [];
    const transitions = changes.state_machine_changes.new_transitions || [];

    if (states.length > 0 || transitions.length > 0) {
      delta.changes.activities_to_add.push({
        diagram_name: 'activity-state-transitions.puml',
        operation: 'State machine updates',
        new_states: states.map(s => s.state_name || s.name),
        new_transitions: transitions.map(t => `${t.from_state} → ${t.to_state}`),
        rationale: 'Phase 7.1 added new states/transitions to state machine',
        source_change: 'state_machine_changes'
      });
    }
  }

  // Check for distributed transaction requirements
  if (requiresDistributedTransaction(microserviceChanges)) {
    const baseline = microserviceChanges.baseline || {};
    delta.changes.sagas_to_add.push({
      diagram_name: `saga-${slugify(baseline.service_name || 'service')}.puml`,
      saga_name: determineSagaName(microserviceChanges),
      steps: 3,  // Default estimate
      compensation_required: true,
      rationale: 'Phase 7.1 changes introduce distributed transaction spanning multiple services',
      source_change: 'dependency_changes + database_changes'
    });
  }

  // Write output
  try {
    const outputDir = path.dirname(args.output);
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    fs.writeFileSync(args.output, JSON.stringify(delta, null, 2));
    console.log(`✅ Control flow delta computed: ${args.output}`);
  } catch (e) {
    console.error(`Error writing output file: ${e.message}`);
    process.exit(2);
  }

  // Summary
  const summary = {
    sequences_to_add: delta.changes.sequences_to_add.length,
    sequences_to_modify: delta.changes.sequences_to_modify.length,
    activities_to_add: delta.changes.activities_to_add.length,
    sagas_to_add: delta.changes.sagas_to_add.length,
    event_flows_to_modify: delta.changes.event_flows_to_modify.length
  };

  console.log(`   Sequences to add: ${summary.sequences_to_add}`);
  console.log(`   Sequences to modify: ${summary.sequences_to_modify}`);
  console.log(`   Activities to add: ${summary.activities_to_add}`);
  console.log(`   Sagas to add: ${summary.sagas_to_add}`);
  console.log(`   Event flows to modify: ${summary.event_flows_to_modify}`);

  process.exit(0);
}

main();
