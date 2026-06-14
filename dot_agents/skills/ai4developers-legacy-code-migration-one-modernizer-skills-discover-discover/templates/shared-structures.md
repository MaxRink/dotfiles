# Shared Data Structures

## Copybook/Header Resolution Summary

| Copybook/Header | Source Path | Used By (Programs) | Field Count | Change Impact    |
| --------------- | ----------- | ------------------ | ----------- | ---------------- |
| {{name}}        | {{path}}    | {{count programs}} | {{count}}   | {{high/med/low}} |

## Structure Details

### {{STRUCTURE_NAME}}

**Source**: `{{file:path}}`
**Type**: {{copybook/header/common-block}}
**Used by**: {{list of programs referencing this structure}}

#### Field Layout

| Level  | Name     | Type/PIC      | Size      | Description |
| ------ | -------- | ------------- | --------- | ----------- |
| {{01}} | {{name}} | {{PIC X(10)}} | {{bytes}} | {{purpose}} |

#### Change Impact Analysis

- Programs affected: {{count}}
- Batch jobs affected: {{list}}
- Online transactions affected: {{list}}

## Inclusion Chains

### {{PROGRAM_NAME}}

```
{{program.cbl}}
  └── COPY {{copybook1}}
       └── COPY {{nested-copybook}} (if nested)
  └── COPY {{copybook2}}
```

## Shared Structure Clusters

{{Groups of copybooks/headers that are always used together}}

| Cluster | Members  | Programs Using All | Likely Domain |
| ------- | -------- | ------------------ | ------------- |
| {{id}}  | {{list}} | {{count}}          | {{domain}}    |
