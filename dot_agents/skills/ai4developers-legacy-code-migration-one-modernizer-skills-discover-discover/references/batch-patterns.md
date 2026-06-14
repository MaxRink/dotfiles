# Batch/JCL Analysis Reference

## JCL Statement Types

| Statement               | Purpose           | What to Extract             |
| ----------------------- | ----------------- | --------------------------- |
| `//jobname JOB`         | Job definition    | Job name, class, accounting |
| `//stepname EXEC PGM=`  | Execute program   | Program name, PARM=         |
| `//stepname EXEC PROC=` | Execute procedure | Proc name, overrides        |
| `//ddname DD DSN=`      | Data definition   | Dataset name, DISP, DCB     |
| `// IF (cond) THEN`     | Conditional step  | Condition logic             |
| `// SET var=value`      | Variable          | Symbolic parameters         |
| `// INCLUDE MEMBER=`    | Include           | Proc library reference      |
| `// JCLLIB ORDER=`      | Proc search path  | Library concatenation       |

## DD Statement DISP Analysis

| DISP                 | Meaning                        | Data Flow Direction      |
| -------------------- | ------------------------------ | ------------------------ |
| `(NEW,CATLG,DELETE)` | Create new, catalog on success | OUTPUT (creates)         |
| `(NEW,PASS)`         | Create, pass to next step      | OUTPUT (temporary)       |
| `(OLD,DELETE)`       | Open exclusive, delete after   | INPUT (destructive read) |
| `(SHR,KEEP)`         | Shared read                    | INPUT                    |
| `(MOD,CATLG)`        | Append to existing             | OUTPUT (append)          |
| `DUMMY`              | Null file                      | Neither (suppressed)     |

## Common Utility Programs

| Program           | Purpose                   | Migration Equivalent    |
| ----------------- | ------------------------- | ----------------------- |
| IEBCOPY           | PDS copy/compress         | File copy               |
| IEBGENER          | Sequential copy           | `cp` / stream copy      |
| IEFBR14           | No-op (for DD allocation) | No equivalent needed    |
| IDCAMS            | VSAM utility              | Database DDL            |
| DFSORT / SYNCSORT | Sort/merge                | ORDER BY / sort utility |
| ICETOOL           | Multi-step sort/report    | ETL pipeline            |
| IKJEFT01          | TSO batch                 | Shell script            |
| IRXJCL            | REXX batch                | Script executor         |
| DFSRRC00          | IMS batch                 | App server call         |
| DFHCSDUP          | CICS table utility        | Config deployment       |

## Batch Architecture Patterns

### Sequential Chain

```
JOB1 (extract) → JOB2 (transform) → JOB3 (load)
  Each job reads the previous job's output dataset
```

### Conditional Execution

```
//STEP01 EXEC PGM=PROCESS
//STEP02 EXEC PGM=REPORT,COND=(0,NE,STEP01)
  STEP02 only runs if STEP01 RC=0
```

### GDG (Generation Data Group)

```
DSN=HLQ.DAILY.FILE(+1)    ← today's generation (output)
DSN=HLQ.DAILY.FILE(0)     ← yesterday's generation (input)
DSN=HLQ.DAILY.FILE(-1)    ← day before yesterday
```

### Restart/Recovery

```
//RESTART EXEC PGM=RESTART,PARM='STEP03'
  Restart from specific step after failure
```

## Control-M Patterns

| Element       | Purpose             | What to Capture        |
| ------------- | ------------------- | ---------------------- |
| SMART_FOLDER  | Job group           | Logical unit boundary  |
| IN-CONDITION  | Prerequisite        | Dependency chain       |
| OUT-CONDITION | Completion signal   | What depends on this   |
| QUANTITATIVE  | Resource limit      | Parallelism constraint |
| CALENDAR      | Schedule definition | Frequency, exclusions  |
| SHOUT         | Alert action        | Failure notification   |

## Autosys JIL Patterns

| Attribute            | Purpose            | Migration Use          |
| -------------------- | ------------------ | ---------------------- |
| `job_type: CMD`      | Command job        | Map to task/step       |
| `job_type: BOX`      | Container          | Map to workflow/DAG    |
| `condition: s(job1)` | Success dependency | DAG edge               |
| `condition: f(job1)` | Failure dependency | Error handling path    |
| `start_times`        | Scheduled start    | Cron/schedule config   |
| `term_run_time`      | Max runtime        | Timeout configuration  |
| `alarm_if_fail: 1`   | Alert on failure   | Monitoring integration |

## Complexity Indicators

| Signal                          | Meaning                                    |
| ------------------------------- | ------------------------------------------ |
| > 20 steps in one job           | Monolithic batch — candidate for splitting |
| GDG with deep generations       | Rolling history — retention policy needed  |
| COND= with complex RC logic     | Hard to trace execution path               |
| Multiple PROC overrides         | Customization of shared logic              |
| RESTART parameter in PARM       | Manual recovery procedures                 |
| VSAM REPRO/DEFINE               | Data store management embedded in batch    |
| Cross-job dataset dependencies  | Implicit coupling between jobs             |
| Time-based scheduling conflicts | Resource contention in batch window        |
