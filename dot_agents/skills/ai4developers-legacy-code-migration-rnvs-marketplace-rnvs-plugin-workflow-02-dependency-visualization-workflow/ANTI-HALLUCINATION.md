# Anti-Hallucination Checklist

Before finalizing PlantUML diagrams:

- Every component in diagrams exists in file-inventory.json
- Every dependency arrow exists in dependency-graph.json edges[]
- Every external system exists in dependency-graph.json external_dependencies[]
- Module groupings derived from file paths or module references (not invented)
- Color coding matches relevance_score from file-inventory.json
- Syntax validated (PlantUML hook passed)

**Red Flags** (DO NOT DO):
- Adding components "because they logically should exist"
- Adding dependencies "because module A probably calls module B"
- Creating diagrams without reading Phase 1 results first
- Ignoring validation errors from PostToolUse hook
- Inventing modules based on naming assumptions
