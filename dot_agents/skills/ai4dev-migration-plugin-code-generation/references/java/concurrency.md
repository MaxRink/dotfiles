# Java Concurrency

Threads, executors, CompletableFuture, virtual threads (Java 21+), synchronization, structured concurrency.

## Quick Reference

```java
// Virtual Threads (Java 21+)
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    IntStream.range(0, 10_000).forEach(i ->
        executor.submit(() -> processRequest(i)));
}

// CompletableFuture composition
CompletableFuture<Result> result = fetchUser(id)
    .thenCompose(user -> fetchOrders(user.id()))
    .thenApply(orders -> processOrders(orders))
    .exceptionally(ex -> handleError(ex))
    .orTimeout(5, TimeUnit.SECONDS);

// Thread pool configuration
ThreadPoolExecutor executor = new ThreadPoolExecutor(
    10, 50, 60L, TimeUnit.SECONDS,
    new ArrayBlockingQueue<>(1000),
    new ThreadPoolExecutor.CallerRunsPolicy()
);

// Lock with timeout
ReentrantLock lock = new ReentrantLock();
if (lock.tryLock(1, TimeUnit.SECONDS)) {
    try {
        // critical section
    } finally {
        lock.unlock();
    }
}
```

## Thread Pool Sizing

| Workload | Formula | Example (8 cores) |
|----------|---------|-------------------|
| CPU-bound | cores | 8 threads |
| I/O-bound | cores × (1 + wait/compute) | 80 threads |
| Mixed | Profile and measure | Benchmark first |

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Deadlock | Circular lock | Lock ordering, tryLock |
| Race condition | Missing sync | Add locks/atomics |
| Thread starvation | Unfair scheduling | Fair locks |
| Livelock | Threads keep yielding | Randomized backoff |
| Memory visibility | Missing volatile | Apply happens-before |

### Debug Commands

```bash
jstack -l <pid> > threaddump.txt   # Thread dump
jcmd <pid> Thread.print             # Thread info
```
