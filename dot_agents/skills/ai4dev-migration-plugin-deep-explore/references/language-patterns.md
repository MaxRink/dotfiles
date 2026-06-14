# Language-Specific Grep Patterns

> Use these patterns to build a file map before reading any source files.
> Adapt the patterns to the stack's dominant language. Run 3-5 targeted greps,
> then read only the files that appear in the results.

## Java / Kotlin / Scala

```text
Grep("class .* implements|class .* extends",      dir) → service/component classes
Grep("@Controller|@RestController|@Service",       dir) → Spring components
Grep("@Entity|@Table|@Document",                   dir) → data models
Grep("@RequestMapping|@GetMapping|@PostMapping",   dir) → API endpoints
Grep("@Scheduled|@EventListener|@KafkaListener",   dir) → async/event handlers
Grep("TODO|FIXME|HACK|XXX|NOSONAR",               dir) → technical debt
```

## Python

```text
Grep("class .*:|def .*:",                          dir) → classes and functions
Grep("@app\\.route|@router\\.|@api_view",          dir) → API endpoints (Flask/FastAPI/Django)
Grep("class .*Model|class .*Schema|Base\\)",       dir) → data models (SQLAlchemy/Pydantic/Django)
Grep("celery|@task|@shared_task",                  dir) → async tasks
Grep("import .*from|from .* import",               dir) → dependency mapping
Grep("TODO|FIXME|HACK|XXX|noqa",                  dir) → technical debt
```

## TypeScript / JavaScript

```text
Grep("export (class|function|const|interface)",    dir) → public API surface
Grep("@(Controller|Injectable|Module|Component)",  dir) → NestJS/Angular decorators
Grep("app\\.(get|post|put|delete|patch)\\(",       dir) → Express routes
Grep("(interface|type) .*\\{",                     dir) → type definitions
Grep("Schema\\(|model\\(|entity\\(",              dir) → data models (Mongoose/TypeORM/Prisma)
Grep("TODO|FIXME|HACK|XXX",                       dir) → technical debt
```

## Go

```text
Grep("func .*(.*) .*{|type .* struct",             dir) → functions and structs
Grep("func .*Handler|func .*Server|http\\.",       dir) → HTTP handlers
Grep("type .* interface",                          dir) → interface definitions
Grep("sql\\.|gorm\\.|ent\\.",                     dir) → database access
Grep("go func|chan |select \\{",                   dir) → concurrency patterns
Grep("TODO|FIXME|HACK|XXX",                       dir) → technical debt
```

## Rust

```text
Grep("pub (fn|struct|enum|trait|impl)",             dir) → public API surface
Grep("#\\[derive|#\\[.*route|#\\[.*handler",       dir) → derive macros and route handlers
Grep("impl .* for",                                dir) → trait implementations
Grep("async fn|tokio::|spawn",                     dir) → async patterns
Grep("TODO|FIXME|HACK|XXX|todo!|unimplemented!",  dir) → technical debt
```

## C / C++

```text
Grep("#include|namespace ",                        dir) → header dependencies
Grep("class .*:|struct .* \\{",                    dir) → class/struct definitions
Grep("virtual |override|= 0;",                    dir) → polymorphism
Grep("malloc|free|new |delete |shared_ptr",        dir) → memory management
Grep("pthread|mutex|std::thread|std::async",       dir) → concurrency
Grep("TODO|FIXME|HACK|XXX",                       dir) → technical debt
```

## C\#

```text
Grep("public class|public interface|public record", dir) → type definitions
Grep("\\[Http(Get|Post|Put|Delete)\\]|\\[Route",   dir) → API endpoints
Grep("\\[Table\\]|DbSet|DbContext",                dir) → Entity Framework models
Grep("async Task|await |CancellationToken",        dir) → async patterns
Grep("TODO|FIXME|HACK|XXX",                       dir) → technical debt
```

## SQL / PL/SQL

```text
Grep("CREATE TABLE|ALTER TABLE",                   dir) → schema definitions
Grep("CREATE.*PROCEDURE|CREATE.*FUNCTION",         dir) → stored procedures
Grep("CREATE.*TRIGGER|CREATE.*VIEW",               dir) → triggers and views
Grep("CREATE.*INDEX|CREATE.*SEQUENCE",             dir) → indexes and sequences
Grep("INSERT INTO|UPDATE |DELETE FROM",            dir) → DML patterns
```

## COBOL

```text
Grep("IDENTIFICATION DIVISION|PROGRAM-ID",        dir) → program entry points
Grep("DATA DIVISION|WORKING-STORAGE",             dir) → data definitions
Grep("PROCEDURE DIVISION",                        dir) → business logic entry
Grep("CALL |EXEC CICS|EXEC SQL",                  dir) → external calls
Grep("COPY |REPLACE ",                            dir) → copybook dependencies
```

## Ruby

```text
Grep("class .*<|module ",                          dir) → classes and modules
Grep("def (self\\.)?",                             dir) → method definitions
Grep("has_many|belongs_to|has_one",                dir) → ActiveRecord associations
Grep("get |post |put |delete |resources ",         dir) → routes
Grep("TODO|FIXME|HACK|XXX",                       dir) → technical debt
```

## PHP

```text
Grep("class .*(extends|implements)",               dir) → class hierarchy
Grep("function .*(Request|Response)",              dir) → controller methods
Grep("@ORM|@Entity|@Table|Schema::",              dir) → data models
Grep("Route::(get|post|put|delete)",              dir) → route definitions
Grep("TODO|FIXME|HACK|XXX",                       dir) → technical debt
```

## Shell / Bash

```text
Grep("function .*\\{|.*\\(\\) \\{",               dir) → function definitions
Grep("source |\\. /|export ",                      dir) → dependencies and env
Grep("curl |wget |ssh |scp ",                      dir) → external calls
Grep("if \\[|case |while |for ",                   dir) → control flow
```

## Tcl

```text
Grep("proc |namespace eval",                       dir) → procedures and namespaces
Grep("package require|load ",                      dir) → package dependencies
Grep("socket |http::|exec ",                       dir) → external calls
Grep("variable |upvar |global ",                   dir) → state management
```
