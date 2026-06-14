# PlantUML Patterns for RNVS Dependency Diagrams

RNVS-specific PlantUML templates and styling patterns.

---

## Module Diagram Template (dependencies.puml)

```plantuml
@startuml dependencies
title ${FEATURE} - Module & Technology Dependencies

' Module groupings - derive from Phase 1 file paths
package "RNVS ${FEATURE} Modules" {
  [RNB Management Module] as RNB
  [TNB Operator Module] as TNB
  [Validation Module] as VAL
}

' Language layers - from Phase 1 files[].language
package "Programming Languages" {
  [PL/SQL Packages] as PLSQL
  [C++ Components] as CPP
  [TCL Scripts] as TCL
}

' External systems - from Phase 1 external_dependencies[]
cloud "External Systems" {
  [BNetzA Gateway] as BNETZ
  [CRM-T] as CRM
  database "Number Block Registry" as DB
}

' Dependencies - from Phase 1 edges[]
RNB --> TNB : validates operators
RNB --> BNETZ : KCODE messages
PLSQL --> DB : T_RNB tables

note right of RNB
  Core number block management
  KCODE: 20-26
end note

@enduml
```

---

## Detailed Diagram Template (dependencies_detailed.puml)

```plantuml
@startuml dependencies_detailed
title ${FEATURE} - Detailed Component Dependencies

' Group by language - PL/SQL first (core business logic)
package "PL/SQL Components" {
  [pack_body_rnb.sql] as RNB_BODY <<Package Body>> #LightGreen
  [p_rnb.pks] as RNB_SPEC <<Package Spec>> #LightGreen
  [pack_body_tnb.sql] as TNB_BODY <<Package Body>> #LightYellow
}

' C++ orchestration layer
package "C++ Components" {
  [RnvsRnbManager.cpp] as RNB_MGR <<Manager>> #LightGreen
  [RnvsTnbManager.hpp] as TNB_MGR <<Header>> #LightYellow
}

' TCL integration layer
package "TCL Scripts" {
  [kcode_processor.tcl] as KCODE_TCL <<Script>> #LightGreen
}

' External systems
cloud "External Systems" {
  database "Number Block Registry" as DB
  [BNetzA Gateway] as BNETZ
}

' Dependencies - from Phase 1 edges[]
RNB_BODY --> TNB_BODY : calls p_tnb procedures
RNB_MGR --> TNB_MGR : includes header
KCODE_TCL --> RNB_BODY : SqlStoPro p_rnb.*
RNB_BODY --> DB : INSERT/UPDATE T_RNB

legend right
  |= Color |= Relevance |
  | <#LightGreen> | High (>=70) |
  | <#LightYellow> | Medium (40-69) |
endlegend

@enduml
```

---

## Essential PlantUML Syntax

**Aliases** (for long file names):
```plantuml
[pack_body_rnb.sql] as RNB_BODY
```

**Stereotypes** (for component types):
```plantuml
[file.sql] <<Package Body>>
[file.cpp] <<Manager>>
[file.tcl] <<Script>>
```

**Color coding**:
```plantuml
RNB_BODY #LightGreen   ' High relevance
TNB_BODY #LightYellow  ' Medium relevance
```

**Layout hints** (for cleaner diagrams):
```plantuml
A -down-> B    ' Force downward
A -right-> B   ' Force rightward
```

**Notes** (for business context):
```plantuml
note right of RNB
  KCODE 20-26 processing
end note
```

---

## RNVS Naming Conventions

| File Pattern | Stereotype | Typical Relevance |
|--------------|------------|-------------------|
| `pack_body_*.sql` | <<Package Body>> | High (core logic) |
| `p_*.pks` | <<Package Spec>> | High |
| `*Manager.cpp` | <<Manager>> | High |
| `*.hpp` | <<Header>> | Medium |
| `*_processor.tcl` | <<Script>> | Medium-High |
| `*_utils.tcl` | <<Utility>> | Low-Medium |
