# ZenUML

Alternative sequence diagram syntax using code-like notation. Requires external plugin.

## Syntax

```
zenuml
  A -> B.method() {
    B -> C.query() {
      return result
    }
    if (condition) {
      B -> D.notify()
    } else {
      B -> E.fallback()
    }
  }
```

**Messages:** `->` sync, `=>` async, `-> new B` creation
**Fragments:** `if/else`, `while/for/loop`, `try/catch/finally`, `par`, `opt`
**Note:** Uses different syntax than standard `sequenceDiagram`.
