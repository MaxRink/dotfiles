# VNRM SPE Architecture - Usage Examples

Practical examples of SPE legacy integration and backend automation.

## Example 1: Database Synchronization (VNRM to RNVS)

### Scenario
NUM service updates callnumber state, SPE synchronizes to RNVS.

### Implementation
```java
@Service
public class RnvsSyncService {

    @Autowired
    private RnvsDbClient rnvsDbClient;

    @Message BusListener(topics = "vnrm.num.callnumber-updated")
    public void syncCallnumberToRnvs(CallnumberEvent event) {
        // 1. Transform VNRM to RNVS format
        RnvsRufnummer rnvsRufnr = RnvsRufnummer.builder()
            .trOnkz(event.getLocalAreaCode())
            .trRufnr(event.getCallnumber())
            .trSperre(mapStateToRnvs(event.getState()))
            .trBuchungskz(event.getBookingType())
            .trGueltigVon(event.getValidFrom())
            .trGueltigBis(event.getValidTo())
            .build();

        // 2. Update RNVS database
        rnvsDbClient.updateRufnummer(rnvsRufnr);

        // 3. Log sync operation
        syncLogRepository.save(createSyncLog(event, rnvsRufnr));
    }

    private String mapStateToRnvs(CallnumberState vnrmState) {
        // Map VNRM state codes to RNVS codes
        return switch (vnrmState) {
            case AVAILABLE -> "F";  // frei
            case RESERVED -> "R";   // reserviert
            case ACTIVATED -> "V";  // vergeben
            case BLOCKED -> "B";    // blockiert
            case WAITING -> "W";    // warten
            default -> "F";
        };
    }
}
```

## Example 2: CRM-T Integration via BEAA

### Scenario
NUM service needs to retrieve customer product information from CRM-T.

### API Call
```java
@Service
public class ProductInventoryService {

    @Autowired
    private BeaaClient beaaClient;

    public List<Product> getCustomerProducts(String phoneNumber) {
        // Call BEAA which proxies to CRM-T
        String url = String.format(
            "/beaa/crm-t/productInventory/products?phoneNumber=%s",
            phoneNumber
        );

        ProductInventoryResponse response = beaaClient.get(
            url,
            ProductInventoryResponse.class
        );

        return response.getProducts();
    }
}

// BEAA routes the request:
// Consumer: /beaa/crm-t/productInventory/products?phoneNumber=03012345678
// Forward:  /productInventory/products?phoneNumber=03012345678 (to CRM-T)
```

## Example 3: File-Based Communication via COMS

### Scenario
External partner uploads porting file via SFTP to communication server.

### File Processing
```java
@Service
public class PortingFileProcessor {

    @Scheduled(fixedDelay = 60000)  // Every minute
    public void processInboundFiles() {
        // 1. Scan communication server folder
        Path inboundDir = Paths.get("/communication-server/users/ext-sst/");

        try (DirectoryStream<Path> stream = Files.newDirectoryStream(inboundDir, "*.pda")) {
            for (Path file : stream) {
                processPortingFile(file);
            }
        } catch (IOException e) {
            logger.error("Error processing inbound files", e);
        }
    }

    private void processPortingFile(Path file) {
        // 2. Parse PDA file
        List<PdaMessage> messages = pdaParser.parse(file);

        // 3. Forward to PRT service
        messages.forEach(msg -> portingService.processPdaMessage(msg));

        // 4. Move to archive
        Path archive = Paths.get("/communication-server/archive/");
        Files.move(file, archive.resolve(file.getFileName()));
    }
}
```

---

**See [SKILL.md](SKILL.md) and [REFERENCE.md](REFERENCE.md) for complete SPE architecture.**
