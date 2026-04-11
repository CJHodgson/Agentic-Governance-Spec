# Agentic-Governance-Spec
Vendor-neutral open specification for governing AI agents across heterogeneous enterprise estates. Defines five architectural layers for DUAA and EU AI Act compliance — including reversibility scoring, purpose compatibility assessment, and immutable audit trails.
# Agentic Governance Layer — Open Specification

**A vendor-neutral governance architecture for AI agent systems operating under the UK Data (Use and Access) Act 2025, UK GDPR, and EU AI Act.**

Status: Open specification — v0.1 draft, April 2026
Maintainer: LGT.io
Contributions: Welcome — see CONTRIBUTING.md
Licence: Apache 2.0

---

## Why this exists

Enterprises deploying AI agents in the UK and EU face a specific and underappreciated problem.

The regulatory frameworks that govern data use and AI systems — the UK Data (Use and Access) Act 2025 (DUAA), UK GDPR, and the EU AI Act (full enforcement from August 2026) — were designed with deterministic software in mind. A system with a fixed purpose, a defined input, a predictable output. Compliance was a matter of documenting what the system did and why.

Agentic AI systems break this model fundamentally. An agent does not have a fixed purpose. It reasons across available data, selects actions from a dynamic action space, and produces outcomes that depend on the state of the systems it touches and the decisions of other agents operating in parallel. In a multi-agent environment, purpose evolves non-linearly. Data collected for Purpose A is reused in the course of completing a task that serves Purpose B — not through a deliberate design decision but as an emergent property of the agent's reasoning.

The DUAA's shift from "prove you are permitted" to "acceptable unless proven harmful" sounds like it creates headroom. In practice, for agentic systems, it creates silent compounding liability. The moment an agent chain produces a harmful outcome, the organisation must demonstrate retroactively that every data reuse across every agent hop was compatible with the original collection purpose. In most current deployments, that demonstration is impossible.

The EU AI Act makes the problem acute. From August 2026, high-risk AI systems must have automated audit trails, documented governance processes, and incident reporting capabilities. Penalties reach 3% of global annual revenue. The Act does not define what governance looks like for agentic systems. It defines the outcome that governance must achieve: demonstrable human oversight, traceable decision rationale, and the ability to intervene.

Every major platform vendor — ServiceNow, Salesforce, AWS, Microsoft, Oracle, IBM — has built governance tooling that addresses this from within their own platform boundaries. None provides a vendor-neutral layer that operates across heterogeneous legacy estates, scores action reversibility before execution, or maintains the cross-era system contract awareness that heterogeneous deployments require.

This specification defines that layer.

---

## The core insight

The governance gap in agentic AI is not a detection problem. It is an authorisation problem.

Current approaches ask: *do I trust this agent?* They answer with identity controls, permission policies, and audit logs. This is necessary but insufficient. In a system where agent reasoning is non-deterministic and agent actions cross multiple systems with different consistency contracts, trusting the agent is not a meaningful guarantee of outcome quality.

The right question is: *do I trust this outcome, given the evidence?*

This shift — from agent trust to evidence trust — is the foundational principle of this specification. It was articulated clearly by practitioners building autonomous security agents in production, and it maps directly onto what the DUAA and EU AI Act require: not that you trust your agents, but that you can demonstrate, for any given action, the evidence that authorised it, the purpose it served, and the mechanism by which it could be reversed or remediated if wrong.

The governance layer this specification defines is the infrastructure that makes that demonstration possible — in real time, not retrospectively.

---

## The five-layer architecture

The complete governance architecture for agentic systems comprises five components. Each has been validated independently by practitioners and researchers. This specification defines the interfaces between them.

### Layer 1 — Data substrate

**What it does:** Provides every agent and every governance component with continuously updated, governed, lineage-tracked data across the full enterprise estate — including legacy systems.

**Why it matters for compliance:** DUAA purpose limitation requires that data reuse be assessed against the original collection purpose. That assessment requires knowing where data came from, how it was transformed, and what it means in context. Without a governed data substrate with full lineage, purpose compatibility assessment is guesswork.

**Interface this layer must expose:**
- Data lineage API: for any data item, return its origin system, collection purpose, transformation history, and current governance status
- Streaming event feed: real-time notification when data relevant to active agent workflows changes
- Cross-system identity resolution: canonical identifier for entities that appear under different identifiers in different systems

**Prior art:** IBM watsonx.data + Confluent (March 2026) represents the current state of the art for this layer at enterprise scale.

---

### Layer 2 — Decision context

**What it does:** Maintains a persistent, versioned, auditable record of every decision made by every agent — including the context in which the decision was made, the rationale applied, the evidence considered, the action taken, and the outcome observed.

**Why it matters for compliance:** This layer is simultaneously the technical governance mechanism and the legal compliance record. The DUAA accountability principle requires that organisations demonstrate how personal data was used and why. The EU AI Act requires automated audit trails for high-risk systems. The decision context layer satisfies both — provided it is structured, queryable, and maintained independently of any individual LLM session.

**Architectural principle:** The graph persists client-side. The LLM is a stateless computation service invoked against it. Sessions are disposable. The graph is the durable artifact. This has critical implications for auditability: the same graph can be subjected to multiple verification passes with different validators. The graph can be inspected, versioned, and audited independent of any LLM session.

**Interface this layer must expose:**
- Decision trace write API: structured record of context, rationale, evidence, action, outcome
- Precedent query API: given a proposed action, retrieve analogous past decisions and their outcomes
- Purpose compatibility log: record of purpose compatibility assessments and their conclusions
- Audit export API: tamper-evident export of decision traces for regulatory inspection

**Prior art:** Ajit Jaokar's Enterprise Context Graph framework (Oxford, March 2026) provides the theoretical foundation for this layer. Corewood TETRA provides a high-performance graph database implementation suited to the latency requirements of real-time agent governance.

---

### Layer 3 — Governance primitive (validator mesh)

**What it does:** Intercepts proposed agent actions before execution, validates them against the decision context and data substrate, scores their reversibility, assesses their purpose compatibility, and authorises or blocks execution based on configurable confidence thresholds.

**Why it matters for compliance:** This is the layer that makes the DUAA compatible reuse assessment operational rather than documentary. Rather than assessing purpose compatibility after the fact, the validator mesh performs the assessment before the action executes — creating a real-time compliance gate rather than a retrospective justification process.

**Key principles:**
- Validation is asynchronous and probabilistic, not synchronous and unanimous. A validator mesh is not a two-phase commit. It accumulates evidence continuously and makes confidence-weighted decisions. Synchronous unanimous agreement fails at agent scale for the same reasons XA transactions fail.
- Confidence threshold scales with reversibility. Low-reversibility actions (writes to systems of record, external communications, financial transactions) require higher confidence thresholds before execution. High-reversibility actions (read queries, draft generation, analysis) can proceed at lower thresholds.
- The mesh governs outcomes, not agents. Any individual validator may be wrong. The mesh is designed to reach reliable conclusions despite unreliable components — the same principle as Byzantine fault tolerant consensus.

**Interface this layer must expose:**
- Action proposal API: receive a proposed action with its context and evidence
- Reversibility score: classification of the proposed action by reversibility class (read-only / idempotent / one-way / destructive)
- Purpose compatibility assessment: evaluation of whether the action is compatible with the data collection purpose under DUAA
- Authorisation decision: proceed / escalate / block, with reasoning recorded to the decision context layer
- Circuit breaker: emergency halt mechanism for correlated anomalies across multiple agents

**Prior art:** XBow's validator-gated execution primitive (2026) provides the conceptual foundation. AWS AgentCore Policy (Cedar engine) provides a partial implementation for AWS-native environments.

---

### Layer 4 — System contract registry

**What it does:** Maintains a machine-readable record of the consistency contracts, failure modes, and rollback capabilities of every system in the enterprise estate — enabling the governance layer to broker safely across system boundaries.

**Why it matters for compliance:** This layer addresses the era-boundary problem that no current vendor solves. An agent calling a 1990s ERP and a 2015 SaaS API in the same workflow is crossing systems with fundamentally different consistency models. The ERP assumes ACID transactions; the SaaS API assumes eventual consistency. Without knowing these contracts, the governance layer cannot determine whether an action that succeeds at the API level has actually completed, failed silently, or entered an indeterminate state.

**Interface this layer must expose:**
- System contract record: for each connected system, its consistency model (ACID / eventual / async), typical failure modes, rollback capability (full / partial / none), and latency profile
- Era classification: which computing era the system originates from and what implicit assumptions that entails
- Boundary protocol: when an agent action crosses from one consistency model to another, the synchronisation checkpoint required before proceeding

---

### Layer 5 — Immutable audit trail

**What it does:** Provides a tamper-evident, append-only record of all governance decisions, validation outcomes, and agent actions — independently verifiable without relying on the systems that produced the records.

**Why it matters for compliance:** The EU AI Act requires that audit trails be maintained in a form that cannot be retrospectively modified. The DUAA accountability principle requires that organisations be able to demonstrate how personal data was used. These requirements are only meaningful if the audit trail is genuinely tamper-evident — not just logged in a database that the organisation controls.

**Design principle:** Cryptographic audit trails — the pattern demonstrated by the blockchain community through Merkle tree structures — provide tamper-evidence without requiring a distributed ledger. A hash chain of decision records, where each record includes the hash of the previous record, makes retrospective modification detectable. This is architecturally lighter than full blockchain deployment and compatible with enterprise latency requirements.

**Interface this layer must expose:**
- Append-only write: decision records written with cryptographic chaining
- Verification API: confirm that a given record has not been modified since creation
- Regulatory export: structured export of audit records in formats compatible with ICO and EU AI Act inspection requirements

---

## DUAA compliance mapping

The following table maps the DUAA's key requirements for data reuse to the governance layer components that satisfy them.

| DUAA requirement | Governance layer component |
|---|---|
| Purpose limitation — original purpose must be documented | Layer 2 decision context: collection purpose recorded at data ingestion |
| Compatible reuse assessment — new purpose must be assessed for compatibility | Layer 3 validator mesh: purpose compatibility gate before action execution |
| Accountability — demonstrate how personal data was used | Layer 2 decision context + Layer 5 audit trail |
| Legitimate interests balancing test | Layer 3 validator mesh: configurable threshold for legitimate interest actions |
| Recognised legitimate interest conditions | Layer 4 system contract registry: pre-classified system types against recognised conditions |
| Data subject rights — demonstrate what data was used and why | Layer 5 audit trail: queryable record of data use per decision |

---

## EU AI Act compliance mapping

| EU AI Act requirement | Governance layer component |
|---|---|
| Human oversight for high-risk systems | Layer 3 validator mesh: escalation path for low-confidence decisions |
| Automated audit trail | Layer 5 immutable audit trail |
| Documented governance process | Layer 3 + Layer 4: machine-readable governance decisions and system contracts |
| Incident reporting capability | Layer 5: exportable incident records with full decision context |
| Risk management system | Layer 3 reversibility classifier + Layer 4 system contract registry |
| Transparency to users | Layer 2 decision context: rationale available for inspection |

---

## What this specification is not

This specification does not define a specific implementation. It defines the interfaces that compliant implementations must expose and the properties they must guarantee.

It does not require any specific vendor, cloud provider, or model. It is designed to be implemented on top of whatever data infrastructure, graph database, LLM, and execution environment an organisation already uses.

It does not claim to solve every governance problem in agentic AI. It addresses the specific gap between what current vendor governance tooling provides and what the DUAA and EU AI Act require for organisations deploying agents across heterogeneous legacy estates.

---

## Current status and roadmap

**v0.1 (April 2026) — Interface specification**
This document. Defines the five layers and their required interfaces. Does not specify implementation.

**v0.2 (target: June 2026) — Reference implementation**
A minimal working implementation of all five layers against a defined test environment, using Corewood TETRA as the decision context graph and a configurable validator mesh.

**v0.3 (target: July 2026) — DUAA compliance toolkit**
Tooling for purpose compatibility assessment and legitimate interests balancing, aligned with ICO guidance published under the DUAA.

**v1.0 (target: August 2026) — EU AI Act readiness**
Full compliance mapping and audit export capability aligned with EU AI Act enforcement requirements.

---

## Contributing

This specification is maintained by LGT.io and welcomes contributions from practitioners, researchers, and organisations working on agentic governance.

Contributions are particularly welcome in the following areas:

- Implementation experience against specific legacy system types
- Legal review of the DUAA and EU AI Act compliance mappings
- Reference implementations of individual layers
- Test cases and validation scenarios

See CONTRIBUTING.md for guidance.

---

## Standards alignment
See [STANDARDS_ALIGNMENT.md](STANDARDS_ALIGNMENT.md) how this specification relates to W3C, MCP, A2A, ICO DUAA guidance, and the EU AI Act.

---

## Intellectual foundations

This specification draws on the following published work and practitioner insight:

- Ajit Jaokar, *Enterprise Context Graphs: Data and Decision as the Foundation for Institutional AI Agents*, Oxford University, March 2026 — foundational framework for the decision context layer
- XBow practitioner insight on validator-gated execution and evidence trust over agent trust, 2026
- Reuven Cohen, Cognitum — proof-gated execution architecture and hardware-level governance primitives
- Corewood TETRA — high-performance graph database for low-latency agent context
- Lorenzo Moriondo, tuned.org.uk — embeddings, vector retrieval, and evidence infrastructure research
- ICO guidance on DUAA purpose limitation and legitimate interests, April 2026
- Anthropic Project Glasswing announcement, April 2026 — industry validation of the capability threshold and governance urgency
- IBM + Confluent acquisition, March 2026 — enterprise data substrate for real-time agent governance

The coordination problem this specification addresses is documented in detail in a four-part series by CJ Hodgson on LinkedIn (April 2026).

---

## Licence

Apache 2.0. See LICENSE for full terms.

This specification may be freely used, modified, and distributed. Commercial implementations built on this specification are permitted and encouraged. Attribution is appreciated but not required.

---

*LGT.io — vendor-neutral agentic governance for UK and EU enterprise*
*lgt.io | chris@lgt.io*
