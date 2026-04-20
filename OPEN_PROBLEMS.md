# Open problems

This specification defines five layers of a governance architecture and maps them to current regulatory requirements. It does not claim to be complete. The following problems are known gaps — areas where the specification as currently written is insufficient, and where contribution, research, and dialogue are most urgently needed.

These are named as open problems rather than deferred features. They are structurally harder than the five-layer architecture and may require new primitives, new standards work, or new regulatory guidance to resolve fully.

---

## Open problem 1 — The portable lawful commitment artifact

**Formulation:** A decision graph, validator mesh, and immutable audit trail can explain and defend an outcome within a single governance domain. But if the next domain still has to reconstruct why the act was valid, then the act itself does not hold across domain boundaries.

**The concrete case:** A clinically valid decision is made. It must then move through dispensing, funding approval, and audit review. What exactly reaches the next domain that it can rely on directly, without reopening the prior act? In the current specification, the answer is a decision trace in the audit log — which the next domain must still interpret against its own governance context. That is reconstruction, not portability.

**Why the five-layer architecture is insufficient here:** The immutable audit trail (Layer 5) records what happened and proves it occurred. The validator mesh (Layer 3) authorised the action under the governance rules of the originating domain. Neither makes the act self-validating in a receiving domain that has its own regulatory context, its own legitimate interests test, and its own interpretation of compatible reuse under the DUAA.

---

### The two-primitive framework

Subsequent work by Peter Cranstone (3PMobile, April 2026) has identified the structural reason the five-layer architecture is insufficient here, and has defined two primitives that any solution must provide. This framework is incorporated into the specification with Peter's permission and is reproduced here in the terms he has established.

**The formation problem and the reliance problem are sequential constraints, not the same problem.**

Most governance architectures — including this one at v0.1 — address formation: ensuring that when an agent acts, the decision is explicit, bounded, measurable, auditable, and certifiable. This is necessary. It is not sufficient.

A certified decision is not automatically a reliable unit of action. When a certified decision crosses into a new domain — institutional, jurisdictional, or operational — one of three things typically occurs:

- **Reinterpretation** — the receiving system evaluates the prior decision under its own policies and assumptions
- **Reconstruction** — the receiving system replays the underlying evidence and re-derives the decision
- **Revalidation** — the receiving system requests fresh inputs or new certification before proceeding

In each case, the original decision has not survived intact. The system has not produced a unit that can be accepted as-is. This is the **reconstruction pattern**: Decision → Record → Re-evaluation. It creates real cost and real exposure — re-evaluation cost, delay, duplicated control activity, fragmented accountability, additional liability surface, and weaker institutional confidence in automation. This is the **reconstruction tax**: the repeated need to rebuild confidence in a prior act because the system never produced a dependable unit in the first place.

---

### The two primitives

**Primitive 1 — The human-resolution event (formation)**

The first primitive is the bounded point at which machine ambiguity is resolved by a human contribution that is: specific rather than open-ended; measurable rather than impressionistic; liability-bearing rather than merely advisory; comparable across like cases; and certifiable as part of the system.

This primitive solves the formation problem. It turns the human contribution from a procedural exception into a certifiable event. The current specification defines an escalation path in the validator mesh (Layer 3) for low-confidence decisions but does not yet define the human-resolution event as a first-class primitive with the properties above. This is a gap that v0.2 must address.

**Primitive 2 — The reliance-ready unit (reliance)**

The second primitive is the output condition that must be satisfied if a certified decision is to remain usable beyond its point of origin. A reliance-ready unit is not merely well-documented, replayable, or explainable. It is one that does not require fresh interpretation of the prior act simply to be accepted in the next relying domain.

The decisive structural moment is the **reliance boundary** — the point at which a prior act must transition from being locally valid to being externally usable. It is the moment where a system must decide whether it can act without reopening the prior act. This is distinct from formation, validation, audit, and policy compliance. It is where many systems break. They produce decisions, but not units that hold.

The central distinction, in Peter's formulation:

> **decision ≠ standing**

Certification produces decision quality but not decision persistence. A decision may be correct, justified, documented, signed, and auditable — and still fail as soon as it crosses into another domain that must reinterpret it before acting.

---

### The portable explanation versus portable act distinction

A cryptographically signed artifact carrying the authorisation, purpose compatibility assessment, and confidence classification — such as a W3C Verifiable Credential — is a major step forward. But it remains, in precise terms, an evidence-bearing object. The receiving domain verifies the signature, reads the claims, and then decides whether to rely on them. There is still a moment of interpretation. The act is defensible; it is not yet standing.

In Peter's formulation, reproduced with permission:

> "A cryptographically signed artifact carrying authorisation, purpose compatibility, and confidence is a major step forward — but it may still be an evidence-bearing object unless lawful commitment itself becomes the primary object of reliance. Not just a portable explanation of why the act should be trusted, but what must exist such that the act can be encountered as already standing."

This introduces a second failure mode: a decision can be valid at the point of binding and still fail once it crosses into another domain, because it degrades into something that must be re-evaluated rather than relied upon.

What is needed is a distinction between:

- A **portable explanation** — an artifact that carries the evidence of why the act was valid, which the receiving domain evaluates and chooses to accept. W3C Verifiable Credentials achieve this.
- A **portable act** — a commitment that the next domain encounters as already standing, without reopening the prior authorisation. The act itself is the primary object of reliance, not the evidence about the act.

This distinction is not merely technical. In the physical world, certain classes of legal instrument — notarised documents, court orders, registered titles — achieve the status of portable acts because a legal framework designates them as primary objects of reliance. For agentic AI systems, achieving equivalent status requires two things: a technical primitive that carries the commitment in verifiable form, and a regulatory framework that designates certain classes of governance decision as primary objects of reliance. The former can be specified now. The latter does not yet exist in DUAA or EU AI Act.

---

### What this means for the specification

The five-layer architecture as specified addresses formation adequately at v0.1. It does not yet address reliance. Closing this gap requires:

1. Defining the human-resolution event as a first-class primitive in the validator mesh escalation path (Layer 3) — with the properties of being specific, measurable, liability-bearing, comparable, and certifiable.

2. Defining the reliance-ready unit as an output condition of the governance layer — not a technical container but a set of properties the output must satisfy for it to be accepted without reconstruction in a receiving domain.

3. Defining the reliance boundary as a formal concept in the architecture — the structural moment where local validity must become external usability, and where the governance layer must produce a portable act rather than portable evidence.

4. Identifying what regulatory recognition would need to exist — in ICO guidance, FCA rules, or primary legislation — for a governance output to constitute a primary object of reliance rather than portable evidence.

### The cross-tier interaction problem — a regulatory instantiation of the reliance boundary

The Digital Omnibus package (March 2026) has created a specific and immediate version of this problem that does not require theoretical future scenarios to illustrate. The EU AI Act's Article 111 non-retroactivity clause creates a two-tier market: Tier 1 systems built governance-first, and Tier 2 systems deployed before December 2027 that are permanently exempt unless substantially modified.

Agents do not respect regulatory tiers. A Tier 1 governed system will receive actions from Tier 2 ungoverned systems. Those actions arrive without a certifiable formation event, without a reliance-ready output, without a dependable unit. The Tier 1 system sits at exactly the reliance boundary described above — but the ungoverned domain on the other side is not a failure of design. It is a feature of the regulatory framework.

The reconstruction tax therefore falls structurally and permanently on compliant organisations. Every incoming action from a Tier 2 system must be treated as unverified at the point of receipt — assessed for purpose compatibility, assigned a confidence threshold based on reversibility, and either accepted, escalated, or blocked. This is not a v1.0 capability. It is a Day 1 requirement for any Tier 1 enterprise operating in a mixed environment — which is every enterprise, because the two-tier market guarantees mixed environments for at least the next twenty-four months.

The governance layer's purpose compatibility gate (Layer 3) and system contract registry (Layer 4) are the defensive perimeter at this reliance boundary. Their design must account for the reality that a significant proportion of incoming actions will originate from systems that were never required to produce dependable units — not because of technical failure, but because the regulatory framework made that a viable strategy.

The EU AI Act delay was intended to reduce governance urgency. The cross-tier interaction problem reverses that logic entirely for Tier 1 enterprises. The delay does not reduce the need for a governance layer. It makes the governance layer the only mechanism by which a compliant organisation can protect itself from the reconstruction tax imposed on it by the non-compliance of others.

**What is needed:** Specification of how the Layer 3 purpose compatibility gate should handle incoming actions from unverified or ungoverned domains — including what confidence threshold applies, what escalation path is triggered, and how the decision is recorded in the audit trail. Legal analysis of whether a Tier 1 organisation bears liability for outcomes that originate in Tier 2 ungoverned agent actions received across a domain boundary. Practical implementation experience of cross-tier scenarios where the reconstruction tax is measurable.

**Update — April 2026:** The TETRA technology review (Kyle Mickey, Corewood, April 2026) identifies a candidate technical primitive for the portable lawful commitment artifact. TETRAFILE's multi-recipient cryptographic addressability allows a governance decision formed in one domain to be made readable by a receiving domain through a recipient addition rather than re-derivation. The formation event and the portable artifact are the same object. The receiving domain verifies the signature and has the commitment as a single self-validating unit without reopening the prior act. The reverse-engineering resistance of the format reinforces this: the receiving domain is not evaluating an inspectable payload with optional verification — it is evaluating an artifact whose only legitimate interpretation path is the signature-verified read through the authorised reader.

This does not resolve the regulatory recognition problem. A technical primitive for a portable act does not by itself make that act a primary object of reliance under DUAA or EU AI Act. The remaining work on Open Problem 1 is therefore regulatory rather than architectural. The technical primitive the problem identified as missing now exists in the substrate.

---

*This problem was first articulated in the context of this specification by Peter Cranstone, 3PMobile, April 2026. The two-primitive framework — formation primitive and reliance-ready unit — the reconstruction tax concept, the reliance boundary, and the portable explanation versus portable act distinction are Peter's formulations, developed in parallel with this specification and incorporated here with his permission. The cross-tier interaction problem as a regulatory instantiation of the reliance boundary was identified by CJ Hodgson, LGT.io, April 2026. The identification of TETRAFILE multi-recipient cryptographic addressability as the candidate technical primitive for the portable lawful commitment artifact was made by Kyle Mickey, Corewood, in the TETRA technology review, April 2026.*

---

## Open problem 2 — Temporal validity of lawful commitments

**Formulation:** A governance decision valid at the time it was made may become invalid — or require re-evaluation — when the regulatory context changes after the commitment was entered into. The five-layer architecture as specified addresses the moment of action. It does not address the lifetime of the commitment.

**The concrete case:** A SWAPS contract entered in 2026 carries a lawful basis assessment, a purpose compatibility determination, and a legitimate interests balancing test valid under the DUAA and EU AI Act as they stand today. That contract may run for ten or twenty years. The regulatory context will change. The ICO will publish new guidance. The EU AI Act will be revised. The organisations on both sides may restructure or change jurisdiction. The lawful basis that was valid in 2026 may require re-evaluation in 2031 — not because anything the parties did changed, but because the external regulatory environment moved around them.

**Why this is structurally harder than the cross-domain problem:** The cross-domain problem (Open Problem 1) exists in a single regulatory moment — clinical and dispensing domains are governed by the same current regulation. The temporal validity problem requires the governance layer to maintain awareness of regulatory change over time and to flag when a previously valid commitment falls outside the current boundary due to external rather than internal changes.

**The connection to the validator mesh:** This suggests the validator mesh cannot only fire at the point of action. For long-lived commitments it must run continuously — or be triggered by regulatory change events — to re-evaluate existing authorisations against the current governance context. A commitment that was valid is flagged for review when the surrounding regulation changes sufficiently to bring it into question. This is structurally similar to a financial circuit breaker: it fires not when a new bad thing happens, but when the context changes enough that a previously valid position becomes invalid.

**The connection to the financial services sector:** This problem is acute for UK and EU financial services firms deploying AI agents in derivatives, risk management, and regulatory reporting. LIBOR transition required the systematic re-evaluation of millions of contracts against a changed reference framework — a structural precedent for what temporal regulatory change requires of a governance layer. The FCA's evolving AI regulatory framework and EMIR reporting changes create ongoing versions of the same problem.

**What is needed:** A formal model for regulatory change events and their effect on existing lawful commitments. A trigger mechanism by which the validator mesh is notified of relevant regulatory changes and initiates re-evaluation of affected commitments. Legal analysis of whether the DUAA's accountability principle requires proactive re-evaluation of existing commitments when guidance changes, or only governs new acts.

**Update — April 2026:** The TETRA technology review (Kyle Mickey, Corewood, April 2026) identifies a material substrate consideration for this problem. TETRAFILE uses post-quantum cryptographic primitives drawn from current FIPS post-quantum standards rather than classical public-key primitives. This removes the harvest-now-decrypt-later exposure that classical primitives face over long commitment lifetimes — files produced today under post-quantum primitives are not subject to decryption by quantum adversaries over the lifetime of commitments recorded in them.

The regulatory-change dimension of this problem remains a validator mesh concern that the substrate does not address. But the cryptographic forward-security question — whether a commitment recorded in 2026 will remain cryptographically intact in 2046 — is resolved at the substrate level for implementations built on TETRAFILE. Implementations intending to serve multi-decade commitment lifetimes, including financial derivatives, long-dated contracts, and regulated data retention obligations, should prefer post-quantum substrates. This is now a specification-level recommendation rather than an implementation detail.

---

## Open problem 3 — Governance of emergent multi-agent purpose

**Formulation:** In a single-agent system, purpose evolution is traceable — the agent's actions can be mapped back to the original collection purpose and a compatibility assessment can be performed. In a multi-agent system with non-linear decision chains, purpose evolves as an emergent property of agent interactions rather than through deliberate design decisions. No individual agent in the chain may have acted outside its authorised purpose, yet the collective outcome may constitute a purpose that no individual agent was authorised to pursue.

**The concrete case:** Agent A ingests customer data for Purpose A (service a support query). Agent A passes context to Agent B for Purpose B (route the query). Agent B invokes Agent C for Purpose C (retrieve account history). Agent C's retrieval triggers Agent D which performs Purpose D (identify upsell opportunity based on account history and query context). No individual agent violated its purpose. The collective chain has produced a behavioural insight the customer did not consent to and the organisation did not design.

**Why the five-layer architecture is insufficient here:** The purpose compatibility gate in the validator mesh (Layer 3) assesses each action against the original collection purpose at the point of execution. In a linear single-agent workflow this is sufficient. In a non-linear multi-agent chain, by the time a potentially incompatible purpose emerges it may have already been acted upon by downstream agents. The gate fires on individual actions, not on emergent collective outcomes.

**What is needed:** A mechanism for tracking purpose evolution across agent chains in real time, identifying when the collective purpose of a chain has diverged from the original authorised purpose even if no individual action triggered the compatibility gate. This may require a population-level purpose tracking layer that sits above the individual validator mesh nodes — closer to the correlated signal detection pattern described in the technical architecture literature as necessary for agent-scale governance.

---

## Contributing to open problems

If you are working on any of these problems — in research, in production deployment, or in legal and regulatory practice — we would welcome your contribution. Open a GitHub Issue labelled `open-problem-1`, `open-problem-2`, or `open-problem-3` and describe your work, your findings, or your questions.

These problems will not be resolved by a single organisation. They require the kind of cross-community collaboration that this specification is designed to facilitate.
