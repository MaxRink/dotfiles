# VNRM COR Architecture - Usage Examples

Practical examples of COR business error management.

## Example 1: NUM Service Reports Error

### Scenario
NUM callnumber reservation fails due to database constraint violation.

### Error Reporting
```java
@Service
public class CallnumberService {

    @Autowired
    private CorErrorReportingClient corClient;

    public void reserveCallnumber(String onkz, String callnumber) {
        try {
            // Attempt reservation
            doReserve(onkz, callnumber);
        } catch (DataIntegrityViolationException e) {
            // Report to COR
            corClient.reportError(
                "NUM-C-0001",
                "NUM-FCM",
                Map.of(
                    "onkz", onkz,
                    "callnumber", callnumber,
                    "operation", "RESERVE",
                    "errorMessage", e.getMessage(),
                    "sqlState", e.getSQLException().getSQLState()
                )
            );
            throw new CallnumberReservationException(e);
        }
    }
}
```

## Example 2: Error Order Analysis

### Root Cause Investigation Workflow
```java
@Service
public class ErrorAnalysisService {

    public RootCauseAnalysis analyzeError(Long orderId) {
        ErrorManagementOrder order = orderRepository.findById(orderId)
            .orElseThrow();

        // 1. Retrieve error details from COM catalog
        ErrorCatalogEntry catalogEntry =
            errorCatalogClient.getError(order.getErrorCode());

        // 2. Find similar historical errors
        List<ErrorManagementOrder> similarErrors =
            findSimilarErrors(order);

        // 3. Analyze timeline
        Timeline timeline = buildTimeline(order);

        // 4. Assess impact
        ImpactAssessment impact = assessImpact(order);

        return RootCauseAnalysis.builder()
            .order(order)
            .catalogEntry(catalogEntry)
            .similarErrors(similarErrors)
            .timeline(timeline)
            .impact(impact)
            .build();
    }
}
```

## Example 3: Error Resolution Action

### Manual Correction Workflow
```java
@Service
public class ErrorResolutionService {

    public void resolveError(Long orderId, ResolutionAction action) {
        ErrorManagementOrder order = orderRepository.findById(orderId)
            .orElseThrow();

        // 1. Execute resolution action
        switch (action.getType()) {
            case MANUAL_CORRECTION:
                executeManualCorrection(order, action);
                break;
            case PROCESS_RETRY:
                retryFailedProcess(order);
                break;
            case ESCALATE:
                escalateToDevelopment(order, action);
                break;
        }

        // 2. Update order status
        order.setStatus(OrderStatus.RESOLVED);
        order.setResolvedAt(LocalDateTime.now());
        order.setResolvedBy(action.getUserId());

        // 3. Log audit trail
        auditService.logResolution(order, action);

        // 4. Notify affected services
        notificationService.notifyResolution(order);
    }
}
```

---

**See [SKILL.md](SKILL.md) and [REFERENCE.md](REFERENCE.md) for complete COR architecture.**
