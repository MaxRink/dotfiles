# RNVS Code Patterns

## Search Patterns by Language

- **TCL**: `proc procedure_name`, `SqlStoPro package.procedure`, `source file.tcl`
- **PL/SQL**: `PROCEDURE procedure_name`, `FUNCTION function_name`, `package.procedure(`
- **C++**: `class ClassName`, `#include "filename.hpp"`, `ClassName::method`
- **Java**: `class ClassName`, `import package.ClassName`
- **Shell**: `source script.sh`, `./script.tcl`, `sqlplus @script.sql`

---

## Dependency Patterns by Language

**TCL**:
```tcl
source ../lib/common_utils.tcl         # File dependency
SqlStoPro p_rnb.validate_assignment    # PL/SQL package dependency
```

**PL/SQL**:
```sql
p_tnb.get_operator(v_tnb_id);          # Package dependency
@rnb_validation.sql;                   # Script dependency
```

**C++**:
```cpp
#include "RnvsTnbManager.hpp"          # Header dependency
#include "common/BaseManager.hpp"      # Path-relative dependency
```

---

## RNVS-Specific Conventions

**Package naming**: `p_rnb`, `p_tnb`, `p_pda` → maps to `pack_body_rnb.sql`, etc.

**External systems** (mark as external, don't search):
- BNetzA Gateway
- CRM-T
- Number Block Registry
