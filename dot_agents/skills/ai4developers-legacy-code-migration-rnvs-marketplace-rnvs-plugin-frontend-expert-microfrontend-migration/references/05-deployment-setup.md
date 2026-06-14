# Deployment Setup

This document provides complete deployment configuration for a VNRM microfrontend including Docker, Nginx, Helm charts, and CI/CD pipeline.

---

## Overview

The deployment stack consists of:

1. **Multi-stage Docker build** - Builds the app and creates a minimal Nginx image
2. **Nginx** - Serves static files with security headers
3. **Helm charts** - Kubernetes deployment with ConfigMaps
4. **GitLab CI/CD** - Automated build and deployment pipeline

---

## Directory Structure

```
├── Dockerfile
├── .dockerignore
├── nginx/
│   ├── default.conf
│   └── security.conf
├── helm/
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
│       ├── deployment.yaml
│       ├── service.yaml
│       ├── ingress.yaml
│       ├── configmap.yaml
│       └── _helpers.tpl
└── .gitlab-ci.yml
```

---

## Docker Configuration

### Dockerfile

```dockerfile
# =============================================================================
# Stage 1: Build
# =============================================================================
FROM node:22-alpine AS build

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --ignore-scripts

# Copy source code
COPY . .

# Build the application
RUN npm run build

# =============================================================================
# Stage 2: Production
# =============================================================================
FROM nginx:1.27-alpine AS production

# Add non-root user
RUN adduser -D -u 1001 appuser

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy nginx configuration
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY nginx/security.conf /etc/nginx/conf.d/security.conf

# Copy built application
COPY --from=build /app/dist /usr/share/nginx/html

# Create cache directories with proper permissions
RUN mkdir -p /var/cache/nginx /var/run \
    && chown -R appuser:appuser /var/cache/nginx /var/run /usr/share/nginx/html

# Use non-root user
USER 1001

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/entry/main.js || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

### .dockerignore

```
node_modules/
dist/
coverage/
test-results/
*.log
.git/
.gitignore
.env*
*.md
!README.md
.vscode/
.idea/
```

---

## Nginx Configuration

### nginx/default.conf

```nginx
server {
    listen 8080;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_types
        text/plain
        text/css
        text/javascript
        application/javascript
        application/json
        application/xml
        image/svg+xml;

    # Cache control for entry point (no cache - allows updates)
    location /entry/ {
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Pragma "no-cache";
        add_header Expires "0";
        try_files $uri =404;
    }

    # Cache control for hashed assets (long-term cache)
    location /assets/ {
        add_header Cache-Control "public, max-age=31536000, immutable";
        try_files $uri =404;
    }

    # Cache control for chunks (long-term cache)
    location /chunks/ {
        add_header Cache-Control "public, max-age=31536000, immutable";
        try_files $uri =404;
    }

    # Config file (short cache, allows updates)
    location /config.json {
        add_header Cache-Control "no-cache";
        try_files $uri =404;
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "OK";
        add_header Content-Type text/plain;
    }

    # Deny access to hidden files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
}
```

### nginx/security.conf

```nginx
# =============================================================================
# Security Headers
# =============================================================================

# HSTS - Force HTTPS (15768000 seconds = 6 months)
add_header Strict-Transport-Security "max-age=15768000; includeSubDomains" always;

# Prevent MIME type sniffing
add_header X-Content-Type-Options "nosniff" always;

# XSS Protection (legacy browsers)
add_header X-XSS-Protection "1; mode=block" always;

# Referrer Policy
add_header Referrer-Policy "strict-origin-when-cross-origin" always;

# Content Security Policy
# Note: Adjust based on your microfrontend's needs
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https://api.vnrm.telekom.de wss:; frame-ancestors 'self' https://*.telekom.de;" always;

# Permissions Policy
add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;

# Note: X-Frame-Options intentionally omitted to allow embedding in container
# The container handles frame security

# =============================================================================
# Rate Limiting (optional - adjust based on needs)
# =============================================================================

# Limit connections per IP
limit_conn_zone $binary_remote_addr zone=conn_limit:10m;
limit_conn conn_limit 50;

# Limit request rate per IP
limit_req_zone $binary_remote_addr zone=req_limit:10m rate=10r/s;
limit_req zone=req_limit burst=20 nodelay;

# =============================================================================
# Disable unnecessary features
# =============================================================================

# Disable server tokens (hide nginx version)
server_tokens off;

# Disable autoindex
autoindex off;
```

---

## Helm Charts

### helm/Chart.yaml

```yaml
apiVersion: v2
name: vnrm-microfrontend
description: VNRM Microfrontend Helm Chart
type: application
version: 1.0.0
appVersion: "1.0.0"
maintainers:
  - name: VNRM Team
    email: vnrm-team@telekom.de
```

### helm/values.yaml

```yaml
# =============================================================================
# Application Configuration
# =============================================================================

replicaCount: 2

image:
  repository: registry.telekom.de/vnrm/my-microfrontend
  pullPolicy: IfNotPresent
  tag: ""  # Overridden by CI/CD

imagePullSecrets:
  - name: registry-credentials

nameOverride: ""
fullnameOverride: ""

# =============================================================================
# Service Account
# =============================================================================

serviceAccount:
  create: true
  annotations: {}
  name: ""

# =============================================================================
# Pod Configuration
# =============================================================================

podAnnotations: {}

podSecurityContext:
  runAsNonRoot: true
  runAsUser: 1001
  runAsGroup: 1001
  fsGroup: 1001

securityContext:
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  runAsNonRoot: true
  runAsUser: 1001
  capabilities:
    drop:
      - ALL

# =============================================================================
# Service Configuration
# =============================================================================

service:
  type: ClusterIP
  port: 80
  targetPort: 8080

# =============================================================================
# Ingress Configuration
# =============================================================================

ingress:
  enabled: true
  className: nginx
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /$2
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
  hosts:
    - host: vnrm.telekom.de
      paths:
        - path: /my-microfrontend(/|$)(.*)
          pathType: Prefix
  tls:
    - secretName: vnrm-tls
      hosts:
        - vnrm.telekom.de

# =============================================================================
# Resource Limits
# =============================================================================

resources:
  limits:
    cpu: 100m
    memory: 128Mi
  requests:
    cpu: 50m
    memory: 64Mi

# =============================================================================
# Probes
# =============================================================================

livenessProbe:
  httpGet:
    path: /health
    port: http
  initialDelaySeconds: 10
  periodSeconds: 10
  timeoutSeconds: 3
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /entry/main.js
    port: http
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3

# =============================================================================
# Autoscaling
# =============================================================================

autoscaling:
  enabled: false
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80

# =============================================================================
# Node Scheduling
# =============================================================================

nodeSelector: {}
tolerations: []
affinity: {}

# =============================================================================
# Runtime Configuration
# =============================================================================

config:
  apiBaseUrl: "https://api.vnrm.telekom.de"
  featureFlags:
    darkMode: true
    experimentalFeatures: false
```

### helm/templates/_helpers.tpl

```yaml
{{/*
Expand the name of the chart.
*/}}
{{- define "vnrm-microfrontend.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "vnrm-microfrontend.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "vnrm-microfrontend.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "vnrm-microfrontend.labels" -}}
helm.sh/chart: {{ include "vnrm-microfrontend.chart" . }}
{{ include "vnrm-microfrontend.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "vnrm-microfrontend.selectorLabels" -}}
app.kubernetes.io/name: {{ include "vnrm-microfrontend.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "vnrm-microfrontend.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "vnrm-microfrontend.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}
```

### helm/templates/deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "vnrm-microfrontend.fullname" . }}
  labels:
    {{- include "vnrm-microfrontend.labels" . | nindent 4 }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "vnrm-microfrontend.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      annotations:
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
        {{- with .Values.podAnnotations }}
        {{- toYaml . | nindent 8 }}
        {{- end }}
      labels:
        {{- include "vnrm-microfrontend.selectorLabels" . | nindent 8 }}
    spec:
      {{- with .Values.imagePullSecrets }}
      imagePullSecrets:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      serviceAccountName: {{ include "vnrm-microfrontend.serviceAccountName" . }}
      securityContext:
        {{- toYaml .Values.podSecurityContext | nindent 8 }}
      containers:
        - name: {{ .Chart.Name }}
          securityContext:
            {{- toYaml .Values.securityContext | nindent 12 }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: 8080
              protocol: TCP
          livenessProbe:
            {{- toYaml .Values.livenessProbe | nindent 12 }}
          readinessProbe:
            {{- toYaml .Values.readinessProbe | nindent 12 }}
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
          volumeMounts:
            - name: config
              mountPath: /usr/share/nginx/html/config.json
              subPath: config.json
              readOnly: true
            - name: cache
              mountPath: /var/cache/nginx
            - name: run
              mountPath: /var/run
      volumes:
        - name: config
          configMap:
            name: {{ include "vnrm-microfrontend.fullname" . }}-config
        - name: cache
          emptyDir: {}
        - name: run
          emptyDir: {}
      {{- with .Values.nodeSelector }}
      nodeSelector:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.affinity }}
      affinity:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.tolerations }}
      tolerations:
        {{- toYaml . | nindent 8 }}
      {{- end }}
```

### helm/templates/service.yaml

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ include "vnrm-microfrontend.fullname" . }}
  labels:
    {{- include "vnrm-microfrontend.labels" . | nindent 4 }}
spec:
  type: {{ .Values.service.type }}
  ports:
    - port: {{ .Values.service.port }}
      targetPort: {{ .Values.service.targetPort }}
      protocol: TCP
      name: http
  selector:
    {{- include "vnrm-microfrontend.selectorLabels" . | nindent 4 }}
```

### helm/templates/ingress.yaml

```yaml
{{- if .Values.ingress.enabled -}}
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ include "vnrm-microfrontend.fullname" . }}
  labels:
    {{- include "vnrm-microfrontend.labels" . | nindent 4 }}
  {{- with .Values.ingress.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
spec:
  {{- if .Values.ingress.className }}
  ingressClassName: {{ .Values.ingress.className }}
  {{- end }}
  {{- if .Values.ingress.tls }}
  tls:
    {{- range .Values.ingress.tls }}
    - hosts:
        {{- range .hosts }}
        - {{ . | quote }}
        {{- end }}
      secretName: {{ .secretName }}
    {{- end }}
  {{- end }}
  rules:
    {{- range .Values.ingress.hosts }}
    - host: {{ .host | quote }}
      http:
        paths:
          {{- range .paths }}
          - path: {{ .path }}
            pathType: {{ .pathType }}
            backend:
              service:
                name: {{ include "vnrm-microfrontend.fullname" $ }}
                port:
                  number: {{ $.Values.service.port }}
          {{- end }}
    {{- end }}
{{- end }}
```

### helm/templates/configmap.yaml

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "vnrm-microfrontend.fullname" . }}-config
  labels:
    {{- include "vnrm-microfrontend.labels" . | nindent 4 }}
data:
  config.json: |
    {
      "apiBaseUrl": {{ .Values.config.apiBaseUrl | quote }},
      "featureFlags": {{ .Values.config.featureFlags | toJson }}
    }
```

---

## GitLab CI/CD Pipeline

### .gitlab-ci.yml

```yaml
# =============================================================================
# VNRM Microfrontend CI/CD Pipeline
# =============================================================================

include:
  - project: 'vnrm/ci-templates'
    ref: main
    file: '/templates/vite.caas.gitlab-ci.yml'

variables:
  DOCKER_REGISTRY: registry.telekom.de
  IMAGE_NAME: vnrm/my-microfrontend
  HELM_CHART_PATH: ./helm

stages:
  - validate
  - test
  - build
  - deploy

# =============================================================================
# Validate Stage
# =============================================================================

lint:
  stage: validate
  image: node:22-alpine
  script:
    - npm ci
    - npm run lint
  rules:
    - if: $CI_MERGE_REQUEST_IID
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

type-check:
  stage: validate
  image: node:22-alpine
  script:
    - npm ci
    - npm run type-check
  rules:
    - if: $CI_MERGE_REQUEST_IID
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

# =============================================================================
# Test Stage
# =============================================================================

unit-tests:
  stage: test
  image: node:22-alpine
  script:
    - npm ci
    - npm run test:coverage
  artifacts:
    reports:
      junit: test-results/junit.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml
    paths:
      - coverage/
    expire_in: 1 week
  coverage: '/All files[^|]*\|[^|]*\s+([\d\.]+)/'
  rules:
    - if: $CI_MERGE_REQUEST_IID
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

# =============================================================================
# Build Stage
# =============================================================================

build-image:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  variables:
    DOCKER_TLS_CERTDIR: "/certs"
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $DOCKER_REGISTRY
  script:
    - |
      if [ -n "$CI_COMMIT_TAG" ]; then
        IMAGE_TAG=$CI_COMMIT_TAG
      else
        IMAGE_TAG=$CI_COMMIT_SHORT_SHA
      fi
    - docker build -t $DOCKER_REGISTRY/$IMAGE_NAME:$IMAGE_TAG .
    - docker push $DOCKER_REGISTRY/$IMAGE_NAME:$IMAGE_TAG
    - |
      if [ "$CI_COMMIT_BRANCH" == "$CI_DEFAULT_BRANCH" ]; then
        docker tag $DOCKER_REGISTRY/$IMAGE_NAME:$IMAGE_TAG $DOCKER_REGISTRY/$IMAGE_NAME:latest
        docker push $DOCKER_REGISTRY/$IMAGE_NAME:latest
      fi
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
    - if: $CI_COMMIT_TAG

# =============================================================================
# Deploy Stage
# =============================================================================

deploy-dev:
  stage: deploy
  image: alpine/helm:3.14
  script:
    - |
      if [ -n "$CI_COMMIT_TAG" ]; then
        IMAGE_TAG=$CI_COMMIT_TAG
      else
        IMAGE_TAG=$CI_COMMIT_SHORT_SHA
      fi
    - helm upgrade --install my-microfrontend $HELM_CHART_PATH
        --namespace vnrm-dev
        --set image.tag=$IMAGE_TAG
        --set config.apiBaseUrl=https://api-dev.vnrm.telekom.de
        --values $HELM_CHART_PATH/values-dev.yaml
        --wait
        --timeout 5m
  environment:
    name: development
    url: https://dev.vnrm.telekom.de/my-microfrontend
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

deploy-prod:
  stage: deploy
  image: alpine/helm:3.14
  script:
    - helm upgrade --install my-microfrontend $HELM_CHART_PATH
        --namespace vnrm-prod
        --set image.tag=$CI_COMMIT_TAG
        --set config.apiBaseUrl=https://api.vnrm.telekom.de
        --values $HELM_CHART_PATH/values-prod.yaml
        --wait
        --timeout 5m
  environment:
    name: production
    url: https://vnrm.telekom.de/my-microfrontend
  rules:
    - if: $CI_COMMIT_TAG
  when: manual
```

---

## Environment-Specific Values

### helm/values-dev.yaml

```yaml
replicaCount: 1

resources:
  limits:
    cpu: 100m
    memory: 128Mi
  requests:
    cpu: 25m
    memory: 64Mi

config:
  apiBaseUrl: "https://api-dev.vnrm.telekom.de"
  featureFlags:
    darkMode: true
    experimentalFeatures: true
```

### helm/values-prod.yaml

```yaml
replicaCount: 3

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70

resources:
  limits:
    cpu: 200m
    memory: 256Mi
  requests:
    cpu: 100m
    memory: 128Mi

config:
  apiBaseUrl: "https://api.vnrm.telekom.de"
  featureFlags:
    darkMode: true
    experimentalFeatures: false
```

---

## Validation Checklist

### Docker

- [ ] Multi-stage build reduces image size
- [ ] Non-root user (UID 1001)
- [ ] Health check configured
- [ ] .dockerignore excludes unnecessary files

### Nginx

- [ ] Listens on port 8080 (non-privileged)
- [ ] Security headers configured
- [ ] Cache headers set correctly
- [ ] Health endpoint available

### Helm

- [ ] Read-only root filesystem
- [ ] No privilege escalation
- [ ] Resource limits defined
- [ ] Liveness and readiness probes
- [ ] ConfigMap for runtime config

### CI/CD

- [ ] Lint and type-check in validate stage
- [ ] Tests with coverage reporting
- [ ] Docker build and push
- [ ] Helm deployment with environment-specific values

---

## Next Steps

After completing deployment setup:

1. **Phase 6**: Troubleshooting - See `06-troubleshooting.md`
