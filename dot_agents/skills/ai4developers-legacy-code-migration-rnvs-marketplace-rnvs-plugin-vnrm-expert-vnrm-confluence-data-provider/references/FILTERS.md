# Search Filters Reference

## Components & Scope
- **SPE**: Legacy RNVS integration, communication server, backend automation
- **PRT**: Number portability operations, carrier integration
- **COM**: Portal management, platform services, reference data management
- **COR**: Business error management, resolution workflows
- **NUM**: Call number resource management, inventory
- **PORT**: Porting processes and workflows

## Architecture Categories
- **APIs**: Interface specifications and contracts
- **BOM**: Data structures and entity relationships
- **Inventory**: Resource interconnections and dependencies
- **Order Management**: Order lifecycle and processing flows
- **Cross-cutting Concepts**: System-wide patterns and principles
- **Runtime View**: Operational behavior and execution flows
- **Requirements**: Core system requirements and constraints

## Search Patterns

**Components**: `space=DHVOICE AND (componentName AND (solution OR specification OR architecture))`
**Architecture**: `space=DHVOICE AND (conceptName AND VNRM AND architecture)`
**Business Objects**: `space=DHVOICE AND (BOM OR "Business Object" AND specificEntity)`

## Component-Specific Filters

**Components**:
- NUM: `space=DHVOICE AND (NUM OR "Number Management" OR "Call number")`
- PRT: `space=DHVOICE AND (PRT OR "Porting Management" OR portability)`
- SPE: `space=DHVOICE AND (SPE OR "Special Functions" OR legacy)`
- COM: `space=DHVOICE AND (COM OR "Common" OR portal OR platform)`
- COR: `space=DHVOICE AND (COR OR "Correction" OR error)`
- PORT: `space=DHVOICE AND (PORT OR porting OR migration)`

**Architecture**:
- APIs: `space=DHVOICE AND (API OR interface OR contract)`
- BOM: `space=DHVOICE AND (BOM OR "Business Object" OR model)`
- Inventory: `space=DHVOICE AND (inventory OR relationship OR resource)`
- Order: `space=DHVOICE AND (order OR lifecycle OR management)`
- Runtime: `space=DHVOICE AND (runtime OR execution OR operational)`
- Requirements: `space=DHVOICE AND (requirement OR fundamental OR core)`

## Search Tips

1. **Start broad, then narrow**: Begin with general terms like "VNRM architecture"
2. **Use component abbreviations**: NUM, PRT, COM, etc. are well-indexed
3. **Include German terms**: Many documents contain German terminology
4. **Combine concepts**: "NUM inventory management" for specific areas
