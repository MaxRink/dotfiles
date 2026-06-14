# Troubleshooting

This document provides diagnostic procedures and solutions for common microfrontend migration issues.

---

## Quick Diagnosis Flowchart

```
Problem Category
├── Build Issues
│   ├── TypeScript errors → Check tsconfig.json
│   ├── Missing modules → Check package.json, npm install
│   └── Vite errors → Check vite.config.ts
│
├── Runtime Issues
│   ├── App doesn't mount → Check lifecycle exports
│   ├── Blank screen → Check console for errors
│   ├── CSS not applied → Check CSS injection plugin
│   └── Routes don't work → Check router configuration
│
├── Container Integration
│   ├── Context undefined → Check createContext usage
│   ├── Events not firing → Check eventBus usage
│   ├── IDP errors → Check token handling
│   └── Config not loading → Check fetch path
│
└── Deployment Issues
    ├── Container won't start → Check Dockerfile
    ├── 404 errors → Check nginx config
    ├── Health check fails → Check probe endpoints
    └── Config not applied → Check ConfigMap mounting
```

---

## Build Issues

### TypeScript Compilation Errors

**Symptom**: `npm run build` fails with TypeScript errors

**Diagnostic Steps**:

```bash
# Run type check only
npm run type-check

# Check TypeScript version
npm ls typescript

# Verify tsconfig.json exists and is valid
cat tsconfig.json | jq .
```

**Common Causes and Solutions**:

| Error | Cause | Solution |
|-------|-------|----------|
| `Cannot find module 'vue'` | Missing peer dependency | `npm install vue@^3.5.0` |
| `JSX element 'scale-*'...` | Missing JSX declarations | Add to `env.d.ts` |
| `Property 'x' does not exist` | Strict mode issue | Check type definitions |
| `Module 'x' has no exported member` | Wrong import | Use `import type` for types |

**Fix for Scale component JSX errors**:

```typescript
// env.d.ts
declare namespace JSX {
  interface IntrinsicElements {
    [elemName: `scale-${string}`]: any;
  }
}
```

---

### Vite Build Errors

**Symptom**: Build fails with Vite/Rollup errors

**Diagnostic Steps**:

```bash
# Clean and rebuild
rm -rf node_modules dist
npm ci
npm run build

# Check Vite version
npm ls vite

# Validate vite.config.ts syntax
npx vite --version
```

**Common Causes and Solutions**:

| Error | Cause | Solution |
|-------|-------|----------|
| `Failed to resolve entry` | Wrong input path | Check `rollupOptions.input` |
| `'vue' is imported but not used` | External not working | Verify `external: ['vue']` |
| `Plugin 'X' not found` | Missing plugin | `npm install vite-plugin-X` |
| `Cannot read properties of undefined` | Config syntax error | Validate `vite.config.ts` |

---

### Missing Dependencies

**Symptom**: `Module not found` errors during build

**Diagnostic Steps**:

```bash
# Check if package is installed
npm ls <package-name>

# Check for peer dependency warnings
npm ls --all 2>&1 | grep -i "peer dep"

# Reinstall all dependencies
rm -rf node_modules package-lock.json
npm install
```

**Common Missing Packages**:

```bash
# Core dependencies
npm install vue@^3.5.0 vue-router@^4.5.0 pinia@^3.0.0

# single-spa
npm install single-spa-vue@^3.0.0

# Build dependencies
npm install -D vite-plugin-css-injected-by-js eventemitter3
```

---

## Runtime Issues

### App Doesn't Mount

**Symptom**: Container loads but microfrontend doesn't appear

**Diagnostic Steps**:

1. Check browser console for errors
2. Verify lifecycle exports:

```javascript
// In browser console, after container loads the module
import('/path/to/entry/main.js').then(module => {
  console.log('Exports:', Object.keys(module));
  // Should show: ['bootstrap', 'mount', 'unmount']
});
```

3. Check if mount element exists:

```javascript
// Check if container created the mount point
document.querySelector('#single-spa-application\\:@vnrm/my-microfrontend');
```

**Solutions**:

| Issue | Solution |
|-------|----------|
| Missing exports | Verify `export const { bootstrap, mount, unmount }` |
| Wrong export format | Check `preserveEntrySignatures: 'exports-only'` |
| Mount element missing | Container issue, check container logs |
| Error in bootstrap | Add try/catch, check handleInstance |

---

### Blank Screen

**Symptom**: App mounts but shows nothing

**Diagnostic Steps**:

```javascript
// Check Vue app state
const app = document.querySelector('[data-v-app]');
console.log('Vue app element:', app);

// Check for Vue errors
// Look for [Vue warn] messages in console
```

**Common Causes and Solutions**:

| Cause | Solution |
|-------|----------|
| Router not installed | Verify `app.use(router)` in handleInstance |
| No route match | Check catch-all route pattern |
| Component error | Check component for errors |
| Missing root template | Verify `app.vue` has `<router-view />` |

---

### CSS Not Applied

**Symptom**: Components render but are unstyled

**Diagnostic Steps**:

```javascript
// Check if styles are in the DOM
document.querySelectorAll('style').length;

// Check for CSS injection
// Look for <style data-vite-dev-id> elements
```

**Solutions**:

1. Verify CSS injection plugin:

```typescript
// vite.config.ts
import cssInjectedByJsPlugin from 'vite-plugin-css-injected-by-js';

export default defineConfig({
  plugins: [
    vue(),
    cssInjectedByJsPlugin(),  // Must be included
  ],
});
```

2. Check for CSS import in main.ts (standalone mode only):

```typescript
// For standalone development
import '@telekom/scale-components/dist/scale-components/scale-components.css';
```

3. Verify scoped styles work:

```vue
<style scoped>
/* Styles should have [data-v-xxxx] attribute */
</style>
```

---

### Routes Don't Work

**Symptom**: Navigation fails or wrong component renders

**Diagnostic Steps**:

```javascript
// Check current route
import { useRouter, useRoute } from 'vue-router';
const route = useRoute();
console.log('Current route:', route.path, route.name);

// Check registered routes
const router = useRouter();
console.log('Routes:', router.getRoutes().map(r => r.path));
```

**Solutions**:

| Issue | Solution |
|-------|----------|
| No catch-all route | Add `path: '/:pathMatch(.*)*'` |
| History mode mismatch | Use `createWebHistory()` |
| Wrong base path | Container handles base, don't set it |
| Guards blocking | Check `beforeEach` guards |

---

## Container Integration Issues

### Context Undefined

**Symptom**: `useContext()` throws "Context not available" error

**Diagnostic Steps**:

```typescript
// Check if createContext is called
// In main.ts handleInstance:
console.log('Installing context...');
app.use(createContext({ eventBus, idp, config }));
console.log('Context installed');
```

**Solutions**:

1. Ensure createContext is called in handleInstance:

```typescript
async handleInstance(app, props) {
  const config = await loadConfig();

  app
    .use(createPinia())
    .use(router)
    .use(createContext({  // This must be called
      eventBus: props.eventBus,
      idp: props.idp,
      config,
    }));
}
```

2. Check component lifecycle:

```typescript
// useContext must be called in setup, not in async callbacks
// WRONG:
onMounted(async () => {
  const { idp } = useContext();  // May fail
});

// CORRECT:
const { idp } = useContext();  // Called in setup
onMounted(async () => {
  console.log(idp.name);  // Works
});
```

---

### EventBus Not Working

**Symptom**: Events are emitted but not received, or vice versa

**Diagnostic Steps**:

```typescript
// Log all events
const { eventBus } = useContext();
const originalEmit = eventBus.emit.bind(eventBus);
eventBus.emit = (event, ...args) => {
  console.log('[EventBus] Emit:', event, args);
  return originalEmit(event, ...args);
};
```

**Common Issues**:

| Issue | Cause | Solution |
|-------|-------|----------|
| Event not received | Wrong event name | Check container's expected events |
| Event received late | Listener added after emit | Add listeners in onMounted |
| Memory leak | Listeners not removed | Remove in onUnmounted |
| Wrong payload | Container expects different format | Check container docs |

**Correct event handling**:

```typescript
onMounted(() => {
  eventBus.on('some-event', handleEvent);
});

onUnmounted(() => {
  eventBus.off('some-event', handleEvent);
});
```

---

### IDP Token Errors

**Symptom**: API calls fail with 401, token undefined

**Diagnostic Steps**:

```typescript
const { idp } = useContext();

// Check IDP is available
console.log('IDP:', idp);
console.log('User:', idp.name);
console.log('Roles:', idp.roles);

// Check token
const token = await idp.getAccessToken();
console.log('Token:', token?.substring(0, 20) + '...');
```

**Solutions**:

| Issue | Solution |
|-------|----------|
| Token undefined | Check container IDP configuration |
| Token expired | Call `idp.refreshToken()` before API call |
| Wrong token type | Use `getAccessToken()` for APIs, `getIdToken()` for user info |
| Roles empty | Check container role mapping |

---

### Config Not Loading

**Symptom**: `config` is undefined or has wrong values

**Diagnostic Steps**:

```typescript
// Check config loading
const configUrl = new URL('../config.json', import.meta.url);
console.log('Config URL:', configUrl.href);

fetch(configUrl)
  .then(r => r.json())
  .then(config => console.log('Config:', config))
  .catch(err => console.error('Config load failed:', err));
```

**Solutions**:

| Issue | Solution |
|-------|----------|
| 404 error | Check config.json exists in public/ |
| Wrong path | Verify URL construction |
| CORS error | Check nginx headers |
| Wrong values | Check Helm ConfigMap |

---

## Deployment Issues

### Container Won't Start

**Symptom**: Pod in CrashLoopBackOff or Error state

**Diagnostic Steps**:

```bash
# Check pod status
kubectl get pods -n vnrm-dev

# Check pod logs
kubectl logs -n vnrm-dev <pod-name>

# Check pod events
kubectl describe pod -n vnrm-dev <pod-name>
```

**Common Causes**:

| Cause | Solution |
|-------|----------|
| Port conflict | Nginx must listen on 8080, not 80 |
| Permission denied | Check user 1001 permissions |
| Missing file | Check Docker build copied files correctly |
| Config error | Check nginx config syntax |

**Test locally**:

```bash
# Build and run locally
docker build -t mfe-test .
docker run -p 8080:8080 mfe-test

# Check if it serves correctly
curl http://localhost:8080/entry/main.js
curl http://localhost:8080/health
```

---

### 404 Errors

**Symptom**: Browser shows 404 for assets or entry point

**Diagnostic Steps**:

```bash
# Check what's in the container
kubectl exec -n vnrm-dev <pod-name> -- ls -la /usr/share/nginx/html/
kubectl exec -n vnrm-dev <pod-name> -- ls -la /usr/share/nginx/html/entry/
```

**Solutions**:

| Issue | Solution |
|-------|----------|
| Entry file missing | Check `npm run build` output |
| Wrong path in container | Check Dockerfile COPY commands |
| Ingress rewrite issue | Check ingress annotations |
| Case sensitivity | Linux is case-sensitive, check paths |

---

### Health Check Fails

**Symptom**: Pod not ready, readiness probe failing

**Diagnostic Steps**:

```bash
# Check probe configuration
kubectl get pod -n vnrm-dev <pod-name> -o yaml | grep -A10 readinessProbe

# Test endpoint manually
kubectl exec -n vnrm-dev <pod-name> -- wget -qO- http://localhost:8080/health
kubectl exec -n vnrm-dev <pod-name> -- wget -qO- http://localhost:8080/entry/main.js | head
```

**Solutions**:

| Issue | Solution |
|-------|----------|
| Wrong endpoint | Check probe path matches nginx config |
| Wrong port | Should be 8080, not 80 |
| Timeout too short | Increase timeout in values.yaml |
| Initial delay too short | Increase initialDelaySeconds |

---

### ConfigMap Not Applied

**Symptom**: Running with wrong configuration values

**Diagnostic Steps**:

```bash
# Check ConfigMap content
kubectl get configmap -n vnrm-dev <release>-config -o yaml

# Check mounted config in pod
kubectl exec -n vnrm-dev <pod-name> -- cat /usr/share/nginx/html/config.json
```

**Solutions**:

| Issue | Solution |
|-------|----------|
| ConfigMap not mounted | Check volumeMounts in deployment |
| Wrong path | Check subPath matches filename |
| Old config | Restart pod after ConfigMap update |
| Template error | Check Helm template syntax |

---

## Development Mode Issues

### Standalone Mode Not Working

**Symptom**: `npm run dev` fails or shows errors

**Diagnostic Steps**:

```bash
# Check Vite can start
npx vite --version

# Check for port conflicts
lsof -i :5173

# Try different port
npm run dev -- --port 3000
```

**Solutions**:

| Issue | Solution |
|-------|----------|
| Port in use | Kill other process or use different port |
| Module not found | Check standalone/main.ts imports |
| EventEmitter error | Install `eventemitter3` |
| Scale not loading | Check index.html script paths |

---

### Hot Reload Not Working

**Symptom**: Changes don't appear without full refresh

**Diagnostic Steps**:

```bash
# Check Vite HMR connection
# Look for "connected" message in browser console

# Check for HMR errors
# Look for [vite] errors in console
```

**Solutions**:

| Issue | Solution |
|-------|----------|
| WebSocket blocked | Check firewall/proxy settings |
| File watcher limit | Increase fs.inotify.max_user_watches |
| Wrong file extension | Ensure .vue files are saved |
| Circular dependency | Check import structure |

---

## Performance Issues

### Large Bundle Size

**Diagnostic**:

```bash
# Analyze bundle
npx vite-bundle-analyzer

# Check what's included
npm run build -- --report
```

**Solutions**:

| Issue | Solution |
|-------|----------|
| Vue bundled | Add to `external` array |
| Large dependencies | Use dynamic imports |
| Unused code | Enable tree shaking |
| Sourcemaps in production | Move to separate files |

---

### Slow Initial Load

**Diagnostic**:

```javascript
// Performance timing
performance.mark('mfe-start');
// ... after mount
performance.mark('mfe-ready');
performance.measure('mfe-load', 'mfe-start', 'mfe-ready');
console.log(performance.getEntriesByName('mfe-load'));
```

**Solutions**:

| Issue | Solution |
|-------|----------|
| Large entry file | Code split with dynamic imports |
| Slow config fetch | Preload or cache config |
| Many dependencies | Review and reduce |
| Render blocking | Use async component loading |

---

## Diagnostic Commands Reference

### Build Diagnostics

```bash
# Clean rebuild
rm -rf node_modules dist && npm ci && npm run build

# Check build output
ls -la dist/entry/
cat dist/entry/main.js | head -50

# Verify exports
grep -E "export (const|function)" dist/entry/main.js
```

### Runtime Diagnostics

```javascript
// Check Vue instance
console.log('Vue version:', Vue.version);

// Check router
console.log('Current route:', router.currentRoute.value);

// Check stores
const store = useCounterStore();
console.log('Store state:', store.$state);
```

### Container Diagnostics

```bash
# Check container logs
kubectl logs -f -n vnrm-dev deployment/<deployment-name>

# Check pod resources
kubectl top pods -n vnrm-dev

# Check network
kubectl exec -n vnrm-dev <pod-name> -- wget -qO- http://localhost:8080/entry/main.js | head
```

---

## Getting Help

If these troubleshooting steps don't resolve your issue:

1. **Check container documentation** for expected props and events
2. **Review single-spa documentation** for lifecycle details
3. **Search GitLab issues** for similar problems
4. **Contact VNRM team** with:
   - Error messages (full stack trace)
   - Steps to reproduce
   - Environment details (browser, node version)
   - Relevant configuration files
