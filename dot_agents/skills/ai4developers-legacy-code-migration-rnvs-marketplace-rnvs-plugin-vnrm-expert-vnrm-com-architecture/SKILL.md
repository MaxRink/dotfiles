---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-vnrm-expert-vnrm-com-architecture
description: VNRM COM (Common) submodule architecture reference covering portal management, platform services, reference data management (RDM), and error management. This skill should be used when designing or implementing COM microservices in phases 6-12 of the RNVS→VNRM migration workflow.
allowed-tools: Read
user-invocable: false
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/vnrm-expert/skills/vnrm-com-architecture by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# VNRM COM Architecture Expert Skill

This skill should be used when designing or implementing COM microservices in phases 6-12 of the RNVS→VNRM migration workflow.

You are a specialized expert in the **VNRM COM (COMMON)** submodule within the Voice Number & Routing Management system. This skill provides comprehensive knowledge about the common services and platform management components based on actual VNRM Confluence documentation and deployed microservices.

## COM Submodule Overview

The COM (COMMON) submodule serves as the foundation of VNRM, providing shared services organized into four core functional areas based on the architecture documentation:

### Portal Management
Central access point for all VNRM functionality with the following features:
- Display and create individual reports with data analysis capabilities
- User concept and access management
- Reference data maintenance
- System and control parameter configuration
- File download and upload capabilities
- Integration with trouble ticket management
- Links to business applications (credential transfer support)
- Access to VNRM system documentation, interface documentation, and user guide

**Deployed Services:**
- **vnrm-container** (v2.4.0) - Main portal container at `vnrm.telekom.de` (HA level)
- **com-port-support-page** (v1.5.0) - Support page for user assistance (OT level)
- **com-port-backend-for-frontend** - Backend for frontend pattern implementation
- **com-port-ra-root-application** - Root application (deprecated, being removed from MTR)
- **com-port-helper-ui** - Helper UI component (deprecated, being removed from MTR)

### Platform Management
Management of distribution of resource ownership across microservices:
- All functionalities used by multiple microservices
- Statistics and analytics with direct triggering of functions
- TMF639 facade implementation for Resource Inventory Management standard

**Deployed Services:**
- **configserver** (v1.8.0) - Central configuration management server
- **com-cs-config-server-api** - Configuration server API (HA level - critical for NBIM dependency)
- **pfm-service** - Platform management service for resource coordination

### Reference Data Management (RDM)
Create, update, and delete business reference data:
- Frontend as micro UI calling from portal
- Update code reference setpoints and maintain master data
- ONKZ (area code) reference data management
- Telephony service provider information

**Deployed Services:**
- **com-rdm-reference-data-management-gui** - RDM GUI component
- **com-rdm-reference-data-management-api** - RDM API interface (OT level - will be re-evaluated when porting goes live)
- **tsp-gui** (v1.9.0) - Telephony service provider GUI
- **com-tsp-telephony-service-provider-api** - TSP API (HA level due to FCM integration)

### Error Management
Centralized error handling and service callnumber porting exchange:
- Standardized error codes across all VNRM services
- Error code catalog maintenance and versioning
- Integration with correction services

**Deployed Services:**
- **com-ecc-errorcode-catalog-api** - Error code catalog API (OT level)
- **com-ecc-errorcode-catalog-gui** - Error code catalog GUI

## Service Level Architecture & Critical Dependencies

### High Availability (HA) Services - 24/7 Support Required
**VNRM Portal (`vnrm.telekom.de`):**
- Critical user interface serving all VNRM users
- Central authentication and authorization point
- 3-hour response time, on-call duty required

**Configuration Server API (`com-cs-config-server-api`):**
- Essential dependency for all VNRM microservices
- Critical for NBIM (Number Block Inventory Management) operations
- Single point of failure for platform configuration

**Telephony Service Provider API (`com-tsp-telephony-service-provider-api`):**
- Required for FCM (Fixed Callnumber Management) integration
- Critical for porting workflows and carrier operations

### Office Time (OT) Services - Business Hours Support
**Reference Data Management API:**
- Currently OT level, planned for HA re-evaluation when porting process goes live
- Foundation for business logic validation across NUM and PRT services

**Error Code Catalog API:**
- Standard error management operations
- Integration point for COR business error management

### Deployment Evolution & Technical Debt
**Legacy Component Deprecation:**
- `com-port-ra-root-application` and `com-port-helper-ui` being removed from MTR repository
- Configuration server consolidation from legacy to new configserver (v1.8.0)
- Version alignment across RDM GUI and backend services

## Architecture Building Blocks Integration

### Platform Management Cluster
Based on the architecture documentation, COM provides:
- **Resource Ownership Distribution**: Management across all VNRM microservices
- **Shared Functionalities**: Used by multiple microservices
- **TMF639 Facade**: Standard telecommunications API compliance
- **Statistics & Analytics**: Direct function triggering and working results

### Reference Data Management Cluster
- **Frontend as Micro UI**: Called from portal for seamless user experience
- **Business Reference Data**: CRUD operations for master data
- **Code Reference Setpoints**: Update and maintenance of system parameters
- **ONKZ Management**: German area code (Ortsnetzkennzahl) administration

### Portal Cluster
Functions documented in architecture:
- **Monitoring Integration**: Tool view, links, or frontend embedding
- **Report Generation**: Display and create individual reports with data analysis
- **User Management**: User concept and access control
- **File Operations**: Download and upload capabilities
- **External Integration**: Links to business applications with credential transfer

## Critical Dependencies & Integration Patterns

### Internal VNRM Service Dependencies
**NUM Integration:**
- RDM provides ONKZ and carrier reference data for number validation
- TSP services support number management operations
- Configuration server provides NUM service settings

**PRT Integration:**
- TSP API supports porting workflows between carriers
- Error catalog provides standardized porting error codes
- Configuration management for porting process parameters

**COR Integration:**
- Error catalog (`com-ecc-errorcode-catalog-api`) integrates with business error management
- Centralized error code definitions and resolution procedures

**SPE Integration:**
- Configuration and platform services support legacy RNVS system integration
- Portal provides access to special function modules

### External System Critical Integrations
**FCM (Fixed Callnumber Management):**
- TSP API serves as critical interface for carrier operations
- HA level service due to real-time carrier integration requirements

**NBIM (Number Block Inventory Management):**
- Configuration server API essential for inventory operations
- HA level requirement due to operational criticality

## Detailed Microservice Implementation Specifications

### Reference Data Management (RDMA) - Technical Implementation

Based on the solution specification documentation:

#### Service Functionality
- **Configuration Management**: All details for configuring business needs of VNRM platform
- **Configuration Distribution**: Sends configuration files via API to different MSA inside VNRM
- **Centralized Control**: Best practice includes all configuration in one MicroserviceApplication (MSA)

#### Interface Architecture
**Communication Patterns:**
- **PDA Distributor → RDM**: TNB file exchange (TNB sends via PDA-Server files with TNB information)
- **RDM → RNVS**: Update RNVS reference data (System RNVS needs reference data until retirement)
- **KLS → RDM**: Local area reference from KLS (API for getting local area reference data from DTAG fixed line network)
- **Resource Allocator ↔ RDM**: CONF_REF (Functions in VNRM need partition rules, setpoints, and reference data)
- **RDM ↔ C@T**: TNB/RNB external reference wholesale
- **RDM → RNVS**: Data synchronization to legacy RNVS (ONKZ, RNB, and TSP reference data updates)
- **Callnumber Management ↔ RDM**: ONKZ and MVST reference data exchange
- **FNA (BNETZA) → RDM.GUI**: Upload of porting IDs manually via GUI
- **NUM → RDM.GUI**: Manual changes of reference data

#### Key Abbreviations and Systems
- **KLS**: Interface partner for terrestrial information of DTAG fixed line network
- **RNB**: Phone number range (Rufnummernblock)
- **TNB**: FNO = Fixed line network operator (Teilnehmernetzbetreiber)
- **TSP**: Telephony service provider
- **ONKZ**: Area code identifying geographic region for phone numbers (Ortsnetzkennzahl)
- **RNVS**: Legacy call number management system to be retired
- **PDA**: Porting data exchange distributor for FNO data file exchange
- **FNA (BNETZA)**: Federal network agency controlling fixed line networks

#### Micro User Interface (MUI) Functions
- **CRUD Operations**: Read, update, delete for every reference data set
- **Bulk Operations**: Single update and bulk operation capabilities
- **Data Export**: Download as XML or CSV formats
- **Data Analysis**: TSP and RNB functions include data analysis between different sources

### Configuration Server (CONFS) - Technical Implementation

#### User Interface Workflow
**Portal Integration:**
- **Role-Based Access**: Users need specific roles (VNRM_SYSA, VNRM_NUM_E, VNRM_SYSA_NON_PROD, LOCAL_ADMIN)
- **Page Access Control**: Page blocked for unauthorized users
- **Initialization Process**: Backend call to get available application, profile, label combinations

#### Configuration Management Process
**Parameter Selection Workflow:**
1. **Application Dropdown**: Choose application name of interest
2. **Profile Dropdown**: Choose profile for selected application (dependent on application selection)
3. **Label Dropdown**: Choose label for application/profile combination
4. **Extended Parameters**: Get full data for chosen service via "Get extended parameters" button

#### Data Editing Capabilities
**Edit Mode Operations:**
- **Table Editing**: Double-click table cells to start editing
- **Change Application**: Apply changes with Enter key
- **Save/Cancel**: Save applied changes or cancel to discard
- **Refresh**: Table refresh functionality
- **Browser Refresh**: Returns to initialization step

#### Error Handling
**Error Management:**
- **Pre-Save Errors**: No changes applied, refresh returns initial data
- **Post-Save Errors**: Changes applied for successful fields, failed fields unchanged
- **Backend Errors**: No changes applied on save failure
- **Invalid Role**: Config service completely blocked

## Advanced Integration Patterns

### TMF639 Resource Inventory Management Compliance
COM provides TMF639 facade implementation ensuring:
- **Standard API Compliance**: Telecommunications Management Forum standard adherence
- **Resource Inventory**: Standardized resource management across VNRM ecosystem
- **Interoperability**: Industry-standard integration patterns for external systems

### Cross-Domain Service Orchestration
**Configuration Distribution Architecture:**
- **Centralized Configuration**: Single source of truth for all VNRM microservice settings
- **Dynamic Configuration**: Runtime configuration updates without service restart
- **Environment Management**: Different configuration sets for DEV, TEST, PROD environments
- **Validation**: Configuration validation before distribution to prevent service failures

### Legacy System Integration Bridge
**RNVS Synchronization:**
- **Bidirectional Sync**: Keep legacy RNVS updated with VNRM reference data changes
- **Migration Support**: Gradual migration support with data consistency validation
- **Fallback Strategy**: Ensure RNVS can operate independently during VNRM maintenance
- **Data Format Translation**: Convert between VNRM modern data formats and RNVS legacy formats

## Technology Stack & Implementation Details

### Backend Architecture
- **Spring Boot Framework**: Microservice implementation
- **Configuration Server**: Spring Cloud Config or similar for centralized configuration
- **Database Integration**: PostgreSQL for reference data storage
- **API Gateway**: Routing and security for microservice communications
- **Message Bus**: Event-driven architecture for cross-service communication

### Frontend Architecture
- **Micro Frontend Pattern**: Each COM function as independent micro UI
- **Portal Integration**: Seamless integration within VNRM portal framework
- **Single Page Application**: Modern web application architecture
- **Role-Based UI**: Dynamic UI based on user permissions and roles

### Security Implementation
- **CIAM Integration**: Centralized identity and access management
- **JWT Tokens**: Secure API authentication
- **Role-Based Access Control**: Granular permissions for different user types
- **API Security**: OAuth2 and OpenID Connect for secure API access

Use this expertise to guide COM microservice architecture decisions, ensuring proper service level classification, understanding critical dependencies, maintaining the foundational role COM plays in the entire VNRM ecosystem, and implementing industry-standard telecommunications management patterns.
