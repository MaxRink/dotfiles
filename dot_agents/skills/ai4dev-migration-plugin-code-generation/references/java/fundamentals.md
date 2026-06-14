# Java Fundamentals

Core Java 8–21: syntax, OOP, records, sealed classes, pattern matching, collections, streams, exception handling.

## Quick Reference

```java
// Record (Java 16+)
public record User(String name, String email) {}

// Pattern matching (Java 21)
String format(Object obj) {
    return switch (obj) {
        case Integer i -> "Int: %d".formatted(i);
        case String s  -> "String: %s".formatted(s);
        default        -> obj.toString();
    };
}

// Stream operations
List<String> names = users.stream()
    .filter(User::isActive)
    .map(User::getName)
    .sorted()
    .toList();

// Optional handling
String name = Optional.ofNullable(user)
    .map(User::getName)
    .orElse("Unknown");
```

## Collection Selection Guide

| Need | Use | Reason |
|------|-----|--------|
| Indexed access | ArrayList | O(1) random access |
| Unique elements | HashSet | O(1) contains |
| Sorted unique | TreeSet | O(log n) sorted |
| Key-value pairs | HashMap | O(1) get/put |
| Thread-safe map | ConcurrentHashMap | Segment locking |
| FIFO queue | ArrayDeque | Fast at both ends |

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| NullPointerException | Null reference | Use Optional |
| ConcurrentModificationException | Modify during iteration | Iterator.remove() |
| ClassCastException | Wrong type | Use generics |
| OutOfMemoryError | Large collections | Profile heap, weak references |
| StackOverflowError | Infinite recursion | Add base case |
