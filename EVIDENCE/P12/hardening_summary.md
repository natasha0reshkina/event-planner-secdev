# P12 Hardening summary (before/after)

## Dockerfile
**Before:**
- build stage upgraded pip without pinning (Hadolint DL3013)
- no explicit least-privilege notes

**After:**
- install dependencies only from pinned `requirements.txt` (no unpinned `pip install --upgrade`)
- runtime runs as non-root (`USER app`) with owned workdir
- multi-stage build keeps runtime image smaller (no build cache in final)

## Kubernetes (k8s/...)
**Before:**
- resources implicitly used `default` namespace
- no NetworkPolicy for the pod

**After:**
- dedicated namespace `simple-blog` (no default)
- `automountServiceAccountToken: false`
- pod `seccompProfile: RuntimeDefault`
- container security: `allowPrivilegeEscalation: false`, `readOnlyRootFilesystem: true`, drop all caps
- NetworkPolicy restricts ingress to app port within namespace
- app config is passed via env (`PORT`)
