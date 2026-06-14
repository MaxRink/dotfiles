---
name: ai4dev-tmforum-plugin-etom-framework
description: TM Forum enhanced Telecom Operations Map (eTOM) business process framework. Use this skill when mapping business processes to eTOM hierarchy, aligning processes with TMF APIs, understanding telecommunications operations framework, or designing process-to-technology alignments.
---

<!-- Imported from ai4developers/claude-code/claude-code-plugins/tmforum-plugin/skills/etom-framework by codex-knowledge-curation/scripts/persist_project_skills.py. -->

# eTOM Framework

## Overview

This skill provides guidance on TM Forum eTOM (enhanced Telecom Operations Map) - a comprehensive business process
framework for telecommunications that maps business operations to technical implementations.

## When to Use This Skill

Use when mapping business processes to eTOM, aligning operations with TMF APIs, designing business architecture, or bridging business and technology views.

## eTOM Structure

### Level 1: Three Main Areas

**1. Strategy, Infrastructure & Product (SIP)**
Long-term planning, infrastructure development, product lifecycle

**2. Operations**
Core operational processes organized as FAB:

- **Fulfillment** (F): Order-to-activation
- **Assurance** (A): Service quality, problem resolution
- **Billing** (B): Usage-to-cash

**3. Enterprise Management**
Cross-functional enterprise processes (Finance, HR, Supply Chain)

## Operations Processes (FAB)

### Fulfillment

**Purpose**: Handle customer orders and requests

**Level 2 Processes**:

- CRM Support & Readiness
- Customer Interface Management
- Selling
- Order Handling
- Problem Handling (Fulfillment)
- Customer QoS/SLA Management

**Key TMF APIs**: TMF622 (Product Ordering), TMF641 (Service Ordering), TMF620 (Product Catalog)

### Assurance

**Purpose**: Maintain service quality and resolve problems

**Level 2 Processes**:

- Service Management & Operations
- Service Problem Management
- Resource Management & Operations
- Resource Problem Management

**Key TMF APIs**: TMF621 (Trouble Ticket), TMF656 (Alarm), TMF638 (Service Inventory), TMF639 (Resource Inventory)

### Billing

**Purpose**: Revenue capture and billing

**Level 2 Processes**:

- Billing & Collections Management
- Bill Inquiry Handling
- Payment Collection

**Key TMF APIs**: TMF678 (Customer Bill), TMF676 (Payment), TMF688 (Event), TMF635 (Usage)

## Process-to-API Mapping

| eTOM Process | TMF API | Operations |
|--------------|---------|------------|
| Order Handling | TMF622 | POST /productOrder, GET /productOrder/{id} |
| Selling | TMF620 | GET /productOffering |
| Service Provisioning | TMF641 | POST /serviceOrder |
| Problem Management | TMF621 | POST /troubleTicket, PATCH /troubleTicket/{id} |
| Billing Management | TMF678 | POST /customerBill, GET /customerBill |
| Payment Collection | TMF676 | POST /payment |

## Process Patterns

**Fulfillment Pattern**:
Request → Feasibility → Authorization → Configuration → Provisioning → Activation → Completion

**Assurance Pattern**:
Detection → Diagnosis → Resolution → Verification → Closure

**Billing Pattern**:
Usage Capture → Rating → Billing → Invoice Delivery → Payment Collection
