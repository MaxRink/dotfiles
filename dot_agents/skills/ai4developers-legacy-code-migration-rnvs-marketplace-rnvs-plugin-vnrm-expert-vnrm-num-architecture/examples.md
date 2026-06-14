# VNRM NUM Architecture - Usage Examples

Practical examples of how agents use NUM architecture knowledge during phases 6-12.

## Example 1: Reserve Single Callnumber (FCM)

### Scenario
Reserve a Berlin number (ONKZ 030) for a customer.

### Implementation
```java
@RestController
@RequestMapping("/api/v1/callnumbers")
public class CallnumberController {

    @PostMapping("/reserve")
    public ResponseEntity<CallnumberReservationResponse> reserveCallnumber(
            @RequestBody CallnumberReservationRequest request) {

        // 1. Validate ONKZ via COM RDM
        rdmClient.validateOnkz(request.getOnkz());

        // 2. Find available callnumber
        Callnumber callnumber = callnumberService.findAvailable(
            request.getOnkz(),
            CallnumberType.SINGLE
        );

        // 3. Reserve with 24h timeout
        CallnumberReservation reservation = callnumberService.reserve(
            callnumber,
            Duration.ofHours(24)
        );

        return ResponseEntity.ok(reservation.toResponse());
    }
}
```

## Example 2: Query Number Block Inventory (NBIM)

### Scenario
Find all available blocks in Munich (ONKZ 089).

### API Query
```bash
GET /api/v1/blocks/by-onkz/089?state=FREE&page=1&size=20
```

**Response:**
```json
{
  "blocks": [
    {
      "block_id": "089456",
      "ndc": "089",
      "block_size": 10000,
      "block_owner_legal": "D001",
      "block_state": "FREE",
      "load_capacity": 0
    }
  ],
  "total": 3
}
```

## Example 3: Callnumber State Machine

### State Transition Diagram
```
[AVAILABLE] --reserve--> [RESERVED] --activate--> [ACTIVATED]
     ^           |                                     |
     |        timeout                              terminate
     |           v                                     v
     +----<----[AVAILABLE]<----expire-----[WAITING]
```

### Usage in Code
```java
public void processReservationTimeout() {
    List<Callnumber> expiredReservations =
        callnumberRepository.findExpiredReservations();

    expiredReservations.forEach(cn -> {
        // Transition: RESERVED → AVAILABLE
        cn.setState(CallnumberState.AVAILABLE);
        cn.setBookingIdVnrm(null);

        // Log modification
        modificationService.logStateChange(
            cn,
            ChangeReason.RESERVATION_TIMEOUT,
            "System"
        );
    });
}
```

---

**See [SKILL.md](SKILL.md) and [REFERENCE.md](REFERENCE.md) for complete NUM architecture.**
