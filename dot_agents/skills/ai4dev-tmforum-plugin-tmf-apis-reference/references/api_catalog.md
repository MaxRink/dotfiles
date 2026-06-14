# TM Forum Open API Complete Catalog

This document provides a comprehensive catalog of all 93+ TM Forum Open APIs organized by family.

## Product Management APIs (TMF6XX)

### TMF620 - Product Catalog Management

**Version**: v5.0.0
**Purpose**: Manage product offerings, specifications, and catalogs
**Key Resources**:

- `productOffering`: Commercialized products available for sale
- `productSpecification`: Detailed product characteristics
- `category`: Product categorization and taxonomy
- `catalog`: Product catalogs grouping offerings

**Common Operations**:

- GET /productOffering - Browse catalog
- POST /productOffering - Create new offering (admin)
- PATCH /productOffering/{id} - Update offering
- GET /productSpecification - Retrieve specifications

**Use Cases**: E-commerce catalogs, subscription management, product portfolio management

### TMF622 - Product Ordering Management

**Version**: v5.0.0
**Purpose**: Submit, track, and manage product orders
**Key Resources**:

- `productOrder`: Customer orders for products
- `productOrderItem`: Individual items within an order
- `cancelProductOrder`: Order cancellation requests

**Common Operations**:

- POST /productOrder - Submit new order
- GET /productOrder/{id} - Track order status
- PATCH /productOrder/{id} - Update order
- POST /cancelProductOrder - Cancel order

**Order States**: acknowledged, inProgress, pending, held, assessingCancellation, pendingCancellation, cancelled, completed, failed, partial

**Use Cases**: E-commerce ordering, subscription sign-up, service changes

### TMF637 - Product Inventory Management

**Version**: v5.0.0
**Purpose**: Track and manage active product instances
**Key Resources**:

- `product`: Instantiated products owned by customers
- `productRelationship`: Relationships between products

**Common Operations**:

- GET /product - Query customer products
- POST /product - Create product instance (fulfillment)
- PATCH /product/{id} - Update product state
- DELETE /product/{id} - Terminate product

**Product States**: created, pendingActive, cancelled, active, pendingTerminate, terminated, suspended, aborted

**Use Cases**: Subscription tracking, customer product inventory, lifecycle management

### TMF679 - Product Qualification Management

**Version**: v5.0.0
**Purpose**: Check product availability and feasibility
**Key Resources**:

- `productQualification`: Qualification requests
- `productQualificationItem`: Items being qualified

**Common Operations**:

- POST /productQualification - Check product availability
- GET /productQualification/{id} - Get qualification result

**States**: acknowledged, inProgress, terminatedWithError, done

**Use Cases**: Address qualification, service availability checks, pre-order validation

### TMF760 - Product Configuration Management

**Version**: v4.0.0
**Purpose**: Configure complex product offerings
**Key Resources**:

- `productConfiguration`: Configuration specifications

**Use Cases**: Complex product configuration, CPQ (Configure-Price-Quote) systems

---

## Customer Management APIs (TMF6XX)

### TMF629 - Customer Management

**Version**: v5.0.0
**Purpose**: CRUD operations on customer entities
**Key Resources**:

- `customer`: Customer entity representing individuals or organizations

**Common Operations**:

- GET /customer - Query customers
- POST /customer - Create customer
- PATCH /customer/{id} - Update customer
- DELETE /customer/{id} - Remove customer

**Customer Statuses**: valued, active, inactive, prospect, terminated

**Use Cases**: Customer onboarding, CRM, customer 360 views

### TMF632 - Party Management

**Version**: v5.0.0
**Purpose**: Manage individuals and organizations
**Key Resources**:

- `individual`: Natural persons
- `organization`: Legal entities
- `partyRole`: Roles that parties play

**Common Operations**:

- GET /individual - Query individuals
- POST /individual - Create individual
- GET /organization - Query organizations
- POST /organization - Create organization

**Use Cases**: Party master data management, contact management, organizational hierarchies

### TMF666 - Account Management

**Version**: v5.0.0
**Purpose**: Customer accounts and balances
**Key Resources**:

- `billingAccount`: Billing accounts
- `settlementAccount`: Financial settlement accounts
- `financialAccount`: General financial accounts

**Common Operations**:

- GET /billingAccount - Query accounts
- POST /billingAccount - Create account
- GET /billingAccount/{id}/balance - Check balance

**Use Cases**: Account management, billing relationships, balance tracking

### TMF667 - Document Management

**Version**: v4.0.0
**Purpose**: Manage customer documents and attachments
**Key Resources**:

- `document`: Document metadata and content

**Use Cases**: Contract storage, ID verification documents, correspondence

### TMF668 - Contact Management

**Version**: v4.0.0
**Purpose**: Manage customer interactions and touchpoints
**Key Resources**:

- `contact`: Customer contact records

**Use Cases**: Interaction history, omnichannel contact management

---

## Service Management APIs (TMF6XX)

### TMF633 - Service Catalog Management

**Version**: v5.0.0
**Purpose**: Manage service offerings and specifications
**Key Resources**:

- `serviceCandidate`: Marketable services
- `serviceSpecification`: Service characteristics
- `serviceCatalog`: Service catalogs

**Use Cases**: Service catalog publishing, service specifications

### TMF638 - Service Inventory Management

**Version**: v5.0.0
**Purpose**: Track active service instances
**Key Resources**:

- `service`: Instantiated services (customer-facing and resource-facing)

**Common Operations**:

- GET /service - Query services
- POST /service - Create service instance
- PATCH /service/{id} - Update service
- DELETE /service/{id} - Terminate service

**Service States**: feasibilityChecked, designed, reserved, inactive, active, terminated

**Use Cases**: Service inventory, customer service tracking, network service management

### TMF640 - Service Activation and Configuration

**Version**: v5.0.0
**Purpose**: Activate and configure services
**Key Resources**:

- `service`: Service activation and configuration operations

**Use Cases**: Service turn-up, service configuration changes

### TMF641 - Service Ordering Management

**Version**: v5.0.0
**Purpose**: Service provisioning orders
**Key Resources**:

- `serviceOrder`: Orders for service provisioning
- `serviceOrderItem`: Service order line items

**Common Operations**:

- POST /serviceOrder - Submit provisioning order
- GET /serviceOrder/{id} - Track order
- PATCH /serviceOrder/{id} - Update order

**Order States**: acknowledged, inProgress, pending, held, assessingCancellation, pendingCancellation, cancelled, completed, failed, partial

**Use Cases**: Service provisioning, service changes, service disconnections

### TMF645 - Service Qualification Management

**Version**: v4.0.0
**Purpose**: Check service availability
**Key Resources**:

- `serviceQualification`: Service qualification requests

**Use Cases**: Service availability checks, technical feasibility

---

## Resource Management APIs (TMF6XX)

### TMF634 - Resource Catalog Management

**Version**: v5.0.0
**Purpose**: Resource specifications and catalogs
**Key Resources**:

- `resourceSpecification`: Resource characteristics
- `resourceCatalog`: Resource catalogs

**Use Cases**: Network resource specifications, IT resource catalogs

### TMF639 - Resource Inventory Management

**Version**: v5.0.0
**Purpose**: Track physical and logical resources
**Key Resources**:

- `resource`: Physical and logical resources (network elements, servers, software)

**Common Operations**:

- GET /resource - Query resources
- POST /resource - Add resource
- PATCH /resource/{id} - Update resource
- DELETE /resource/{id} - Remove resource

**Resource States**: planning, installing, active, standby, terminated, suspended

**Use Cases**: Network inventory, IT asset management, capacity planning

### TMF652 - Resource Function Activation Configuration

**Version**: v4.0.0
**Purpose**: Activate resource functions
**Key Resources**:

- `resourceFunctionActivationConfiguration`: Activation configurations

**Use Cases**: Network function activation, VNF lifecycle management

### TMF664 - Resource Order Management

**Version**: v4.0.0
**Purpose**: Resource provisioning orders
**Key Resources**:

- `resourceOrder`: Orders for resource provisioning

**Use Cases**: Resource provisioning workflows

### TMF685 - Resource Pool Management

**Version**: v4.0.0
**Purpose**: Manage resource pools and allocation
**Key Resources**:

- `resourcePool`: Pools of resources
- `reservation`: Resource reservations

**Use Cases**: Capacity management, resource allocation, reservation systems

---

## Operations & Trouble APIs (TMF6XX)

### TMF621 - Trouble Ticket Management

**Version**: v5.0.0
**Purpose**: Create and track trouble tickets
**Key Resources**:

- `troubleTicket`: Trouble tickets for problem tracking

**Common Operations**:

- POST /troubleTicket - Create ticket
- GET /troubleTicket/{id} - Retrieve ticket
- PATCH /troubleTicket/{id} - Update ticket

**Ticket States**: acknowledged, inProgress, pending, resolved, closed, cancelled

**Use Cases**: Customer issue tracking, network problem management, NOC operations

### TMF656 - Alarm Management

**Version**: v4.0.0
**Purpose**: Network alarms and events
**Key Resources**:

- `alarm`: Network alarms
- `alarmSpecification`: Alarm definitions

**Common Operations**:

- GET /alarm - Query alarms
- PATCH /alarm/{id} - Acknowledge/clear alarm

**Alarm Severities**: critical, major, minor, warning, indeterminate, cleared

**Use Cases**: Network monitoring, alarm correlation, fault management

### TMF724 - Incident Management

**Version**: v4.0.0
**Purpose**: Incident tracking and resolution
**Key Resources**:

- `incident`: Service/network incidents

**Use Cases**: Incident response, major outage management

### TMF623 - Service Level Agreement Management

**Version**: v4.0.0
**Purpose**: SLA definitions and monitoring
**Key Resources**:

- `serviceLevelAgreement`: SLA contracts

**Use Cases**: SLA management, service quality assurance

### TMF625 - Service Level Objective Management

**Version**: v4.0.0
**Purpose**: SLO tracking
**Key Resources**:

- `serviceLevelObjective`: SLO specifications

**Use Cases**: Performance monitoring, quality of service

---

## Finance & Revenue APIs (TMF6XX)

### TMF678 - Customer Bill Management

**Version**: v5.0.0
**Purpose**: Generate and deliver customer bills
**Key Resources**:

- `customerBill`: Customer bills/invoices
- `appliedCustomerBillingRate`: Applied billing rates

**Common Operations**:

- GET /customerBill - Query bills
- POST /customerBill - Generate bill
- GET /customerBill/{id} - Retrieve specific bill

**Bill States**: new, onCycle, offCycle, validated, sent, partiallyPaid, paid, settled

**Use Cases**: Billing, invoicing, bill presentment

### TMF676 - Payment Management

**Version**: v5.0.0
**Purpose**: Process payments and refunds
**Key Resources**:

- `payment`: Payment transactions
- `refund`: Refund transactions

**Common Operations**:

- POST /payment - Process payment
- GET /payment/{id} - Query payment status
- POST /refund - Issue refund

**Payment States**: open, pending, cancelled, completed, failed

**Use Cases**: Payment processing, refund management, payment reconciliation

### TMF688 - Event Management

**Version**: v4.0.0
**Purpose**: Usage events for billing
**Key Resources**:

- `event`: Usage events

**Use Cases**: Usage capture, event-based billing, rating

### TMF635 - Usage Management

**Version**: v4.0.0
**Purpose**: Usage data collection and rating
**Key Resources**:

- `usage`: Usage records
- `usageSpecification`: Usage specifications

**Use Cases**: Usage collection, rating, mediation

### TMF654 - Prepay Balance Management

**Version**: v4.0.0
**Purpose**: Prepaid account balances
**Key Resources**:

- `balanceActionRequest`: Balance operations (reserve, unreserve, deduct)

**Use Cases**: Prepaid services, balance management, real-time charging

---

## Advanced Capabilities APIs (TMF7XX, TMF9XX)

### TMF730 - Software and Compute Management

**Version**: v4.0.0
**Purpose**: Cloud resources and VNFs
**Key Resources**:

- `softwareInstance`: Software instances
- `computeInstance`: Compute resources

**Use Cases**: Cloud service management, VNF lifecycle management

### TMF663 - Shopping Cart Management

**Version**: v4.0.0
**Purpose**: Multi-item cart management
**Key Resources**:

- `shoppingCart`: Shopping carts

**Use Cases**: E-commerce, multi-product ordering

### TMF699 - Communication Management

**Version**: v4.0.0
**Purpose**: Notifications and messaging
**Key Resources**:

- `communication`: Communication records

**Use Cases**: Customer notifications, omnichannel messaging

### TMF669 - Party Role Management

**Version**: v4.0.0
**Purpose**: Party roles and relationships
**Key Resources**:

- `partyRole`: Roles (customer, supplier, partner, employee)

**Use Cases**: Role management, B2B relationships

### TMF931 - Open Gateway Onboarding

**Version**: v1.0.0
**Purpose**: Network-as-a-Service APIs
**Key Resources**:

- TBD (Emerging API)

**Use Cases**: Network API exposure, NEaaS platforms

---

## Additional Notable APIs

### TMF651 - Agreement Management

**Version**: v4.0.0
**Purpose**: Contracts and agreements

### TMF620 - Quote Management

**Version**: v4.0.0
**Purpose**: Price quotations

### TMF646 - Appointment Management

**Version**: v4.0.0
**Purpose**: Service appointments

### TMF648 - Quote Management

**Version**: v4.0.0
**Purpose**: Product and service quotes

### TMF666 - Payment Method Management

**Version**: v4.0.0
**Purpose**: Customer payment methods

### TMF674 - Geographic Address Management

**Version**: v4.0.0
**Purpose**: Address validation and management

### TMF673 - Geographic Site Management

**Version**: v4.0.0
**Purpose**: Geographic sites and locations

### TMF672 - User Roles and Permissions

**Version**: v4.0.0
**Purpose**: RBAC and user management

### TMF644 - Party Privacy Profile Management

**Version**: v4.0.0
**Purpose**: Privacy preferences and consent

---

## API Version Summary

**v5.0.0 (Latest)**:

- TMF620, TMF622, TMF629, TMF632, TMF633, TMF637, TMF638, TMF640, TMF641, TMF666, TMF678, TMF676

**v4.0.0 (Widely Adopted)**:

- Most other APIs (TMF621, TMF634, TMF639, TMF645, TMF652, TMF654, TMF656, TMF663, TMF664, TMF667, TMF668, TMF669, TMF673, TMF674, TMF679, TMF685, TMF688, TMF699, TMF724, TMF730, etc.)

**Recommendation**: Use v5.0.0 for new implementations where available. v4.0.0 remains widely supported and stable.

---

## Quick API Finder

**Need to...** → **Use API**:

- Browse products → TMF620
- Order products → TMF622
- Track customer products → TMF637
- Manage customers → TMF629
- Provision services → TMF641
- Track services → TMF638
- Report problems → TMF621
- Monitor alarms → TMF656
- Generate bills → TMF678
- Process payments → TMF676
- Manage resources → TMF639
- Check availability → TMF679, TMF645

---
