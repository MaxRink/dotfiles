# Go Service Code Patterns

## Project Structure

```
<service-name>/
├── go.mod
├── go.sum
├── Dockerfile
├── cmd/
│   └── server/
│       └── main.go
├── internal/
│   ├── handler/
│   │   └── order_handler.go
│   ├── service/
│   │   └── order_service.go
│   ├── domain/
│   │   ├── order.go
│   │   └── errors.go
│   ├── repository/
│   │   └── order_repository.go
│   ├── event/
│   │   └── publisher.go
│   └── config/
│       └── config.go
├── pkg/
│   └── dto/
│       ├── request.go
│       └── response.go
├── migrations/
│   └── 001_create_orders.sql
└── internal/handler/
    └── order_handler_test.go
```

## Domain Model

```go
package domain

type OrderStatus string

const (
    OrderStatusPending  OrderStatus = "PENDING"
    OrderStatusApproved OrderStatus = "APPROVED"
    OrderStatusRejected OrderStatus = "REJECTED"
)

type Order struct {
    ID         int64
    CustomerID string
    Total      float64
    Status     OrderStatus
    Lines      []OrderLine
    CreatedAt  time.Time
    UpdatedAt  time.Time
}

type OrderLine struct {
    ID        int64
    OrderID   int64
    ProductID string
    Quantity  int
    Price     float64
}
```

## Repository (Interface + Implementation)

```go
package repository

type OrderRepository interface {
    Create(ctx context.Context, order *domain.Order) error
    FindByID(ctx context.Context, id int64) (*domain.Order, error)
    FindByCustomerID(ctx context.Context, customerID string) ([]*domain.Order, error)
    UpdateStatus(ctx context.Context, id int64, status domain.OrderStatus) error
}

type postgresOrderRepo struct {
    db *sql.DB
}

func NewOrderRepository(db *sql.DB) OrderRepository {
    return &postgresOrderRepo{db: db}
}

func (r *postgresOrderRepo) Create(ctx context.Context, order *domain.Order) error {
    query := `INSERT INTO orders (customer_id, total, status, created_at) VALUES ($1, $2, $3, $4) RETURNING id`
    return r.db.QueryRowContext(ctx, query, order.CustomerID, order.Total, order.Status, time.Now()).Scan(&order.ID)
}

func (r *postgresOrderRepo) FindByID(ctx context.Context, id int64) (*domain.Order, error) {
    query := `SELECT id, customer_id, total, status, created_at FROM orders WHERE id = $1`
    order := &domain.Order{}
    err := r.db.QueryRowContext(ctx, query, id).Scan(&order.ID, &order.CustomerID, &order.Total, &order.Status, &order.CreatedAt)
    if errors.Is(err, sql.ErrNoRows) {
        return nil, domain.ErrOrderNotFound
    }
    return order, err
}
```

## Service (Business Logic)

```go
package service

type OrderService struct {
    repo      repository.OrderRepository
    validator *OrderValidator
    publisher event.Publisher
}

func NewOrderService(repo repository.OrderRepository, validator *OrderValidator, publisher event.Publisher) *OrderService {
    return &OrderService{repo: repo, validator: validator, publisher: publisher}
}

// Implements: BR-001
func (s *OrderService) CreateOrder(ctx context.Context, req dto.CreateOrderRequest) (*domain.Order, error) {
    if err := s.validator.ValidateCreditLimit(ctx, req); err != nil {
        return nil, err
    }

    order := &domain.Order{
        CustomerID: req.CustomerID,
        Total:      req.CalculateTotal(),
        Status:     domain.OrderStatusPending,
    }

    if err := s.repo.Create(ctx, order); err != nil {
        return nil, fmt.Errorf("creating order: %w", err)
    }

    s.publisher.Publish(ctx, event.OrderCreated{OrderID: order.ID, CustomerID: order.CustomerID})
    return order, nil
}
```

## Handler (HTTP)

```go
package handler

type OrderHandler struct {
    service *service.OrderService
}

func NewOrderHandler(svc *service.OrderService) *OrderHandler {
    return &OrderHandler{service: svc}
}

func (h *OrderHandler) RegisterRoutes(mux *http.ServeMux) {
    mux.HandleFunc("POST /api/orders", h.CreateOrder)
    mux.HandleFunc("GET /api/orders/{id}", h.GetOrder)
}

func (h *OrderHandler) CreateOrder(w http.ResponseWriter, r *http.Request) {
    var req dto.CreateOrderRequest
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        writeError(w, http.StatusBadRequest, "invalid request body")
        return
    }

    order, err := h.service.CreateOrder(r.Context(), req)
    if err != nil {
        var creditErr *domain.CreditLimitExceededError
        if errors.As(err, &creditErr) {
            writeError(w, http.StatusUnprocessableEntity, err.Error())
            return
        }
        writeError(w, http.StatusInternalServerError, "internal error")
        return
    }

    writeJSON(w, http.StatusCreated, dto.OrderResponseFrom(order))
}
```

## Error Types

```go
package domain

var ErrOrderNotFound = errors.New("order not found")

type CreditLimitExceededError struct {
    CustomerID string
    Requested  float64
    Available  float64
}

func (e *CreditLimitExceededError) Error() string {
    return fmt.Sprintf("credit limit exceeded for customer %s: requested %.2f, available %.2f",
        e.CustomerID, e.Requested, e.Available)
}
```

## Test Patterns (Table-Driven)

```go
func TestOrderService_CreateOrder(t *testing.T) {
    tests := []struct {
        name        string
        req         dto.CreateOrderRequest
        setupMocks  func(*mocks.MockOrderRepository, *mocks.MockPublisher)
        wantErr     bool
        wantErrType error
    }{
        {
            // Covers: TC-001
            name: "valid order created successfully",
            req:  dto.CreateOrderRequest{CustomerID: "CUST-1", Lines: []dto.OrderLineRequest{{ProductID: "P1", Qty: 2, Price: 50}}},
            setupMocks: func(repo *mocks.MockOrderRepository, pub *mocks.MockPublisher) {
                repo.EXPECT().Create(gomock.Any(), gomock.Any()).Return(nil)
                pub.EXPECT().Publish(gomock.Any(), gomock.Any()).Return(nil)
            },
            wantErr: false,
        },
        {
            // Covers: TC-002
            name: "credit limit exceeded returns error",
            req:  dto.CreateOrderRequest{CustomerID: "CUST-1", Lines: []dto.OrderLineRequest{{ProductID: "P1", Qty: 100, Price: 500}}},
            setupMocks: func(repo *mocks.MockOrderRepository, pub *mocks.MockPublisher) {},
            wantErr:     true,
            wantErrType: &domain.CreditLimitExceededError{},
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            ctrl := gomock.NewController(t)
            repo := mocks.NewMockOrderRepository(ctrl)
            pub := mocks.NewMockPublisher(ctrl)
            tt.setupMocks(repo, pub)

            svc := service.NewOrderService(repo, NewValidator(), pub)
            _, err := svc.CreateOrder(context.Background(), tt.req)

            if tt.wantErr {
                require.Error(t, err)
                if tt.wantErrType != nil {
                    require.ErrorAs(t, err, &tt.wantErrType)
                }
            } else {
                require.NoError(t, err)
            }
        })
    }
}
```
