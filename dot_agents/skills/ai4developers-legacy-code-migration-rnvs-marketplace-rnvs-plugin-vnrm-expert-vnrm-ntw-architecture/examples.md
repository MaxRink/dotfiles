# VNRM NTW Architecture - Usage Examples

## Example: Routing Update on Callnumber Activation

```java
@Message BusListener(topics = "vnrm.num.callnumber-activated")
public void handleCallnumberActivation(CallnumberEvent event) {
    // Update routing table
    routingService.addRoute(
        event.getOnkz(),
        event.getCallnumber(),
        event.getTargetNetwork()
    );

    // Configure network elements
    networkElementService.activateService(
        event.getCallnumber(),
        event.getServiceType()
    );
}
```

---

**See [SKILL.md](SKILL.md) and [REFERENCE.md](REFERENCE.md) for complete NTW architecture.**
