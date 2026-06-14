# Batch Processing Topology

## Schedule Overview

| Window   | Start     | End       | Job Count | Critical?  |
| -------- | --------- | --------- | --------- | ---------- |
| {{name}} | {{HH:MM}} | {{HH:MM}} | {{count}} | {{yes/no}} |

## Critical Path Chains

### Chain: {{CHAIN_NAME}}

**Total Steps**: {{count}}
**Estimated Duration**: {{time}}
**Parallelization Opportunity**: {{yes/no — why}}

```
{{JOB1}} → {{JOB2}} → {{JOB3}} → ...
  └── PGM: {{program}}    └── PGM: {{program}}
  └── DSN: {{dataset}}    └── DSN: {{dataset}}
```

## Job Inventory

| Job Name | Schedule         | Steps | Programs | Datasets | Predecessor | Successor |
| -------- | ---------------- | ----- | -------- | -------- | ----------- | --------- |
| {{name}} | {{daily/weekly}} | {{n}} | {{list}} | {{list}} | {{job}}     | {{job}}   |

## Program Inventory (Batch)

| Program  | Called From (Jobs) | Language | Inputs       | Outputs      | Tables Accessed |
| -------- | ------------------ | -------- | ------------ | ------------ | --------------- |
| {{name}} | {{job.step}}       | {{lang}} | {{datasets}} | {{datasets}} | {{tables}}      |

## Dataset Flow

### Input Datasets

| Dataset (DSN) | Produced By | Consumed By | Format       | Retention |
| ------------- | ----------- | ----------- | ------------ | --------- |
| {{dsn}}       | {{job/ext}} | {{job}}     | {{FB/VB/PS}} | {{days}}  |

### Output Datasets

| Dataset (DSN) | Produced By | Consumed By      | Format       | GDG?       |
| ------------- | ----------- | ---------------- | ------------ | ---------- |
| {{dsn}}       | {{job}}     | {{job/external}} | {{FB/VB/PS}} | {{yes/no}} |

## Conditional Logic & Recovery

| Job      | Condition             | Action on Failure | Restart Point |
| -------- | --------------------- | ----------------- | ------------- |
| {{name}} | {{COND=(0,NE,STEP1)}} | {{ABEND/SKIP}}    | {{step name}} |

## Resource Dependencies

| Resource | Type             | Jobs Competing | Contention Risk  |
| -------- | ---------------- | -------------- | ---------------- |
| {{name}} | {{tape/DASD/DB}} | {{list}}       | {{high/med/low}} |

## Unknowns

- {{Any undocumented job dependencies, missing JCL, unclear scheduling}}
