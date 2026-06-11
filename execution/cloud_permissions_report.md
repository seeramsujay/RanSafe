# RanSafe Cloud Permissions & Production Deployment Report
**Infrastructure Execution & Security Ops Guide**

This report outlines the Google Cloud Platform (GCP) IAM policies, API permissions, and Google Kubernetes Engine (GKE) RBAC rules required to run the RanSafe SRE Containment Engine in a production environment. 

---

## 1. Google Cloud IAM Permissions

To run state-mutating API operations, the RanSafe runner (or its Google Cloud Service Account) requires the following project-level IAM roles and specific permissions:

### A. Secret Manager Access
RanSafe retrieves the identity verification tokens and third-party API credentials dynamically from GCP Secret Manager.
* **Secret ID:** `ransafe-auth-key`
* **Required IAM Role:** `roles/secretmanager.secretAccessor` (Secret Manager Secret Accessor)
* **Underlying Permissions:**
  * `secretmanager.versions.access`
  * `secretmanager.versions.get`

### B. VPC Firewall rules Mutation
RanSafe deploys and tears down emergency ingress/egress firewall blocks targeting infected compute nodes.
* **Required IAM Role:** `roles/compute.securityAdmin` (Compute Security Admin)
* **Underlying Permissions:**
  * `compute.firewalls.create`
  * `compute.firewalls.delete`
  * `compute.firewalls.get`
  * `compute.firewalls.list`

### C. Cloud Armor Policy Mutation
RanSafe modifies security policies in real-time to drop HTTP/HTTPS request headers targeting infected edge nodes.
* **Required IAM Role:** `roles/compute.securityAdmin` (Compute Security Admin)
* **Underlying Permissions:**
  * `compute.securityPolicies.get`
  * `compute.securityPolicies.update`
  * `compute.securityPolicies.use`

### D. IAM Role Revocation (Lateral Movement Prevention)
RanSafe removes project-level permissions (e.g. `roles/editor`) from compromised service accounts associated with breached nodes.
* **Required IAM Role:** `roles/resourcemanager.projectIamAdmin` (Project IAM Admin)
* **Underlying Permissions:**
  * `resourcemanager.projects.getIamPolicy`
  * `resourcemanager.projects.setIamPolicy`

---

## 2. Kubernetes RBAC Configuration (GKE)

RanSafe requires container-level lifecycle management capabilities in GKE to evict compromised pods and trigger rollout restarts of clean backup workloads.

The following RBAC `Role` and `RoleBinding` should be applied in the GKE `production` namespace to authenticate the RanSafe service account:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: ransafe-workload-containment
  namespace: production
rules:
  # Pod eviction permission (kubectl delete pod)
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "list", "delete"]
  # Rollout deployment restart (kubectl rollout restart)
  - apiGroups: ["apps"]
    resources: ["deployments", "deployments/rollback"]
    verbs: ["get", "list", "update", "patch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: ransafe-workload-containment-binding
  namespace: production
subjects:
  - kind: ServiceAccount
    name: ransafe-agent-sa
    namespace: production
roleRef:
  kind: Role
  name: ransafe-workload-containment
  apiGroup: rbac.authorization.k8s.io
```

---

## 3. Production Deployment & Workload Identity

For maximum security compliance and to protect local MB/GB quota pools, **do not export static JSON service account keys**. Instead, leverage **Workload Identity Federation** in Google Cloud:

1. **Enable Workload Identity on GKE:**
   ```bash
   gcloud container clusters update <cluster-name> \
       --workload-pool=<project-id>.svc.id.goog
   ```

2. **Create the GCP Service Account:**
   ```bash
   gcloud iam service-accounts create ransafe-agent-sa \
       --description="SRE Containment Orchestrator Service Account" \
       --display-name="ransafe-agent-sa"
   ```

3. **Bind the GCP Service Account to the Kubernetes Service Account:**
   ```bash
   gcloud iam service-accounts add-iam-policy-binding ransafe-agent-sa@<project-id>.iam.gserviceaccount.com \
       --role="roles/iam.workloadIdentityUser" \
       --member="serviceAccount:<project-id>.svc.id.goog[production/ransafe-agent-sa]"
   ```

4. **Annotate the Kubernetes Service Account:**
   ```yaml
   apiVersion: v1
   kind: ServiceAccount
   metadata:
     name: ransafe-agent-sa
     namespace: production
     annotations:
       iam.gke.io/gcp-service-account: ransafe-agent-sa@<project-id>.iam.gserviceaccount.com
   ```
