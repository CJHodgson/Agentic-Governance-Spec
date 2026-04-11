# Open problems

This specification defines five layers of a governance architecture and maps them to current regulatory requirements. It does not claim to be complete. The following problems are known gaps — areas where the specification as currently written is insufficient, and where contribution, research, and dialogue are most urgently needed.

These are named as open problems rather than deferred features. They are structurally harder than the five-layer architecture and may require new primitives, new standards work, or new regulatory guidance to resolve fully.

---

## Open problem 1 — The portable lawful commitment artifact

**Formulation:** A decision graph, validator mesh, and immutable audit trail can explain and defend an outcome within a single governance domain. But if the next domain still has to reconstruct why the act was valid, then the act itself does not hold across domain boundaries.

**The concrete case:** A clinically valid decision is made. It must then move through dispensing, funding approval, and audit review. What exactly reaches the next domain that it can rely on directly, without reopening the prior act? In the current specification, the answer is a decision trace in the audit log — which the next domain must still interpret against its own governance context. That is reconstruction, not portability.

**Why the five-layer architecture is insufficient here:** The immutable audit trail (Layer 5) records what happened and proves it occurred. The validator mesh (Layer 3) authorised the action under the governance rules of the originating domain. Neither makes the act self-validating in a receiving domain that has its own regulatory context, its own legitimate interests test, and its own interpretation of compatible reuse under the DUAA.

**The direction this specification is exploring:** W3C Verifiable Credentials may provide the answer — a cryptographically signed artifact issued at the point of authorisation that carries the purpose compatibility assessment, confidence classification, and reversibility score as portable, independently verifiable claims. The receiving domain verifies the credential against the issuing authority's signature without needing to contact the issuer or reconstruct the original decision. This would constitute a sixth component of the governance architecture — a portable lawful commitment artifact that sits above the five layers and binds them into a form that survives domain crossing.

**What is needed:** Practical implementation experience of cross-domain governance scenarios. Legal analysis of whether a W3C Verifiable Credential carrying a DUAA purpose compatibility assessment would satisfy the ICO's accountability requirements in the receiving domain. Reference to any existing work on verifiable credentials in regulated data exchange contexts.

*This problem was first articulated in the context of this specification by Peter Cranstone, 3PMobile, April 2026.*

---

## Open problem 2 — Temporal validity of lawful commitments

**Formulation:** A governance decision valid at the time it was made may become invalid — or require re-evaluation — when the regulatory context changes after the commitment was entered into. The five-layer architecture as specified addresses the moment of action. It does not address the lifetime of the commitment.

**The concrete case:** A SWAPS contract entered in 2026 carries a lawful basis assessment, a purpose compatibility determination, and a legitimate interests balancing test valid under the DUAA and EU AI Act as they stand today. That contract may run for ten or twenty years. The regulatory context will change. The ICO will publish new guidance. The EU AI Act will be revised. The organisations on both sides may restructure or change jurisdiction. The lawful basis that was valid in 2026 may require re-evaluation in 2031 — not because anything the parties did changed, but because the external regulatory environment moved around them.

**Why this is structurally harder than the cross-domain problem:** The cross-domain problem (Open Problem 1) exists in a single regulatory moment — clinical and dispensing domains are governed by the same current regulation. The temporal validity problem requires the governance layer to maintain awareness of regulatory change over time and to flag when a previously valid commitment falls outside the current boundary due to external rather than internal changes.

**The connection to the validator mesh:** This suggests the validator mesh cannot only fire at the point of action. For long-lived commitments it must run continuously — or be triggered by regulatory change events — to re-evaluate existing authorisations against the current governance context. A commitment that was valid is flagged for review when the surrounding regulation changes sufficiently to bring it into question. This is structurally similar to a financial circuit breaker: it fires not when a new bad thing happens, but when the context changes enough that a previously valid position becomes invalid.

**The connection to the financial services sector:** This problem is acute for UK and EU financial services firms deploying AI agents in derivatives, risk management, and regulatory reporting. LIBOR transition required the systematic re-evaluation of millions of contracts against a changed reference framework — a structural precedent for what temporal regulatory change requires of a governance layer. The FCA's evolving AI regulatory framework and EMIR reporting changes create ongoing versions of the same problem.

**What is needed:** A formal model for regulatory change events and their effect on existing lawful commitments. A trigger mechanism by which the validator mesh is notified of relevant regulatory changes and initiates re-evaluation of affected commitments. Legal analysis of whether the DUAA's accountability principle requires proactive re-evaluation of existing commitments when guidance changes, or only governs new acts.

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
