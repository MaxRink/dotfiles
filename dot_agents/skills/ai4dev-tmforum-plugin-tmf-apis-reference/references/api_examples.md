# TMF API Request/Response Examples

This document provides real-world API request/response examples for common use cases.

## Product Ordering Flow

### 1. Browse Product Catalog (TMF620)

**Request**:

```http
GET /productCatalogManagement/v5/productOffering?category=mobile&lifecycleStatus=Active
Authorization: Bearer {token}
```

**Response** (200 OK):

```json
[
  {
    "id": "5G-UNLIMITED-PREMIUM",
    "href": "/productCatalogManagement/v5/productOffering/5G-UNLIMITED-PREMIUM",
    "name": "5G Unlimited Premium",
    "description": "Unlimited 5G data with premium features",
    "version": "2.0",
    "lifecycleStatus": "Active",
    "validFor": {
      "startDateTime": "2025-01-01T00:00:00Z"
    },
    "productSpecification": {
      "id": "SPEC-5G-MOBILE",
      "href": "/productCatalogManagement/v5/productSpecification/SPEC-5G-MOBILE",
      "name": "5G Mobile Service Specification"
    },
    "productOfferingPrice": [
      {
        "id": "PRICE-5G-MONTHLY",
        "name": "Monthly Subscription",
        "priceType": "recurring",
        "price": {
          "taxIncludedAmount": {
            "unit": "EUR",
            "value": 49.99
          }
        },
        "recurringChargePeriod": "monthly"
      }
    ],
    "category": [
      {
        "id": "CAT-MOBILE",
        "name": "Mobile Plans"
      }
    ]
  }
]
```

### 2. Check Product Qualification (TMF679)

**Request**:

```http
POST /productQualificationManagement/v5/productQualification
Authorization: Bearer {token}
Content-Type: application/json
```

```json
{
  "externalId": "QUAL-2025-001",
  "instantSyncQualification": true,
  "productQualificationItem": [
    {
      "id": "1",
      "action": "add",
      "product": {
        "productOffering": {
          "id": "5G-UNLIMITED-PREMIUM"
        },
        "place": [
          {
            "id": "ADDR-12345",
            "role": "installationAddress",
            "@referredType": "GeographicAddress"
          }
        ]
      }
    }
  ]
}
```

**Response** (201 Created):

```json
{
  "id": "PQ-9876",
  "href": "/productQualificationManagement/v5/productQualification/PQ-9876",
  "state": "done",
  "productQualificationItem": [
    {
      "id": "1",
      "state": "done",
      "qualificationResult": "qualified",
      "product": {
        "productOffering": {
          "id": "5G-UNLIMITED-PREMIUM"
        }
      }
    }
  ]
}
```

### 3. Submit Product Order (TMF622)

**Request**:

```http
POST /productOrderingManagement/v5/productOrder
Authorization: Bearer {token}
Content-Type: application/json
```

```json
{
  "externalId": "ORD-2025-12345",
  "orderDate": "2025-01-07T10:30:00Z",
  "requestedStartDate": "2025-01-10T00:00:00Z",
  "productOrderItem": [
    {
      "id": "1",
      "action": "add",
      "product": {
        "productOffering": {
          "id": "5G-UNLIMITED-PREMIUM",
          "href": "/productCatalogManagement/v5/productOffering/5G-UNLIMITED-PREMIUM"
        },
        "productCharacteristic": [
          {
            "name": "simType",
            "value": "eSIM"
          },
          {
            "name": "phoneNumber",
            "value": "+49151234567"
          }
        ],
        "place": [
          {
            "id": "ADDR-12345",
            "role": "installationAddress"
          }
        ]
      }
    }
  ],
  "relatedParty": [
    {
      "id": "CUST-789",
      "role": "customer",
      "@referredType": "Customer"
    }
  ],
  "billingAccount": {
    "id": "BA-456"
  }
}
```

**Response** (201 Created):

```json
{
  "id": "PO-2025-9876",
  "href": "/productOrderingManagement/v5/productOrder/PO-2025-9876",
  "externalId": "ORD-2025-12345",
  "state": "acknowledged",
  "orderDate": "2025-01-07T10:30:00Z",
  "requestedStartDate": "2025-01-10T00:00:00Z",
  "expectedCompletionDate": "2025-01-10T18:00:00Z",
  "productOrderItem": [
    {
      "id": "1",
      "state": "acknowledged",
      "action": "add",
      "product": {
        "id": "PROD-TEMP-001",
        "productOffering": {
          "id": "5G-UNLIMITED-PREMIUM"
        }
      }
    }
  ]
}
```

### 4. Track Order Status (TMF622)

**Request**:

```http
GET /productOrderingManagement/v5/productOrder/PO-2025-9876
Authorization: Bearer {token}
```

**Response** (200 OK):

```json
{
  "id": "PO-2025-9876",
  "state": "completed",
  "completionDate": "2025-01-10T14:30:00Z",
  "productOrderItem": [
    {
      "id": "1",
      "state": "completed",
      "product": {
        "id": "PROD-2025-5678",
        "href": "/productInventoryManagement/v5/product/PROD-2025-5678"
      }
    }
  ]
}
```

## Customer Management

### Create Customer (TMF629)

**Request**:

```http
POST /customerManagement/v5/customer
Authorization: Bearer {token}
Content-Type: application/json
```

```json
{
  "name": "Jane Smith",
  "status": "active",
  "engagedParty": {
    "id": "IND-12345",
    "role": "customer",
    "@referredType": "Individual"
  },
  "contactMedium": [
    {
      "mediumType": "email",
      "preferred": true,
      "characteristic": {
        "emailAddress": "jane.smith@example.com"
      }
    },
    {
      "mediumType": "phone",
      "characteristic": {
        "phoneNumber": "+49151234567",
        "phoneType": "mobile"
      }
    }
  ]
}
```

**Response** (201 Created):

```json
{
  "id": "CUST-9876",
  "href": "/customerManagement/v5/customer/CUST-9876",
  "name": "Jane Smith",
  "status": "active",
  "engagedParty": {
    "id": "IND-12345",
    "role": "customer",
    "@referredType": "Individual"
  }
}
```

## Service Provisioning

### Submit Service Order (TMF641)

**Request**:

```http
POST /serviceOrderingManagement/v5/serviceOrder
Authorization: Bearer {token}
Content-Type: application/json
```

```json
{
  "externalId": "SO-2025-001",
  "orderDate": "2025-01-07T10:30:00Z",
  "requestedStartDate": "2025-01-10T00:00:00Z",
  "serviceOrderItem": [
    {
      "id": "1",
      "action": "add",
      "service": {
        "serviceType": "mobile_broadband",
        "serviceSpecification": {
          "id": "SPEC-5G-SERVICE"
        },
        "serviceCharacteristic": [
          {
            "name": "bandwidth",
            "value": "unlimited"
          },
          {
            "name": "technology",
            "value": "5G"
          }
        ],
        "relatedParty": [
          {
            "id": "CUST-9876",
            "role": "customer"
          }
        ]
      }
    }
  ]
}
```

**Response** (201 Created):

```json
{
  "id": "SO-2025-5678",
  "href": "/serviceOrderingManagement/v5/serviceOrder/SO-2025-5678",
  "state": "acknowledged",
  "orderDate": "2025-01-07T10:30:00Z",
  "expectedCompletionDate": "2025-01-10T18:00:00Z"
}
```

## Trouble Management

### Create Trouble Ticket (TMF621)

**Request**:

```http
POST /troubleTicketManagement/v5/troubleTicket
Authorization: Bearer {token}
Content-Type: application/json
```

```json
{
  "externalId": "TICKET-2025-001",
  "description": "No internet connectivity on mobile device",
  "severity": "major",
  "priority": "2",
  "ticketType": "serviceProblem",
  "relatedParty": [
    {
      "id": "CUST-9876",
      "role": "customer",
      "@referredType": "Customer"
    }
  ],
  "relatedObject": [
    {
      "id": "PROD-2025-5678",
      "@referredType": "Product"
    }
  ]
}
```

**Response** (201 Created):

```json
{
  "id": "TT-2025-1234",
  "href": "/troubleTicketManagement/v5/troubleTicket/TT-2025-1234",
  "externalId": "TICKET-2025-001",
  "status": "acknowledged",
  "creationDate": "2025-01-07T10:30:00Z",
  "expectedResolutionDate": "2025-01-09T18:00:00Z",
  "severity": "major",
  "priority": "2"
}
```

### Update Trouble Ticket (TMF621)

**Request**:

```http
PATCH /troubleTicketManagement/v5/troubleTicket/TT-2025-1234
Authorization: Bearer {token}
Content-Type: application/json
```

```json
{
  "status": "resolved",
  "resolutionDate": "2025-01-08T14:20:00Z",
  "statusChangeReason": "Network configuration issue resolved"
}
```

## Billing and Payment

### Generate Customer Bill (TMF678)

**Request**:

```http
POST /customerBillManagement/v5/customerBill
Authorization: Bearer {token}
Content-Type: application/json
```

```json
{
  "billingAccount": {
    "id": "BA-456"
  },
  "billDate": "2025-01-31T23:59:59Z",
  "billNo": "INV-2025-001",
  "runType": "onCycle",
  "state": "new",
  "taxIncludedAmount": {
    "unit": "EUR",
    "value": 59.49
  },
  "taxExcludedAmount": {
    "unit": "EUR",
    "value": 49.99
  },
  "taxItem": [
    {
      "taxCategory": "VAT",
      "taxRate": 19.0,
      "taxAmount": {
        "unit": "EUR",
        "value": 9.50
      }
    }
  ]
}
```

### Process Payment (TMF676)

**Request**:

```http
POST /paymentManagement/v5/payment
Authorization: Bearer {token}
Content-Type: application/json
```

```json
{
  "paymentDate": "2025-02-05T10:15:00Z",
  "amount": {
    "unit": "EUR",
    "value": 59.49
  },
  "paymentMethod": {
    "id": "PM-CARD-789",
    "@type": "CreditCard"
  },
  "relatedParty": [
    {
      "id": "CUST-9876",
      "role": "payer"
    }
  ],
  "bill": [
    {
      "id": "CB-2025-001",
      "@referredType": "CustomerBill"
    }
  ]
}
```

**Response** (201 Created):

```json
{
  "id": "PAY-2025-5678",
  "href": "/paymentManagement/v5/payment/PAY-2025-5678",
  "status": "completed",
  "paymentDate": "2025-02-05T10:15:00Z",
  "amount": {
    "unit": "EUR",
    "value": 59.49
  },
  "authorizationCode": "AUTH-XYZ123"
}
```

## Event Notifications

### Product Order Created Event

```json
{
  "eventId": "evt-2025-001",
  "eventTime": "2025-01-07T10:30:05Z",
  "eventType": "ProductOrderCreatedEvent",
  "correlationId": "corr-12345",
  "domain": "productOrderingManagement",
  "title": "Product Order Created",
  "description": "A new product order has been created",
  "priority": "3",
  "timeOcurred": "2025-01-07T10:30:00Z",
  "event": {
    "productOrder": {
      "id": "PO-2025-9876",
      "href": "/productOrderingManagement/v5/productOrder/PO-2025-9876",
      "state": "acknowledged"
    }
  }
}
```

### Product Order State Change Event

```json
{
  "eventId": "evt-2025-002",
  "eventTime": "2025-01-10T14:30:05Z",
  "eventType": "ProductOrderStateChangeEvent",
  "event": {
    "productOrder": {
      "id": "PO-2025-9876",
      "state": "completed",
      "completionDate": "2025-01-10T14:30:00Z"
    }
  }
}
```

### Trouble Ticket Resolved Event

```json
{
  "eventId": "evt-2025-003",
  "eventTime": "2025-01-08T14:20:05Z",
  "eventType": "TroubleTicketResolvedEvent",
  "event": {
    "troubleTicket": {
      "id": "TT-2025-1234",
      "status": "resolved",
      "resolutionDate": "2025-01-08T14:20:00Z"
    }
  }
}
```

## Error Responses

### 400 Bad Request

```json
{
  "code": "400",
  "reason": "Bad Request",
  "message": "Invalid product offering reference: Product offering '5G-INVALID' does not exist",
  "status": "400",
  "@type": "Error"
}
```

### 404 Not Found

```json
{
  "code": "404",
  "reason": "Not Found",
  "message": "Product order 'PO-INVALID' not found",
  "status": "404",
  "@type": "Error"
}
```

### 500 Internal Server Error

```json
{
  "code": "500",
  "reason": "Internal Server Error",
  "message": "An unexpected error occurred while processing the request",
  "status": "500",
  "@type": "Error"
}
```

---

These examples demonstrate typical TMF API patterns and payloads. Adapt them to your specific implementation requirements.
