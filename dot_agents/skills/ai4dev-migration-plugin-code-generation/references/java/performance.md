# Java Performance

GC tuning (G1/ZGC/Shenandoah), JFR/async-profiler, JMH benchmarks, heap analysis.

## Quick Reference

### JMH Benchmark

```java
@BenchmarkMode(Mode.AverageTime)
@OutputTimeUnit(TimeUnit.NANOSECONDS)
@State(Scope.Benchmark)
@Warmup(iterations = 5, time = 1)
@Measurement(iterations = 10, time = 1)
@Fork(2)
public class CollectionBenchmark {

    private List<Integer> arrayList;
    private Set<Integer> hashSet;

    @Setup
    public void setup() {
        arrayList = IntStream.range(0, 10_000).boxed().collect(Collectors.toList());
        hashSet = new HashSet<>(arrayList);
    }

    @Benchmark
    public boolean arrayListContains() {
        return arrayList.contains(5_000);
    }

    @Benchmark
    public boolean hashSetContains() {
        return hashSet.contains(5_000);
    }
}
```

### GC Tuning Presets

```bash
# Balanced (default for most apps)
-XX:+UseG1GC -XX:MaxGCPauseMillis=200
-Xms4g -Xmx4g -XX:+AlwaysPreTouch

# Low-latency
-XX:+UseZGC -XX:+ZGenerational
-Xms8g -Xmx8g

# Throughput-optimized
-XX:+UseParallelGC -XX:GCTimeRatio=99
-Xms4g -Xmx4g

# Memory-constrained
-XX:+UseSerialGC -Xms512m -Xmx512m
-XX:+UseCompressedOops -XX:MaxMetaspaceSize=128m
```

### Profiling Commands

```bash
# JFR recording
jcmd <pid> JFR.start duration=60s filename=app.jfr

# Heap dump
jmap -dump:format=b,file=heap.hprof <pid>

# GC logging
-Xlog:gc*:file=gc.log:time,level,tags:filecount=5,filesize=10m

# async-profiler (CPU)
./profiler.sh -d 30 -f profile.html <pid>

# Thread dump
jstack -l <pid> > threads.txt

# GC statistics
jstat -gcutil <pid> 1000 10
```

## Performance Anti-Patterns

| Anti-Pattern | Impact | Fix |
|-------------|--------|-----|
| String concatenation in loops | O(n²) allocation | Use StringBuilder |
| Autoboxing in hot paths | Unnecessary allocations | Use primitives |
| Excessive synchronization | Thread contention | Fine-grained locks, lock-free |
| Missing connection pooling | Resource exhaustion | HikariCP, pooled resources |
| Unbounded caches | Memory leak | Set max size, TTL |
| Reflection in hot paths | Slow method calls | Cache Method handles |

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Long GC pauses | Wrong GC or tuning | Switch to ZGC or tune G1 |
| High CPU usage | Hot loop or GC | Profile with async-profiler |
| Memory leak | Retained references | Heap dump + MAT analysis |
| Slow startup | Class loading, init | Use CDS, lazy init |
| Throughput regression | Contention | Thread dump analysis |
