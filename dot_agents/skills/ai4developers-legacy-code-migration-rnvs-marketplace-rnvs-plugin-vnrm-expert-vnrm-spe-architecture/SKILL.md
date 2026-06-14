---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-vnrm-expert-vnrm-spe-architecture
description: VNRM SPE (Special Functions) submodule architecture reference covering legacy RNVS integration, communication server, backend automation adapter, and RNVS-to-VNRM migration support. This skill should be used when designing or implementing SPE services in phases 6-12 of the RNVS→VNRM migration workflow.
allowed-tools: Read
user-invocable: false
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/vnrm-expert/skills/vnrm-spe-architecture by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# VNRM SPE Architecture Expert Skill

## Purpose

Provides comprehensive architecture knowledge for the **VNRM SPE (SPECIAL FUNCTIONS)** submodule, which serves as the critical bridge between modern VNRM microservices and legacy RNVS systems, providing database integration, communication management, and backend automation capabilities.

## SPE Submodule Overview

The SPE (SPECIAL FUNCTIONS) submodule provides specialized services for legacy system integration and communication management within VNRM:

### Deployed SPE Services

Based on VNRM production deployment and SLA documentation:

#### Communication Server API
- **spe-coms-communication-server-api** - Communication server API (OT level service)
- Handles communication protocols and message exchange
- Office time support (3-day response, business hours only)
- Integration point for external communication systems

#### Backend Automation Adapter API
- **spe-beaa-backend-automation-adapter-api** - Backend automation adapter API (OT level service)
- Provides automation interfaces for backend systems
- Handles automated workflows and process orchestration
- Office time support (3-day response, business hours only)

#### VNRM-RNVS Database API
- **spe-vnrm-rnvs-db-api** - VNRM to RNVS database integration API (OT level service)
- Critical bridge between modern VNRM and legacy RNVS systems
- Provides data synchronization and migration capabilities
- Office time support (3-day response, business hours only)

## Service Architecture & Dependencies

### Current Deployment Status
Based on VNRM SLA documentation:
- **Service Level**: All SPE services are Office Time (OT) level
- **Support Model**: 3-day response time, business hours only (8h/5d)
- **Support Channels**: ServiceNow + FMB post box
- **Production Status**: Deployed and operational

### Legacy System Integration

#### RNVS Database Integration
The **spe-vnrm-rnvs-db-api** serves as the critical integration layer:
- **Purpose**: Bridge between VNRM microservices and legacy RNVS database
- **Data Flow**: Bidirectional synchronization of number management data
- **Migration Support**: Facilitates gradual migration from RNVS to VNRM
- **Consistency**: Ensures data consistency during transition period

#### Communication Server Functions
The **spe-coms-communication-server-api** provides:
- **Protocol Management**: Support for legacy communication protocols
- **Message Routing**: Route messages between VNRM and external systems
- **Format Translation**: Convert between legacy and modern message formats
- **Error Handling**: Centralized error management for communication failures

#### Backend Automation
The **spe-beaa-backend-automation-adapter-api** enables:
- **Process Automation**: Automated workflows for routine operations
- **System Integration**: Connect VNRM with external automation systems
- **Batch Processing**: Handle bulk operations and data processing
- **Monitoring Integration**: Interface with operational monitoring tools

## Functional Capabilities

### Legacy System Bridge
- **Database Synchronization**: Real-time sync between VNRM and RNVS databases
- **Schema Translation**: Convert between legacy and modern data schemas
- **Transaction Management**: Ensure data consistency across system boundaries
- **Migration Support**: Tools and APIs for gradual system migration

### Communication Management
- **Protocol Support**: Multiple communication protocols (REST, SOAP, legacy protocols)
- **Message Transformation**: Convert message formats between systems
- **Routing Logic**: Intelligent message routing based on content and destination
- **Error Recovery**: Automatic retry and error handling mechanisms

### Automation Services
- **Workflow Execution**: Execute predefined business workflows
- **Event Processing**: React to system events and trigger appropriate actions
- **Batch Operations**: Handle large-scale data operations efficiently
- **Integration APIs**: Provide standardized interfaces for external systems

## Integration Dependencies

### Internal VNRM Dependencies
- **NUM**: Integrates with number management services for data synchronization
- **PRT**: Supports porting workflows through communication and automation services
- **COM**: Uses configuration and reference data services
- **COR**: Integrates with error management for issue resolution

### External System Dependencies
- **Legacy RNVS**: Direct database and application integration
- **External Communication Systems**: Various telecom and business systems
- **Automation Platforms**: Enterprise automation and monitoring tools
- **Operational Systems**: Integration with network and service management

### Platform Dependencies
- Configuration server for service settings and parameters
- Reference data management for validation and business rules
- Centralized logging and monitoring for operational visibility
- Error management integration for fault handling and resolution

## Technical Architecture

### Service Communication Patterns
- **RESTful APIs**: Modern API interfaces for VNRM integration
- **Legacy Protocol Support**: Backward compatibility with RNVS systems
- **Asynchronous Processing**: Event-driven architecture for scalability
- **Database Integration**: Direct database access for data synchronization

### Data Management Patterns
- **Dual-Write Pattern**: Simultaneous updates to VNRM and RNVS systems
- **Event Sourcing**: Capture all changes for audit and replay capabilities
- **CQRS Pattern**: Separate read and write models for performance
- **Saga Pattern**: Manage distributed transactions across system boundaries

### Error Handling & Resilience
- **Circuit Breaker**: Prevent cascade failures in legacy system integration
- **Retry Logic**: Intelligent retry mechanisms with exponential backoff
- **Fallback Strategies**: Alternative approaches when primary systems fail
- **Monitoring**: Comprehensive monitoring of integration health

## Business Use Cases

### RNVS-VNRM Migration Support
- **Gradual Migration**: Support phased migration from RNVS to VNRM
- **Data Consistency**: Maintain data integrity during migration period
- **Fallback Capability**: Ensure business continuity if migration issues occur
- **Validation**: Verify data consistency between old and new systems

### Legacy System Maintenance
- **Continued Operation**: Keep legacy systems operational during transition
- **Data Synchronization**: Ensure RNVS remains current with VNRM changes
- **Reporting**: Generate reports from both legacy and modern data sources
- **Compliance**: Maintain regulatory compliance across both systems

### Communication Integration
- **External Interface**: Provide stable interfaces for external system integration
- **Protocol Translation**: Enable communication between different system generations
- **Message Routing**: Route messages to appropriate systems based on business rules
- **Error Management**: Handle communication failures gracefully

## Service Level Requirements

### Support Classification
All SPE services are classified as **Office Time (OT)**:
- **Response Time**: 3-day response for issues and changes
- **Support Hours**: Business hours only (8h/5d)
- **On-call Duty**: No on-call duty required
- **Escalation**: Standard priority through ServiceNow and FMB post box

### Operational Characteristics
- **Availability**: Business hours operational window
- **Performance**: Standard performance requirements for backend services
- **Scalability**: Designed for steady-state legacy integration workloads
- **Maintenance**: Regular maintenance windows for updates and patches

## Migration Strategy Considerations

### Transition Planning
- **Phased Approach**: Gradual transition from RNVS to VNRM functionality
- **Risk Mitigation**: Minimize business disruption during migration
- **Rollback Plans**: Ability to revert to legacy systems if needed
- **Testing Strategy**: Comprehensive testing of integration points

### Data Migration Patterns
- **Incremental Sync**: Continuous synchronization during transition period
- **Validation**: Data quality checks and consistency verification
- **Transformation**: Convert legacy data formats to modern schemas
- **Audit Trail**: Complete history of all migration activities

### Decommissioning Strategy
- **Sunset Timeline**: Planned retirement of legacy integration services
- **Documentation**: Comprehensive documentation of integration patterns
- **Knowledge Transfer**: Ensure operational knowledge is preserved
- **Final Validation**: Complete verification before legacy system shutdown

## Detailed Microservice Implementation Specifications

### BEAA - Backend Automation Adapter (Detailed Implementation)

Based on the solution specification documentation:

#### System Use Cases
**Primary Functions:**
- **NUM BEA Access**: Enables NUM Backend Automation access to hub external systems via API (like CRM-T)
- **Response Forwarding**: Contains no business logic, forwards complete response of hub external systems to consumer
- **View-Only Operations**: Intention is to enable data views, Write and Update functions not enabled for consumers

#### Technical Architecture
**Request Logic Pattern:**
```
Consumer Request: <Tardis-Url>/<Tardis-Path-Bea-Adapter>/<Target-System-Name>/<Path>
Forward to: <Tardis-Url>/<Tardis-Path-Target-System>/<Path>
```

#### Security Implementation
**Authentication Flow:**
- **M2M Authentication**: Standard Tardis M2M Authentication Flow using Iris and Stargate
- **Bidirectional Security**: Authentication required for both consumer and target system directions
- **Token Management**: JWT-based authentication for secure API access

#### Implementation Details
**Technology Stack:**
- **Spring Cloud Gateway**: Same technology as VNRM Portal Backend for Frontend (B4F)
- **Configuration-Driven**: New target systems can be added via configuration changes
- **No Business Logic**: Pure proxy pattern with no data transformation

#### Service Level Agreements
**Operational Requirements:**
- **Monitoring**: All inbound and outbound requests monitored
- **Availability**: Service available during office hours
- **Support**: Office time support model

#### Currently Implemented Endpoints
**ProductInventoryManagement:**
- `GET Products (/beaa/crm-t/productInventory/products?phoneNumber=[phonenumber])`

**OrderInformation:**
- `GET ProductOrders (/beaa/crm-t/orderInformation/productOrders?phoneNumber=[phonenumber])`
- `GET ProductOrder by ID (/beaa/crm-t/orderInformation/productOrder/[productID])`

**Provider Change:**
- `GET ProviderChange Data By VAO ID (/beaa/crm-t/providerChange/vaoid/[vaoID])`

**Agreement Management:**
- `GET Agreements (/beaa/ws/agreementData/agreement)`
- `GET Agreement By ID (/beaa/ws/agreementData/agreement/[agreementID])`

### COMS - Communication Server (Detailed Implementation)

#### File System Architecture
**Structured File Management:**
- **Dedicated Folders**: Each user type gets dedicated folder with specific rights
- **Archive Integration**: Links to archive folders for historical data
- **Security Model**: Role-based access control for file operations

#### User Role Management
**Permission Matrix:**

| Role | Read Files | Update Files | New Files | Delete Files | Full Rights |
|------|------------|--------------|-----------|--------------|-------------|
| ComServ admin | ✓ | ✓ | ✓ | ✓ | ✓ (includes scripts, CRUD) |
| Technical Int. SST | ✓ | - | ✓ | - | - |
| Consumer API (TARDIS) | ✓ | - | ✓ | - | - |
| Technical VNRM System | ✓ | ✓ | ✓ | ✓ | - |
| Technical Ext. SST | ✓ | - | ✓ | ✓ | - |

#### Communication Flow Architecture
**Network Integration:**
- **Internet Connectivity**: External partner integration
- **Hitnet Connectivity**: Internal Telekom network access
- **VNRM Internal**: Internal microservice communication
- **SFTP Support**: Secure file transfer protocols

#### Service Level Agreements
**Operational Requirements:**
- **Monitoring**: 24/7 availability monitoring
- **User Management**: Technical user for every microservice in working area
- **Backup**: Daily backup of filesystem
- **Network**: Connection to internet, hitnet, and VNRM internal

#### File System Structure
**Organized Directory Layout:**
- **User-Specific Folders**: Dedicated directories per user type
- **Archive Folders**: Long-term storage with proper linking
- **Working Directories**: Active file processing areas
- **Log Directories**: System and access logging

## Advanced Integration Patterns

### Legacy System Bridge Architecture
**RNVS Integration Strategy:**
- **Database Bridge**: Direct database access and synchronization
- **File-Based Exchange**: Structured file formats for data transfer
- **API Translation**: Convert between legacy and modern API formats
- **State Management**: Maintain consistency across system boundaries

### External System Integration
**CRM-T Integration:**
- **Product Inventory**: Real-time product information retrieval
- **Order Management**: Order status and tracking information
- **Provider Change**: VAO-based provider change processing
- **Agreement Data**: Customer agreement and contract information

### Automation Workflow Patterns
**Backend Automation:**
- **NUM Integration**: Automated number management operations
- **CRM-T Connectivity**: Customer system data retrieval
- **File Processing**: Automated file handling and distribution
- **Error Management**: Integration with COR for error handling

## Technology Implementation Details

### Infrastructure Architecture
**Spring Cloud Gateway:**
- **Routing Rules**: Dynamic routing based on configuration
- **Load Balancing**: Distribution across multiple target systems
- **Circuit Breaker**: Resilience patterns for external system failures
- **Rate Limiting**: Traffic control and throttling

### Security Implementation
**Tardis Integration:**
- **Iris Authentication**: Identity management integration
- **Stargate Authorization**: Role-based access control
- **Token Validation**: JWT token verification and validation
- **Audit Logging**: Complete security audit trail

### Monitoring and Operations
**24/7 Monitoring:**
- **Health Checks**: Continuous service health monitoring
- **Performance Metrics**: Response time and throughput tracking
- **Error Tracking**: Real-time error detection and alerting
- **Capacity Monitoring**: Resource utilization tracking

Use this expertise to design effective legacy system integration strategies, manage the RNVS-to-VNRM migration process, ensure seamless communication between legacy and modern telecommunications systems, and implement robust automation and communication server capabilities while maintaining business continuity and regulatory compliance.
