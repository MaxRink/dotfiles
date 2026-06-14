---
name: ai4developers-legacy-code-migration-rnvs-marketplace-rnvs-plugin-vnrm-expert-vnrm-cor-architecture
description: VNRM COR (Correction/Business Error Management) submodule architecture reference covering business error tracking, resolution workflows, and error catalog integration. This skill should be used when designing or implementing COR services in phases 6-12 of the RNVS→VNRM migration workflow.
allowed-tools: Read
user-invocable: false
---

<!-- Imported from ai4developers/legacy-code-migration/rnvs-marketplace/rnvs-plugin/vnrm-expert/skills/vnrm-cor-architecture by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# VNRM COR Architecture Expert Skill

## Purpose

Provides comprehensive architecture knowledge for the **VNRM COR (CORRECTION)** submodule, which handles business error management including error tracking, resolution workflows, and integration with the COM error catalog for standardized error handling across all VNRM services.


## COR Submodule Overview

The COR (CORRECTION) submodule provides business error management capabilities through a minimal set of deployed microservices:

### Business Error Management
- **cor-bem-business-error-management-api** - Business error management API (OT level service)
- Handles error tracking and resolution for business logic issues
- Currently deployed to production but not yet released for business use
- Office time support (3-day response, business hours only)

## Service Architecture from Confluence Data

### Current Deployment Status
Based on VNRM SLA documentation:
- **Service Level**: Office Time (OT) - business hours support only
- **Production Status**: Deployed but not business-released
- **Support Model**: 3-day response time, no on-call duty required
- **Current State**: "Technisch in Prod, aber fachlich noch nicht freigegeben"

### Functional Scope
The COR submodule focuses on business error management rather than comprehensive correction capabilities:
- Business logic error tracking
- Error resolution workflows
- Integration with other VNRM services for error reporting
- Support for troubleshooting platform-internal and business defects

## Integration Dependencies

### Internal VNRM Integration
- **COM**: Uses error catalog services (com-ecc-errorcode-catalog-api) for standardized error codes
- **NUM**: Receives error reports from number management services
- **PRT**: Handles porting-related business errors
- **SPE**: Integrates with legacy system error handling

### Platform Dependencies
- Configuration server for service settings
- Reference data management for error categorization
- Centralized logging for error tracking and analysis

## Detailed Microservice Implementation Specifications

### BEM - Business Error Management (Detailed Implementation)

Based on the solution specification documentation:

#### GUI Navigation Architecture
**Navigation Structure:**
- **Order View**: Primary interface for viewing business error orders
- **Single Order Analysis**: Detailed view for individual error investigation
- **Navigation Map**: Structured navigation between different error management views

#### Error Management Workflow
**Order-Based Error Tracking:**
1. **Error Detection**: System identification of business logic errors
2. **Order Creation**: Generation of error management orders for tracking
3. **Analysis Interface**: Detailed view for error investigation and root cause analysis
4. **Resolution Tracking**: Monitoring of error correction progress
5. **Completion Verification**: Validation of successful error resolution

#### User Interface Components
**Order View Features:**
- **Error List Display**: Comprehensive listing of all business errors
- **Filter Capabilities**: Search and filter errors by various criteria
- **Status Tracking**: Real-time status of error resolution progress
- **Priority Management**: Prioritization of critical business errors

**Single Order Analysis:**
- **Detailed Error Information**: Complete error context and technical details
- **Root Cause Analysis**: Tools for investigating error origins
- **Resolution Actions**: Available correction actions and workflows
- **History Tracking**: Complete audit trail of error handling activities

#### Integration with VNRM Ecosystem
**Cross-Service Error Management:**
- **NUM Integration**: Business error handling for number management operations
- **PRT Integration**: Error management for porting workflow failures
- **COM Integration**: Integration with error catalog for standardized error codes
- **SPE Integration**: Error handling for legacy system integration issues

#### Error Classification System
**Business Error Categories:**
- **Data Validation Errors**: Business rule validation failures
- **Process Workflow Errors**: Business process execution failures
- **Integration Errors**: Cross-service communication failures
- **Regulatory Compliance Errors**: Violations of telecommunications regulations

#### Technical Architecture
**Service Design Patterns:**
- **RESTful API**: Standard REST API for error management operations
- **Database Integration**: Persistent storage for error tracking and history
- **Event-Driven**: Integration with VNRM message bus for error notifications
- **Monitoring Integration**: Connection to platform monitoring and alerting systems

#### Current Limitations and Future Development
**Development Status:**
- **Technical Deployment**: Service is technically deployed and operational
- **Business Release Pending**: Not yet released for full business use
- **Limited Scope**: Currently focuses on essential business error management
- **Evolution Path**: Planned expansion based on operational experience

Use this expertise to understand the business error management capabilities within VNRM, design error management solutions, implement business error tracking and resolution workflows, and integrate with other VNRM services while understanding the current limited scope and production readiness of the COR submodule.
