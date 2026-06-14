# OpenAPI Patterns Reference

## Standard OpenAPI 3.1 Template

```yaml
openapi: 3.1.0
info:
  title: Service Name API
  version: 1.0.0
  description: Brief description of the API
  contact:
    name: Team Name
    email: team@telekom.de

servers:
  - url: https://api.example.com/v1
    description: Production
  - url: https://api.staging.example.com/v1
    description: Staging

security:
  - bearerAuth: []

paths:
  /resources:
    get:
      summary: List resources
      operationId: listResources
      tags: [resources]
      parameters:
        - $ref: '#/components/parameters/PageSize'
        - $ref: '#/components/parameters/PageCursor'
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ResourceList'
        '401':
          $ref: '#/components/responses/Unauthorized'

    post:
      summary: Create a resource
      operationId: createResource
      tags: [resources]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateResourceRequest'
      responses:
        '201':
          description: Created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Resource'
        '400':
          $ref: '#/components/responses/BadRequest'
        '409':
          $ref: '#/components/responses/Conflict'

  /resources/{id}:
    get:
      summary: Get a resource
      operationId: getResource
      tags: [resources]
      parameters:
        - $ref: '#/components/parameters/ResourceId'
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Resource'
        '404':
          $ref: '#/components/responses/NotFound'

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  parameters:
    ResourceId:
      name: id
      in: path
      required: true
      schema:
        type: string
        format: uuid
    PageSize:
      name: size
      in: query
      schema:
        type: integer
        default: 20
        maximum: 100
    PageCursor:
      name: cursor
      in: query
      schema:
        type: string

  schemas:
    Resource:
      type: object
      required: [id, name, created_at]
      properties:
        id:
          type: string
          format: uuid
        name:
          type: string
          maxLength: 255
        description:
          type: string
        status:
          type: string
          enum: [active, inactive, archived]
        created_at:
          type: string
          format: date-time
        updated_at:
          type: string
          format: date-time

    CreateResourceRequest:
      type: object
      required: [name]
      properties:
        name:
          type: string
          maxLength: 255
        description:
          type: string

    ResourceList:
      type: object
      properties:
        data:
          type: array
          items:
            $ref: '#/components/schemas/Resource'
        pagination:
          $ref: '#/components/schemas/Pagination'

    Pagination:
      type: object
      properties:
        total_count:
          type: integer
        next_cursor:
          type: string
          nullable: true
        has_more:
          type: boolean

    Error:
      type: object
      required: [error]
      properties:
        error:
          type: object
          required: [code, message]
          properties:
            code:
              type: string
            message:
              type: string
            details:
              type: array
              items:
                type: object
                properties:
                  field:
                    type: string
                  issue:
                    type: string
            trace_id:
              type: string

  responses:
    BadRequest:
      description: Bad Request
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
    Unauthorized:
      description: Unauthorized
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
    NotFound:
      description: Not Found
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
    Conflict:
      description: Conflict
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
```

## Common Patterns

### Pagination
- Cursor-based (recommended for large datasets)
- Offset-based (simpler, fine for small datasets)
- Always include `total_count` and `has_more`

### Filtering
```
GET /orders?status=active&created_after=2024-01-01&sort=-created_at
```

### Bulk Operations
```yaml
POST /resources/bulk
requestBody:
  content:
    application/json:
      schema:
        type: object
        properties:
          operations:
            type: array
            maxItems: 100
            items:
              type: object
              properties:
                action:
                  enum: [create, update, delete]
                data:
                  $ref: '#/components/schemas/Resource'
```

### Webhooks
```yaml
webhooks:
  resourceCreated:
    post:
      summary: Resource created event
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                event_type:
                  const: resource.created
                timestamp:
                  type: string
                  format: date-time
                data:
                  $ref: '#/components/schemas/Resource'
```
