# VNRM PRT Architecture - Usage Examples

Practical examples of how agents use PRT architecture knowledge during phases 6-12.

## Example 1: PDA Message Processing (FBPM)

### Scenario
Process incoming PDA file with L (Export) and P (Import) messages.

### Implementation
```java
@Service
public class PdaMessageProcessor {

    public void processPdaFile(File pdaFile) {
        // 1. Parse PDA file
        List<PdaMessage> messages = pdaParser.parse(pdaFile);

        // 2. Validate syntax
        messages.forEach(msg -> {
            if (!validator.validateSyntax(msg)) {
                createOrder(msg, OrderState.PROBLEM);
                return;
            }
            createOrder(msg, OrderState.CHECKED);
        });

        // 3. Check for paired messages
        matchPairedMessages(messages);
    }

    private void matchPairedMessages(List<PdaMessage> messages) {
        Map<String, List<PdaMessage>> grouped = messages.stream()
            .collect(Collectors.groupingBy(PdaMessage::getCallnumber));

        grouped.forEach((callnumber, msgs) -> {
            PdaMessage lMsg = findByStatus(msgs, "L");
            PdaMessage pMsg = findByStatus(msgs, "P");

            if (lMsg != null && pMsg != null && isMatched(lMsg, pMsg)) {
                // Paired messages matched
                updateOrderState(callnumber, OrderState.PORTED);
                publishPortingEvent(callnumber, lMsg, pMsg);
            } else if (lMsg != null || pMsg != null) {
                // Single message received, waiting for pair
                updateOrderState(callnumber, OrderState.WAITING);
            }
        });
    }

    private boolean isMatched(PdaMessage lMsg, PdaMessage pMsg) {
        return lMsg.getPortingDate().equals(pMsg.getPortingDate())
            && lMsg.getPkAb().equals(pMsg.getPkAb())
            && lMsg.getPkAuf().equals(pMsg.getPkAuf());
    }
}
```

## Example 2: Automated Import Workflow (FCPM)

### Scenario
LWL triggers automated porting import with parallel booking.

### Workflow Sequence
```java
@Service
public class AutomatedPortingService {

    @Transactional
    public void handleLwlTrigger(LwlPortingNotification notification) {
        // 1. Parallel processing: Import + Booking
        CompletableFuture<Void> importFuture = CompletableFuture.runAsync(() ->
            importCallnumber(notification.getCallnumber())
        );

        CompletableFuture<Void> bookingFuture = CompletableFuture.runAsync(() ->
            bookCallnumber(notification.getCallnumber(), notification.getCustomerId())
        );

        // 2. Wait for both operations
        CompletableFuture.allOf(importFuture, bookingFuture).join();

        // 3. Confirm to CRM-T
        crmTClient.confirmNumberAllocation(
            notification.getCallnumber(),
            notification.getCustomerId()
        );

        // 4. Set provisional import status
        callnumberService.updateState(
            notification.getCallnumber(),
            CallnumberState.PROVISIONAL_IMPORT
        );

        // 5. Wait for LWL implementation
        lwlImplementationTracker.register(notification.getCallnumber());
    }

    @EventListener
    public void handleLwlImplementation(LwlImplementationEvent event) {
        // 6. Trigger PDA_MESSAGE_OUT
        generatePdaMessage(event.getCallnumber(), PdaStatus.P);

        // 7. Distribute to all TNBs
        pdaDistributionService.distributeToAllTnbs(
            event.getCallnumber(),
            PdaStatus.P
        );
    }
}
```

## Example 3: Porting State Machine

### State Transition Example
```java
public class PortingOrderStateMachine {

    public void transitionState(PortingOrder order, OrderEvent event) {
        switch (order.getState()) {
            case CHECKED:
                if (event == OrderEvent.CRM_T_CONFIRMED) {
                    order.setState(OrderState.PROVISIONAL_IMPORT);
                } else if (event == OrderEvent.VALIDATION_ERROR) {
                    order.setState(OrderState.PROBLEM);
                }
                break;

            case PROVISIONAL_IMPORT:
                if (event == OrderEvent.LWL_IMPLEMENTED) {
                    order.setState(OrderState.PORTED);
                }
                break;

            case WAITING:
                if (event == OrderEvent.PAIRED_MESSAGE_RECEIVED) {
                    order.setState(OrderState.PORTED);
                } else if (event == OrderEvent.TIMEOUT) {
                    order.setState(OrderState.PROBLEM);
                }
                break;

            case PROBLEM:
                if (event == OrderEvent.MANUAL_CORRECTION) {
                    order.setState(OrderState.CORRECTION);
                } else if (event == OrderEvent.REJECT) {
                    order.setState(OrderState.REJECTED);
                }
                break;
        }

        portingOrderRepository.save(order);
        auditService.logStateChange(order, event);
    }
}
```

## Example 4: Integration with NUM Services

### Scenario
Update NUM callnumber state after successful porting.

### Event-Driven Integration
```java
@Service
public class PortingEventPublisher {

    @Autowired
    private Message BusTemplate<String, PortingEvent> message_busTemplate;

    public void publishPortingCompleted(PortingOrder order) {
        PortingEvent event = PortingEvent.builder()
            .callnumber(order.getCallnumber())
            .onkz(order.getOnkz())
            .pkOld(order.getPkAb())
            .pkNew(order.getPkAuf())
            .portingDate(order.getPortingDate())
            .state(PortingState.COMPLETED)
            .timestamp(LocalDateTime.now())
            .build();

        // Publish to Message Bus topic for NUM consumption
        message_busTemplate.send("vnrm.prt.porting-completed", event);
    }
}

// NUM Service consumes the event
@Service
public class CallnumberPortingListener {

    @Message BusListener(topics = "vnrm.prt.porting-completed")
    public void handlePortingCompleted(PortingEvent event) {
        // Update callnumber state in NUM
        Callnumber cn = callnumberRepository.findById(event.getCallnumber())
            .orElseThrow();

        cn.setState(CallnumberState.ACTIVATED);
        cn.setPortingDate(event.getPortingDate());
        callnumberRepository.save(cn);

        // Log modification
        modificationService.logPortingCompleted(cn, event);
    }
}
```

---

**See [SKILL.md](SKILL.md) and [REFERENCE.md](REFERENCE.md) for complete PRT architecture.**
