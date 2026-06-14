# Kanban Boards

For task workflow visualization.

## Syntax

```mermaid
kanban
  todo[Todo]
    task1[Design API schema]@{priority: "High"}
    task2[Write tests]
  inProgress[In Progress]
    task3[Implement auth]@{assigned: "Alice", ticket: "AUTH-42", priority: "Very High"}
  done[Done]
    task4[Deploy staging]@{ticket: "DEP-10"}
```

**Metadata:** `@{assigned: "name", ticket: "ID", priority: "High"}`
**Priority values:** `Very High`, `High`, `Low`, `Very Low`
**Config:** `ticketBaseUrl: 'https://jira.example.com/browse/#TICKET#'` makes tickets clickable.
