# Agentic Governance Layer — Open Specification

**A technology-agnostic open specification for governing AI agent systems operating under the UK Data (Use and Access) Act 2025, UK GDPR, and EU AI Act — with a sovereign-by-default reference implementation built on Corewood TETRA.**

> **Regulatory note (updated April 2026):** The EU AI Act high-risk enforcement deadline has moved to December 2027 under the Digital Omnibus package. The DUAA is already in force. This specification treats the DUAA as the primary near-term regulatory driver and the EU AI Act as the medium-term destination. See the roadmap section for implications.

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

The EU AI Act remains a significant governance driver, though its enforcement timeline has shifted. Under the Digital Omnibus package agreed by Parliament and Council in March 2026, the high-risk AI system deadline moved from August 2026 to December 2027, with AI embedded in medical devices moving to August 2028. This is not straightforward breathing room. Article 111's non-retroactivity clause means any high-risk AI system placed on the market before the deadline is exempt from the Act unless substantially modified afterward — creating a two-tier market in which organisations that deployed governance-first face competitors who did not, now operating under different rules indefinitely. The Act's requirements remain the destination: automated audit trails, documented governance processes, incident reporting, penalties up to 3% of global annual revenue. The deadline has moved. The architecture has not.

The two-tier market creates an immediate fourth forcing function that the delay itself generates. Agents do not respect regulatory tiers. A Tier 1 system — compliant, governed, with full audit trail and purpose compatibility assessment — will inevitably receive actions from Tier 2 systems that were deployed before the deadline and are exempt from governance requirements. Those Tier 2 systems produce no dependable unit, no reliance-ready output, no certifiable formation event. The Tier 1 system receives an action from an ungoverned domain and must decide whether to act on it.

This is the cross-tier interaction problem. It cannot be solved by the Tier 2 system — that system has no governance requirement. It can only be solved by the Tier 1 system's governance layer, which must treat every incoming action from an ungoverned domain as unverified at the point of receipt. The reconstruction tax — the repeated cost of rebuilding confidence in a prior act that arrived without dependable provenance — falls entirely on the compliant organisation, not on the one that avoided compliance. The EU AI Act delay was intended to reduce governance urgency. The cross-tier interaction problem reverses that logic: for any Tier 1 enterprise operating in a mixed environment — which is every enterprise for the foreseeable future — the governance layer is more urgent now, not less.

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

**Design principle — hash chaining:** Cryptographic audit trails — the pattern demonstrated by the blockchain community through Merkle tree structures — provide tamper-evidence without requiring a distributed ledger. A hash chain of decision records, where each record includes the hash of the previous record, makes retrospective modification detectable. This is architecturally lighter than full blockchain deployment and compatible with enterprise latency requirements.

**Alternative design principle — file-format-native tamper-evidence:** A substrate that provides per-section cryptographic integrity at the file format level — such that any modification of the file is detectable on read, as a native property of the format rather than a secondary audit layer — satisfies Layer 5 without requiring a separate append-only record. Where such a substrate is used, Layers 2 and 5 collapse into a single artifact: the decision context graph is simultaneously the tamper-evident audit trail, and verification of the file is simultaneously verification of the audit record.

This is a stronger property than the hash-chaining pattern. It removes the architectural dependency between the decision context store and the audit log, eliminates the synchronisation problem between them, and makes the audit trail intrinsic to the governance artifact rather than dependent on a parallel system. Future revisions of this specification will consider whether the separation of Layers 2 and 5 reflects an architectural necessity or an accident of the specification's derivation from prior art in systems where file-format-native integrity was not available.

*This architectural observation was first made in the context of this specification by Kyle Mickey, Corewood, in the TETRA technology review, April 2026.*

**Interface this layer must expose:**
- Append-only write: decision records written with cryptographic chaining (hash-chain pattern) or file-format-native integrity (collapsed Layer 2/5 pattern)
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

The specification itself is technology-agnostic — it can in principle be implemented on any graph database, any LLM, and any execution environment. The Apache 2.0 licence explicitly permits this and any organisation may build their own implementation on their preferred infrastructure.

The reference implementation maintained by LGT.io is built on Corewood TETRA — a deliberate choice based on TETRA's demonstrably superior performance characteristics, sovereign deployment capability, and minimal infrastructure footprint for the specific requirements of the governance layer. Other implementors are free to make different choices. The specification defines what must be true of any implementation, not how it must be built.

It does not claim to solve every governance problem in agentic AI. It addresses the specific gap between what current vendor governance tooling provides and what the DUAA and EU AI Act require for organisations deploying agents across heterogeneous legacy estates.

---

## Current status and roadmap

**v0.1 (April 2026) — Interface specification**
This document. Defines the five layers and their required interfaces. Does not specify implementation.

**v0.2 (target: June 2026) — Reference implementation**
A minimal working implementation of all five layers against a defined test environment, using Corewood TETRA as the decision context graph and a configurable validator mesh.

**v0.3 (target: September 2026) — DUAA compliance toolkit**
Tooling for purpose compatibility assessment and legitimate interests balancing, aligned with ICO guidance published under the DUAA. The DUAA is already in force and is the primary regulatory driver for UK deployments.

**v1.0 (target: mid-2027) — EU AI Act readiness**
Full compliance mapping and audit export capability aligned with EU AI Act enforcement requirements. Note: following the Digital Omnibus package (March 2026), the high-risk AI system deadline moved to December 2027. Article 111's non-retroactivity clause means systems placed on market before that date are exempt unless substantially modified. This specification is designed for organisations building governance-first — for whom the deadline is not an escape route but a destination.

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

See [ENDORSEMENTS.md](ENDORSEMENTS.md) for external contributions to this specification.## Intellectual foundations

___


This specification draws on the following published work and practitioner insight:

- Ajit Jaokar, *Enterprise Context Graphs: Data and Decision as the Foundation for Institutional AI Agents*, Oxford University, March 2026 — foundational framework for the decision context layer
- XBow practitioner insight on validator-gated execution and evidence trust over agent trust, 2026
- Reuven Cohen, Cognitum — proof-gated execution architecture and hardware-level governance primitives
- Corewood TETRA and TETRAFILE — high-performance graph database and governance artifact substrate. Kyle Mickey, Corewood, contributed the TETRA technology review (April 2026) identifying the TETRA/TETRAFILE architectural distinction, the Layer 2/5 collapse property, TETRAFILE multi-recipient addressability as the candidate portable lawful commitment primitive, and post-quantum forward-security as a specification-level substrate recommendation. These contributions materially advanced the specification.
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
