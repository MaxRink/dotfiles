# Quarkus Security

Quarkus security: OIDC, JWT, RBAC, input validation, CSRF, CORS, secrets management, and security headers.

## Quick Reference

```java
// Secure endpoint with role check
@Path("/admin")
@RolesAllowed("admin")
public class AdminResource {

    @GET
    @Path("/users")
    public List<User> getAllUsers() {
        // Only accessible to admin role
    }
}

// Get current user
@Inject
SecurityIdentity securityIdentity;

String username = securityIdentity.getPrincipal().getName();
boolean isAdmin = securityIdentity.hasRole("admin");
```

## JWT Authentication

### Configuration

```properties
# JWT RBAC
quarkus.smallrye-jwt.enabled=true
mp.jwt.verify.publickey.location=META-INF/resources/publicKey.pem
mp.jwt.verify.issuer=https://your-issuer.com

# OIDC (OpenID Connect)
quarkus.oidc.auth-server-url=https://auth.example.com/realms/myrealm
quarkus.oidc.client-id=my-app
quarkus.oidc.credentials.secret=${OIDC_CLIENT_SECRET}
quarkus.oidc.tls.verification=required

# Token validation
quarkus.oidc.token.issuer=https://auth.example.com/realms/myrealm
quarkus.oidc.token.audience=my-app
```

### Secure Endpoints

```java
@Path("/api/users")
public class UserResource {

    @Inject
    JsonWebToken jwt;

    @Inject
    SecurityIdentity securityIdentity;

    // Authenticated users only
    @GET
    @Authenticated
    public List<User> list() {
        String userId = jwt.getSubject();
        return userService.findAll();
    }

    // Specific roles required
    @POST
    @RolesAllowed({"user", "admin"})
    public Response create(CreateUserRequest request) {
        // Accessible to user or admin roles
    }

    // Admin only
    @DELETE
    @Path("/{id}")
    @RolesAllowed("admin")
    public Response delete(@PathParam("id") Long id) {
        // Only admin can delete
    }

    // Public endpoint
    @GET
    @Path("/public")
    @PermitAll
    public Response publicEndpoint() {
        return Response.ok("Public access").build();
    }
}
```

### Access Token Claims

```java
@Path("/profile")
@Authenticated
public class ProfileResource {

    @Inject
    JsonWebToken jwt;

    @GET
    public UserProfile getProfile() {
        String userId = jwt.getSubject();
        String email = jwt.getClaim("email");
        Set<String> groups = jwt.getGroups();
        String name = jwt.getClaim("name");

        return new UserProfile(userId, email, name, groups);
    }
}
```

## RBAC (Role-Based Access Control)

### Annotation-Based Security

```java
// Class-level security
@Path("/admin")
@RolesAllowed("admin")
public class AdminResource {

    @GET
    public String adminOnly() {
        return "Admin content";
    }

    // Override class-level security
    @GET
    @Path("/public-stats")
    @PermitAll
    public Stats getPublicStats() {
        return statsService.getPublicStats();
    }
}

// Method-level security
@ApplicationScoped
public class UserService {

    @RolesAllowed("admin")
    public void deleteUser(Long id) {
        // Only admin can call this
    }

    @RolesAllowed({"user", "admin"})
    public User updateProfile(Long id, UpdateProfileRequest request) {
        // User can update own profile, admin can update any
    }
}
```

### Programmatic Security Checks

```java
@Inject
SecurityIdentity securityIdentity;

public void updateUser(Long id, UpdateUserRequest request) {
    // Check if user is authenticated
    if (securityIdentity.isAnonymous()) {
        throw new UnauthorizedException("Authentication required");
    }

    // Check specific role
    if (!securityIdentity.hasRole("admin")) {
        // Users can only update their own profile
        String currentUserId = securityIdentity.getPrincipal().getName();
        if (!id.toString().equals(currentUserId)) {
            throw new ForbiddenException("Cannot update other users");
        }
    }

    // Proceed with update
}
```

## Input Validation

### Bean Validation

```java
public record CreateUserRequest(
    @NotBlank(message = "Name is required")
    @Size(min = 2, max = 100, message = "Name must be 2-100 characters")
    @Pattern(regexp = "^[a-zA-Z ]+$", message = "Name must contain only letters")
    String name,

    @NotBlank(message = "Email is required")
    @Email(message = "Invalid email format")
    String email,

    @NotBlank(message = "Password is required")
    @Size(min = 8, max = 100, message = "Password must be 8-100 characters")
    @Pattern(
        regexp = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$!%*?&])[A-Za-z\\d@$!%*?&]{8,}$",
        message = "Password must contain uppercase, lowercase, digit, and special character"
    )
    String password,

    @NotNull(message = "Role is required")
    @Pattern(regexp = "^(USER|ADMIN)$", message = "Invalid role")
    String role
) {}

// In resource - validation automatic with @Valid
@POST
public Response create(@Valid CreateUserRequest request) {
    // request is validated before reaching here
}
```

### Path/Query Parameter Validation

```java
@Path("/users")
public class UserResource {

    @GET
    @Path("/{id}")
    public UserResponse getById(
        @PathParam("id")
        @Min(1) @Max(Long.MAX_VALUE)
        Long id
    ) {
        return userService.findById(id);
    }

    @GET
    public List<UserResponse> search(
        @QueryParam("page")
        @DefaultValue("0") @Min(0)
        int page,

        @QueryParam("size")
        @DefaultValue("20") @Min(1) @Max(100)
        int size,

        @QueryParam("email")
        @Email
        String email
    ) {
        return userService.search(email, page, size);
    }
}
```

## CORS Configuration

```properties
# Basic CORS
quarkus.http.cors=true
quarkus.http.cors.origins=http://localhost:3000,https://app.example.com
quarkus.http.cors.methods=GET,POST,PUT,DELETE,OPTIONS
quarkus.http.cors.headers=accept,authorization,content-type,x-requested-with
quarkus.http.cors.exposed-headers=Content-Disposition
quarkus.http.cors.access-control-max-age=24H
quarkus.http.cors.access-control-allow-credentials=true

# Multiple origins with wildcards
quarkus.http.cors.origins=/https://.*\\.example\\.com/
```

## CSRF Protection

```properties
# Enable CSRF protection
quarkus.rest-csrf.enabled=true
quarkus.rest-csrf.cookie-name=csrf-token
quarkus.rest-csrf.cookie-path=/
quarkus.rest-csrf.cookie-max-age=1H

# Form authentication CSRF
quarkus.csrf-reactive.enabled=true
```

```java
// Include CSRF token in forms
@Path("/form")
public class FormResource {

    @Inject
    CsrfTokenParameterProvider csrfToken;

    @GET
    @Produces(MediaType.TEXT_HTML)
    public String getForm() {
        return """
            <form method="POST" action="/form/submit">
                <input type="hidden" name="%s" value="%s">
                <input type="text" name="data">
                <button type="submit">Submit</button>
            </form>
            """.formatted(csrfToken.getParameterName(), csrfToken.getToken());
    }

    @POST
    @Path("/submit")
    public Response submit(@FormParam("data") String data) {
        // CSRF validation happens automatically
        return Response.ok().build();
    }
}
```

## Secrets Management

### Environment Variables

```properties
# Use environment variables for secrets
quarkus.datasource.password=${DB_PASSWORD}
quarkus.oidc.credentials.secret=${OIDC_CLIENT_SECRET}
app.api-key=${API_KEY}

# Vault integration
quarkus.vault.url=http://localhost:8200
quarkus.vault.authentication.kubernetes.role=my-role
quarkus.vault.secret-config-kv-path=secret/myapp
```

### Vault Configuration

```java
@ConfigMapping(prefix = "app")
public interface AppConfig {
    // Automatically fetched from Vault
    String apiKey();
    String databasePassword();
}
```

## Security Headers

```java
@Provider
public class SecurityHeadersFilter implements ContainerResponseFilter {

    @Override
    public void filter(ContainerRequestContext request,
                      ContainerResponseContext response) {
        MultivaluedMap<String, Object> headers = response.getHeaders();

        // Prevent clickjacking
        headers.add("X-Frame-Options", "DENY");

        // Prevent MIME sniffing
        headers.add("X-Content-Type-Options", "nosniff");

        // XSS Protection
        headers.add("X-XSS-Protection", "1; mode=block");

        // Content Security Policy
        headers.add("Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'");

        // HSTS (HTTPS only)
        headers.add("Strict-Transport-Security",
            "max-age=31536000; includeSubDomains");

        // Referrer Policy
        headers.add("Referrer-Policy", "no-referrer");

        // Permissions Policy
        headers.add("Permissions-Policy",
            "geolocation=(), microphone=(), camera=()");
    }
}
```

## Password Hashing

```java
@ApplicationScoped
public class PasswordService {

    @Inject
    BcryptUtil bcrypt;  // Quarkus provides this

    public String hashPassword(String plainPassword) {
        return bcrypt.bcryptHash(plainPassword);
    }

    public boolean verifyPassword(String plainPassword, String hashedPassword) {
        return bcrypt.matches(plainPassword, hashedPassword);
    }
}

// Using Argon2 (recommended for new apps)
@ApplicationScoped
public class Argon2PasswordService {

    private final Argon2 argon2 = Argon2Factory.create(
        Argon2Factory.Argon2Types.ARGON2id,
        32,  // Salt length
        64   // Hash length
    );

    public String hashPassword(String plainPassword) {
        return argon2.hash(2, 65536, 1, plainPassword.toCharArray());
    }

    public boolean verifyPassword(String plainPassword, String hashedPassword) {
        return argon2.verify(hashedPassword, plainPassword.toCharArray());
    }
}
```

## Rate Limiting

```properties
# Redis-based rate limiting
quarkus.redis.hosts=redis://localhost:6379
```

```java
@ApplicationScoped
public class RateLimiter {

    @Inject
    RedisClient redis;

    public boolean allowRequest(String userId, int maxRequests, Duration window) {
        String key = "ratelimit:" + userId;
        String count = redis.get(key);

        if (count == null) {
            redis.setex(key, window.getSeconds(), "1");
            return true;
        }

        int currentCount = Integer.parseInt(count);
        if (currentCount >= maxRequests) {
            return false;
        }

        redis.incr(key);
        return true;
    }
}

// Filter for rate limiting
@Provider
@Priority(1000)
public class RateLimitFilter implements ContainerRequestFilter {

    @Inject
    RateLimiter rateLimiter;

    @Inject
    SecurityIdentity securityIdentity;

    @Override
    public void filter(ContainerRequestContext context) {
        if (securityIdentity.isAnonymous()) {
            return;
        }

        String userId = securityIdentity.getPrincipal().getName();
        boolean allowed = rateLimiter.allowRequest(userId, 100, Duration.ofMinutes(1));

        if (!allowed) {
            context.abortWith(
                Response.status(429)
                    .entity(Map.of("error", "Rate limit exceeded"))
                    .build()
            );
        }
    }
}
```

## OAuth2 Client

```properties
# OAuth2 client configuration
quarkus.oidc-client.auth-server-url=https://auth.example.com/realms/myrealm
quarkus.oidc-client.client-id=backend-service
quarkus.oidc-client.credentials.secret=${OAUTH2_CLIENT_SECRET}
quarkus.oidc-client.grant.type=client_credentials
```

```java
@ApplicationScoped
public class ExternalApiClient {

    @Inject
    @Named("oidc-client")
    Tokens tokens;

    public String callExternalApi() {
        String accessToken = tokens.getAccessToken();

        // Use token to call external API
        return restClient.get()
            .header("Authorization", "Bearer " + accessToken)
            .retrieve()
            .bodyToMono(String.class)
            .block();
    }
}
```

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| 401 Unauthorized | Missing/invalid token | Check token format and signature |
| 403 Forbidden | Insufficient permissions | Verify user roles match @RolesAllowed |
| CORS errors | Misconfigured origins | Add origin to quarkus.http.cors.origins |
| Token validation fails | Wrong public key | Verify mp.jwt.verify.publickey.location |
| SecurityIdentity is null | Not authenticated endpoint | Add @Authenticated or @RolesAllowed |
