# User Journey

For mapping user experience flows with satisfaction scores.

## Syntax

```
journey
  title User Checkout Flow
  section Browse
    Visit homepage: 5: User
    Search product: 4: User
    View details: 4: User
  section Purchase
    Add to cart: 5: User
    Enter payment: 2: User
    Confirm order: 4: User, System
  section Post-Purchase
    Receive confirmation: 5: System
    Track delivery: 3: User
```

**Format:** `Task name: score: actor1, actor2` where score is 1-5 (5 = best).
