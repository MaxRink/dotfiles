# Cognitive Data Product Templates

This reference provides templates and examples for designing cognitive data products aligned with MARA principles.

## What is a Cognitive Data Product?

A **Cognitive Data Product** is a domain-owned data asset that goes beyond traditional data products by embedding:

- **Semantics** - Business-meaningful schema with ontology mappings
- **Intelligence** - AI-generated features, predictions, risk scores, recommendations
- **Context** - Enrichment with domain knowledge and relationships
- **Governance** - Built-in quality, lineage, compliance, and trust scoring
- **Autonomy** - Self-describing, discoverable, and consumable by AI agents
- **Adaptability** - Continuous learning and improvement from feedback loops

---

## Core Components of a Cognitive Data Product

### 1. Product Identity & Ownership

```yaml
product_name: CustomerChurnPredictor
product_id: CDP-CUST-001
version: 2.3.0
domain: Customer Analytics
owner_team: Customer Insights
owner_email: customer-insights@telekom.de
product_type: Cognitive Analytics Product
classification: Confidential
```

### 2. Business Context

```yaml
business_purpose: |
  Predict customer churn risk and recommend retention actions
  to reduce customer attrition and improve lifetime value.

business_value:
  - Reduce churn rate by 15%
  - Increase customer retention campaign effectiveness by 30%
  - Enable proactive retention with personalized offers

target_consumers:
  - Marketing & Retention Team
  - Customer Care Agents
  - CRM Systems
  - AI Recommendation Engines

use_cases:
  - Proactive retention campaigns
  - Real-time offer personalization
  - Customer care prioritization
  - Predictive analytics dashboards
```

### 3. Semantic Schema

```yaml
ontology_mapping:
  base_ontology: TelecomCustomerOntology_v3
  mapped_entities:
    - Customer (TM_Forum.PartyRole.Customer)
    - Subscription (TM_Forum.Product.Subscription)
    - Device (TM_Forum.Resource.Device)
    - UsagePattern (Custom.Analytics.UsagePattern)

schema:
  entities:
    Customer:
      customer_id: string (UUID, PK)
      customer_segment: enum [Premium, Standard, Basic]
      lifecycle_stage: enum [Acquisition, Growth, Retention, Winback]
      registration_date: timestamp
      last_interaction_date: timestamp

    ChurnSignals:
      customer_id: string (FK → Customer)
      churn_risk_score: float [0.0-1.0]
      churn_probability: float [0.0-1.0]
      churn_likelihood: enum [Low, Medium, High, Critical]
      predicted_churn_date: date (nullable)
      churn_reason_primary: string
      churn_reason_secondary: string (nullable)
      confidence_score: float [0.0-1.0]

  relationships:
    - Customer HAS_CHURN_SIGNALS ChurnSignals (1:1)
    - Customer SUBSCRIBED_TO Plan (1:many)
    - Customer OWNS Device (1:many)
    - Customer LOCATED_IN CoverageZone (1:1)
```

### 4. Data Contract

```yaml
contract:
  sla:
    availability: 99.9%
    latency_p95: 200ms (real-time API)
    latency_batch: 24 hours (daily refresh)
    freshness: 1 hour (streaming updates)
    completeness: 99.5% (required fields)

  quality_guarantees:
    - No null values for customer_id, churn_risk_score
    - churn_risk_score between 0.0 and 1.0
    - confidence_score >= 0.7 for production use
    - Daily validation against ground truth

  schema_evolution:
    compatibility: backward_compatible
    breaking_changes: requires 30-day notice
    versioning: semantic_versioning

  compliance:
    - GDPR compliant (PII masked)
    - Data residency: EU only
    - Retention: 90 days rolling
    - Right to be forgotten: automated
```

### 5. Embedded Features

```yaml
features:
  demographic_features:
    - customer_age_group
    - customer_segment
    - account_tenure_months
    - lifecycle_stage

  usage_features:
    - avg_data_usage_7d (GB)
    - avg_data_usage_30d (GB)
    - avg_voice_minutes_7d
    - avg_voice_minutes_30d
    - avg_sms_count_7d
    - usage_trend (increasing, stable, decreasing)
    - data_speed_avg_mbps

  network_features:
    - call_drop_rate_7d (%)
    - network_quality_score (0-100)
    - coverage_zone_quality
    - service_interruption_count_30d
    - avg_latency_ms

  billing_features:
    - monthly_spend_avg
    - payment_delay_frequency
    - billing_dispute_count_90d
    - plan_change_frequency
    - outstanding_balance

  behavioral_features:
    - customer_care_contact_count_90d
    - complaint_count_90d
    - complaint_severity_avg
    - app_usage_frequency
    - roaming_frequency

  graph_derived_features:
    - social_network_churn_rate (% of contacts who churned)
    - device_upgrade_cycle_position
    - competitor_offer_exposure_score
```

### 6. Predictive Signals (AI-Generated)

```yaml
predictions:
  primary_predictions:
    - churn_risk_score: float (0.0 = no risk, 1.0 = certain churn)
    - churn_probability: float (statistical probability)
    - predicted_churn_date: date (nullable, if probability > 0.7)

  explanatory_signals:
    - churn_reason_primary: string
      values: [network_quality, price_sensitivity, competitor_offer,
               poor_service, device_issue, billing_dispute, other]
    - churn_reason_secondary: string (nullable)
    - contributing_factors: array[string]
      example: ["high_call_drop_rate", "3_recent_complaints", "payment_delay"]

  recommended_actions:
    - retention_action_type: enum [discount_offer, device_upgrade,
                                    service_improvement, customer_care_call]
    - retention_offer_id: string (reference to offer catalog)
    - expected_impact: float (predicted reduction in churn probability)
    - action_priority: enum [low, medium, high, critical]
    - best_contact_channel: enum [sms, email, app_notification, call]
    - best_contact_time: timestamp

  model_metadata:
    - model_name: "ChurnPredictorV2.3"
    - model_type: "GradientBoosting + GraphNN"
    - training_date: timestamp
    - training_data_size: 5M customers
    - validation_accuracy: 0.89
    - precision: 0.87
    - recall: 0.84
    - feature_importance_top5: array[string]
```

### 7. Quality Gates & Trust Scoring

```yaml
quality_gates:
  ingestion_validation:
    - schema_conformance: true
    - completeness_check: >= 99.5%
    - duplicate_detection: true
    - anomaly_detection: true

  processing_validation:
    - feature_distribution_check: true
    - data_drift_detection: true
    - model_performance_monitoring: true
    - bias_fairness_check: true

  output_validation:
    - prediction_range_check: true (0.0-1.0)
    - confidence_threshold: >= 0.7
    - explanation_completeness: true
    - recommendation_validity: true

trust_score:
  calculation:
    - data_quality_score: 0.95 (completeness, accuracy, consistency)
    - model_performance_score: 0.89 (accuracy, precision, recall)
    - sla_compliance_score: 0.98 (availability, latency)
    - consumer_satisfaction_score: 4.2/5.0 (user ratings)

  overall_trust_score: 0.91 (weighted average)
  trust_level: HIGH
  last_updated: 2025-11-07T10:30:00Z
```

### 8. Lineage & Observability

```yaml
lineage:
  source_systems:
    - system: CRM
      entities: [Customer, Subscription, Interaction]
      refresh_frequency: real-time (CDC)

    - system: OSS
      entities: [NetworkMetrics, QoS, CellTower]
      refresh_frequency: 5 minutes

    - system: BSS
      entities: [Billing, Payment, Invoice]
      refresh_frequency: daily

  transformations:
    - stage: bronze (raw ingestion)
      location: s3://datalake/bronze/customer/
      format: parquet

    - stage: silver (cleansed & validated)
      location: s3://datalake/silver/customer360/
      transformations: [deduplication, validation, enrichment]

    - stage: gold (curated & cognitive)
      location: s3://datalake/gold/churn_predictor/
      transformations: [feature_engineering, ml_inference, semantic_enrichment]

  dependencies:
    upstream_products:
      - Customer360BaseProduct
      - NetworkQualityProduct
      - BillingHistoryProduct

    downstream_consumers:
      - RetentionCampaignOrchestrator
      - CRMInsightsAPI
      - CustomerCareDashboard

observability:
  metrics:
    - data_volume: 2.5M records/day
    - processing_time_p95: 180 seconds
    - prediction_latency_p95: 150ms
    - error_rate: 0.02%

  monitoring:
    - data_quality_alerts: enabled
    - model_drift_detection: enabled
    - sla_breach_alerts: enabled
    - anomaly_detection: enabled

  dashboards:
    - DataProductHealth: https://monitoring.internal/dp/churn
    - ModelPerformance: https://mlops.internal/models/churn-v2
```

### 9. API / Event Interface

```yaml
consumption_interfaces:
  rest_api:
    endpoint: https://api.data.telekom.de/v1/churn-predictor
    authentication: OAuth2 + mTLS
    rate_limit: 1000 requests/min

    operations:
      - GET /customers/{customer_id}/churn-risk
        response: ChurnRiskResponse
        latency_sla: 200ms p95

      - POST /customers/batch-prediction
        request: CustomerBatch (max 1000)
        response: ChurnRiskBatch
        latency_sla: 5 seconds

      - GET /customers/{customer_id}/retention-recommendation
        response: RetentionRecommendation

  event_streams:
    - topic: telekom.churn.high-risk-detected
      schema: ChurnHighRiskEvent
      frequency: real-time
      format: avro

    - topic: telekom.churn.daily-batch
      schema: ChurnDailyBatch
      frequency: daily 06:00 UTC
      format: parquet

  feature_store_access:
    - feature_group: churn_features_v2
      features: [all usage, billing, network features]
      access: offline (training) + online (inference)

  graphql_api:
    endpoint: https://graph.data.telekom.de/v1
    query: customer360WithChurn(customerId: String!)

access_control:
  rbac:
    - role: data_scientist
      permissions: [read_features, read_predictions, read_metadata]

    - role: marketing_team
      permissions: [read_predictions, read_recommendations]

    - role: customer_care
      permissions: [read_predictions, read_explanations, read_recommendations]

  abac:
    - attribute: customer_segment
      rule: premium_segment_only (for high-touch campaigns)
```

### 10. Feedback Loops

```yaml
feedback_mechanisms:
  outcome_tracking:
    - retention_campaign_results
      source: CRM (campaign_outcome event)
      metrics: [accepted_offer, rejected_offer, no_response]
      frequency: real-time

    - actual_churn_events
      source: CRM (customer_churned event)
      metrics: [churn_date, churn_reason]
      frequency: real-time

    - customer_care_feedback
      source: Care System (resolution_note)
      metrics: [issue_resolved, customer_satisfied]
      frequency: daily

  model_retraining:
    trigger: scheduled (weekly) OR performance_degradation
    training_data: last 90 days + outcome feedback
    validation: hold-out set (20%) + A/B test
    deployment: gradual rollout (canary → 10% → 100%)

  continuous_improvement:
    - feature_engineering:
        AI discovers new features from feedback patterns

    - explanation_refinement:
        Update churn reasons based on actual outcomes

    - recommendation_optimization:
        Learn which retention actions work best for each segment
```

---

## Complete Example: Customer Churn Cognitive Product

```yaml
# Customer Churn Cognitive Data Product
# Version: 2.3.0
# Owner: Customer Analytics Team

product_metadata:
  name: CustomerChurnPredictor
  id: CDP-CUST-001
  version: 2.3.0
  domain: Customer Analytics
  owner: customer-insights@telekom.de
  classification: Confidential
  created: 2024-01-15
  last_updated: 2025-11-07

business_context:
  purpose: Predict churn risk and recommend retention actions
  value_drivers:
    - 15% reduction in churn rate
    - 30% improvement in retention campaign ROI
    - Proactive customer engagement
  consumers: [Marketing, Care, CRM, AI Agents]

semantic_schema:
  ontology: TelecomCustomerOntology_v3
  entities:
    - Customer
    - ChurnSignals
    - RetentionRecommendations
  relationships:
    - Customer → HAS_CHURN_SIGNALS → ChurnSignals
    - Customer → RECOMMENDED_ACTION → RetentionRecommendations

data_contract:
  sla:
    availability: 99.9%
    latency_p95: 200ms
    freshness: 1 hour
    completeness: 99.5%
  quality:
    - No nulls in primary predictions
    - Confidence >= 0.7
  compliance:
    - GDPR compliant
    - EU data residency

features:
  categories:
    - demographic: [age, segment, tenure]
    - usage: [data_usage_7d, voice_minutes_7d]
    - network: [call_drop_rate, quality_score]
    - billing: [monthly_spend, payment_delays]
    - behavioral: [complaints, care_contacts]
    - graph: [social_churn_rate, device_cycle]

predictions:
  outputs:
    - churn_risk_score: float [0.0-1.0]
    - churn_reason: string
    - recommended_action: string
    - retention_offer_id: string
  model:
    name: ChurnPredictorV2.3
    type: GradientBoosting + GraphNN
    accuracy: 0.89

quality_gates:
  ingestion: [schema, completeness, anomaly detection]
  processing: [drift, bias check]
  output: [range check, confidence threshold]
  trust_score: 0.91 (HIGH)

lineage:
  sources: [CRM, OSS, BSS]
  transformations: [bronze → silver → gold]
  dependencies:
    upstream: [Customer360, NetworkQuality, BillingHistory]
    downstream: [RetentionOrchestrator, CRMInsights]

interfaces:
  rest_api: https://api.data.telekom.de/v1/churn-predictor
  event_streams: [telekom.churn.high-risk-detected]
  feature_store: churn_features_v2
  graphql: customer360WithChurn query

feedback:
  tracking: [campaign_results, actual_churn, care_feedback]
  retraining: weekly OR performance_degradation
  improvement: [feature discovery, explanation refinement]
```

---

## Template: Network Quality Cognitive Product

```yaml
product_metadata:
  name: NetworkQualityCognitiveProduct
  id: CDP-NET-002
  domain: Network Operations
  owner: network-analytics@telekom.de

business_context:
  purpose: Real-time network quality monitoring with predictive congestion alerts
  value_drivers:
    - Proactive congestion management
    - Improved customer QoS
    - Reduced network incident response time

features:
  - cell_tower_utilization
  - bandwidth_usage_trends
  - packet_drop_rate
  - latency_distribution
  - device_density_per_cell

predictions:
  - congestion_risk_score: float [0.0-1.0]
  - predicted_congestion_time: timestamp
  - impacted_customer_count: integer
  - recommended_action: enum [reroute, capacity_increase, load_balance]
  - root_cause_hypothesis: string

interfaces:
  real_time_api: /v1/network/cell/{cell_id}/quality
  event_stream: telekom.network.congestion-alert
  dashboard: Network Operations Center
```

---

## Template: Fraud Detection Cognitive Product

```yaml
product_metadata:
  name: FraudDetectionCognitiveProduct
  id: CDP-FRD-003
  domain: Security & Fraud
  owner: fraud-analytics@telekom.de

business_context:
  purpose: Real-time fraud detection with risk scoring and auto-blocking
  value_drivers:
    - Reduce fraud losses by 40%
    - Real-time transaction blocking
    - Minimize false positives

features:
  - transaction_amount_deviation
  - location_anomaly_score
  - device_change_frequency
  - sim_swap_indicators
  - usage_pattern_deviation
  - social_graph_risk_score

predictions:
  - fraud_risk_score: float [0.0-1.0]
  - fraud_type: enum [sim_swap, account_takeover, subscription_fraud, roaming_fraud]
  - confidence: float [0.0-1.0]
  - recommended_action: enum [allow, alert, block, review]
  - evidence_summary: array[string]

interfaces:
  real_time_api: /v1/fraud/transaction/score
  event_stream: telekom.fraud.high-risk-detected
  blocking_service: Auto-block on fraud_risk_score > 0.9
```

---

## Template: Revenue Optimization Cognitive Product

```yaml
product_metadata:
  name: RevenueOptimizationCognitiveProduct
  id: CDP-REV-004
  domain: Revenue Management
  owner: revenue-analytics@telekom.de

business_context:
  purpose: Personalized upsell/cross-sell recommendations to maximize ARPU
  value_drivers:
    - 20% increase in upsell conversion
    - Personalized offer targeting
    - Optimized pricing strategies

features:
  - propensity_to_upgrade_score
  - price_sensitivity_index
  - service_usage_headroom
  - competitor_offer_exposure
  - device_upgrade_likelihood

predictions:
  - upsell_propensity_score: float [0.0-1.0]
  - recommended_offer_id: string
  - optimal_price_point: float
  - expected_revenue_lift: float (currency)
  - best_engagement_channel: enum [app, sms, email, call]

interfaces:
  rest_api: /v1/revenue/customer/{id}/recommendations
  reverse_etl: Push to CRM, Marketing Automation
  feature_store: revenue_optimization_features
```

---

## Design Checklist

When designing a cognitive data product, ensure:

### Identity & Ownership

- [ ] Clear product name and ID
- [ ] Defined owner team and contact
- [ ] Version and changelog
- [ ] Classification and security level

### Business Value

- [ ] Clear business purpose and outcomes
- [ ] Identified target consumers
- [ ] Defined use cases
- [ ] Measurable value drivers (KPIs)

### Semantic Design

- [ ] Ontology mapping defined
- [ ] Business-meaningful schema
- [ ] Relationships documented
- [ ] Schema versioning strategy

### Data Contract

- [ ] SLA defined (availability, latency, freshness)
- [ ] Quality guarantees specified
- [ ] Compliance requirements listed
- [ ] Schema evolution policy

### AI/ML Components

- [ ] Features clearly defined and documented
- [ ] Predictions/signals specified
- [ ] Model metadata tracked
- [ ] Explainability embedded

### Quality & Trust

- [ ] Quality gates at each stage
- [ ] Trust scoring implemented
- [ ] Validation rules defined
- [ ] Anomaly detection enabled

### Consumption

- [ ] APIs/events documented
- [ ] Access control defined
- [ ] Rate limits specified
- [ ] Example queries provided

### Governance

- [ ] Lineage tracked end-to-end
- [ ] Dependencies documented
- [ ] Observability enabled
- [ ] Privacy/compliance verified

### Feedback & Learning

- [ ] Outcome tracking mechanism
- [ ] Retraining triggers defined
- [ ] Improvement loops enabled
- [ ] Performance monitoring active

---

## Anti-Patterns to Avoid

### 1. Data Dump Product

**Problem**: Just exposing raw data without curation, semantics, or intelligence
**Solution**: Add semantic schema, features, predictions, and quality gates

### 2. Black Box Predictions

**Problem**: Providing predictions without explanations or confidence scores
**Solution**: Include explainability, feature importance, and confidence metadata

### 3. Static Product

**Problem**: No feedback loops or continuous improvement
**Solution**: Implement outcome tracking and automated retraining

### 4. Schema Chaos

**Problem**: Frequent breaking changes without versioning
**Solution**: Semantic versioning, backward compatibility, consumer notifications

### 5. Governance Afterthought

**Problem**: Adding compliance/quality checks after product is built
**Solution**: Embed governance, lineage, and quality gates from design phase

### 6. Consumer Ignorance

**Problem**: Building product without understanding consumer needs
**Solution**: Co-design with consumers, gather feedback, iterate

### 7. Monolithic Product

**Problem**: One huge product trying to serve all use cases
**Solution**: Decompose into focused, composable products

### 8. SLA Mismatch

**Problem**: Latency/freshness SLAs don't match consumer requirements
**Solution**: Define SLAs based on use cases (real-time vs batch)

---

## Maturity Progression

### Level 1: Basic Data Product

- Structured data with schema
- Basic quality checks
- API or file export
- Manual updates

### Level 2: Curated Data Product

- Business-meaningful schema
- Automated quality gates
- Lineage tracking
- Self-service access

### Level 3: Analytical Data Product

- Pre-computed aggregates and KPIs
- Feature sets for ML
- Performance optimized
- SLA monitoring

### Level 4: Cognitive Data Product

- Embedded AI predictions
- Semantic enrichment
- Explainability included
- Real-time or near-real-time

### Level 5: Autonomous Data Product

- Self-healing quality
- Automated retraining
- Adaptive to feedback
- Agent-consumable
