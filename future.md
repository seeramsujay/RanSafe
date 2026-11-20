# RanSafe: Architectural Review & Autonomous SRE Roadmap (future.md)

---

## 1. Architectural Code Review & Threat Landscape Analysis

RanSafe is an autonomous Site Reliability Engineering (SRE) and cybersecurity orchestrator engineered to serve as an instant circuit-breaker against ransomware propagating within cloud environments. By integrating **Google Cloud Agent Builder** and **Gemini 3** with real-time application metrics exposed through a **Dynatrace Model Context Protocol (MCP)** server, RanSafe bridges the critical detection-to-remediation latency gap.

### Current Architecture Strengths
- **Decoupled 4-Lane Engineering:** Strict schema segregation (`telemetry_schema.json` and `execution_interface.json`) allows sandbox threat simulations, telemetry ingestion, AI reasoning, and infrastructure mutation to evolve asynchronously.
- **Model Context Protocol Grounding:** Utilizes Dynatrace MCP to ground LLM reasoning directly in verifiable infrastructure metrics (CPU spikes, IOPS anomalies, rapid write bursts).
- **Proactive Circuit Breaking:** Replaces human-in-the-loop escalation with deterministic network airgapping and traffic rerouting.

### Identified Bottlenecks & Vulnerabilities
1. **Telemetry Ingestion Lag:** Polling Dynatrace metrics over MCP introduces a 5–15 second lag window, during which aggressive ransomware can encrypt thousands of local database or block volume files.
2. **Userspace vs Kernel Interception:** Shell-based network cutoffs (`iptables` / interface drops) do not halt active file encryption already underway in memory.
3. **Rollback Integrity Verification:** Provisioning a clean replica cluster requires mathematically verifying that backup snapshots predate payload staging and lateral persistence.

---

## 2. Strategic Engineering Roadmap

```mermaid
flowchart TD
    subgraph Phase 1: Sub-Second Kernel Telemetry
        P1A[eBPF Kernel Sensor: sys_enter_write] --> P1B[Shannon Entropy Stream Calculation]
        P1B --> P1C[Local RingBuffer Emergency Breaker]
    end

    subgraph Phase 2: Distributed Cloud Mesh Airgap
        P2A[K8s NetworkPolicy Quarantine] --> P2B[Istio mTLS Certificate Revocation]
        P2B --> P2C[AWS / GCP Subnet VPC Isolation]
    end

    subgraph Phase 3: Immutable Instant Recovery
        P3A[Copy-On-Write ZFS / EBS Micro-Snapshots] --> P3B[Automated Clean Replica Spin-up]
        P3B --> P3C[Proxy Traffic Diverter & Canary Health Check]
    end

    subgraph Phase 4: Autonomous SRE Chaos Drills
        P4A[Automated Ransomware Chaos Engineering] --> P4B[Gemini Post-Mortem Generation]
        P4B --> P4C[Continuous Airgap Policy Optimization]
    end

    Phase 1 --> Phase 2
    Phase 2 --> Phase 3
    Phase 3 --> Phase 4
```

---

## 3. Detailed Milestone Execution Plan

### Milestone 1: Sub-Second eBPF Kernel Probes & Entropy Detection
- [ ] **Kernel-Level I/O Monitoring:** Implement an eBPF tracepoint program on `vfs_write` and `sys_enter_renameat2` to track file modification frequencies at the operating system level.
- [ ] **Real-time Shannon Entropy Calculation:** Compute streaming entropy on modified data blocks. A sudden transition from plaintext ($\approx 3.5 - 5.0$) to high entropy ($\approx 7.95 - 8.0$) triggers immediate containment prior to centralized cloud polling.
- [ ] **Autonomous Freeze Daemon (`ransafe-freeze`):** Execute instantaneous `SIGSTOP` on suspicious process trees before network or disk serialization finishes.

### Milestone 2: Multi-Cloud Mesh Isolation & Microsegmentation
- [ ] **Kubernetes Dynamic NetworkPolicy:** Autonomously generate and apply strict default-deny ingress/egress policies to infected pods.
- [ ] **Service Mesh Token Revocation:** Invalidate Istio / Envoy SPIFFE/SPIRE cryptographic identities to eliminate lateral east-west traversal.
- [ ] **Cloud VPC Route Blackholing:** Integrate with GCP Cloud Router / AWS VPC Route Tables to detach infected subnet interfaces within $<200\text{ms}$.

### Milestone 3: Immutable Snapshotting & Zero-Downtime Traffic Rerouting
- [ ] **Continuous Atomic Snapshots:** Maintain high-frequency local CoW (Copy-On-Write) snapshots on persistent volumes.
- [ ] **Automated Replica Validation:** Verify pre-infection hash states and launch clean uncompromised container replicas in parallel subnets.
- [ ] **Envoy Gateway Traffic Diverter:** Shift production ingress traffic seamlessly away from quarantined nodes to newly restored replicas with zero dropped HTTP connections.

### Milestone 4: SRE Self-Healing Drills & Gemini 3 Post-Mortem Synthesis
- [ ] **Chaos Ransomware Simulator:** Automated purple-team chaos tests injecting pseudo-ransomware payloads to benchmark MTTR (Mean Time To Recovery).
- [ ] **Automated Incident Root-Cause Reports:** Ground Gemini 3 in Dynatrace distributed traces to output comprehensive post-mortem Markdown documents detailing the initial ingress vector, blast radius, and recovery timeline.
