# Standards alignment

This specification is designed to complement and build upon emerging open standards for agentic AI systems. Where relevant standards exist or are in active development, this specification references them explicitly rather than duplicating work.

---

## W3C AI Agent Protocol Community Group

**URL:** https://www.w3.org/community/agentprotocol
**Status:** Active — biweekly meetings, draft white paper and protocol specification published

The W3C AI Agent Protocol Community Group is developing open, interoperable protocols for agent identity, discovery, and communication across heterogeneous platforms. Their core technical contribution is the `did:wba` method — a Web-anchored implementation of Decentralised Identifiers (DIDs) that enables agents to authenticate each other without a central authority, using existing Web PKI and HTTPS infrastructure.

**Relationship to this specification:**

This specification's Layer 5 (immutable audit trail) and Layer 4 (system contract registry) are designed to be compatible with did:wba agent identity. Specifically:

- Audit trail records reference agent DIDs rather than platform-specific identifiers, making audit entries independently verifiable without relying on any single vendor's identity system
- The system contract registry can record which agent DID classes are permitted to interact with which system types, providing a machine-readable access control layer that persists across sessions
- The validator mesh (Layer 3) can use DID-based authentication to verify the provenance of action proposals in multi-agent chains — addressing the non-linear purpose evolution problem under DUAA

**What the W3C group does not address:**

The W3C group's scope is agent communication and identity — how agents prove who they are and establish trust before acting. It does not address whether a proposed action should proceed, how confidence threshold varies with reversibility, or how DUAA purpose compatibility is assessed at runtime. This specification addresses that gap.

---

## W3C Agentic Integrity Verification Specification (proposed)

**URL:** https://www.w3.org/community/blog/2026/03/30/proposed-group-agentic-integrity-verification-specification-community-group/
**Status:** Proposed — requires five supporters to launch

This proposed W3C Community Group addresses the integrity and verification of consequential agent actions — browsing websites, submitting forms, executing code, and making purchasing decisions on behalf of humans. Its scope overlaps directly with Layer 3 (validator mesh) and Layer 5 (immutable audit trail) of this specification.

This specification is intended to serve as a UK and EU regulatory compliance implementation layer for whatever the Agentic Integrity Verification Specification group produces. As that group's standards mature, this specification will align its interface definitions accordingly.

**We encourage contributors to this specification to support the proposed W3C group at the link above.**

---

## Model Context Protocol (MCP)

**Governance:** Linux Foundation Agentic AI Foundation (from December 2025)
**Status:** Widely adopted — supported by Anthropic, AWS, Microsoft, Google, and others

MCP defines a standardised connector layer for AI agents to access external tools, data sources, and APIs. It is the current de facto standard for agent-to-tool connections and is directly relevant to this specification's Layer 4 (system contract registry).

**Relationship to this specification:**

MCP server definitions encode information about what a tool does and how to call it. The system contract registry extends this by adding the consistency model, failure modes, rollback capability, and era classification of the underlying system — information MCP does not currently capture but that is essential for cross-era governance. A DUAA-compliant implementation should treat MCP server definitions as the starting point for system contract registry entries, enriched with the governance properties this specification requires.

---

## Agent2Agent (A2A) protocol

**Origin:** Google (2025), now under broader industry adoption
**Status:** Maturing — agent card specifications and discovery mechanisms in active development

A2A defines how agents discover each other's capabilities and coordinate tasks. It complements MCP (agent-to-tool) by addressing agent-to-agent communication.

**Relationship to this specification:**

A2A agent cards describe what an agent can do. The validator mesh (Layer 3) needs to know not just what an agent proposes to do, but what its declared capability scope is — enabling it to flag actions that fall outside an agent's authorised envelope. A2A agent cards are the natural source for that scope definition. This specification's action proposal API should be designed to accept A2A agent cards as an input to the authorisation decision.

---

## Decentralised Identifiers (DIDs) — W3C Recommendation

**URL:** https://www.w3.org/TR/did-core/
**Status:** W3C Recommendation (stable)

DIDs provide the cryptographic identity primitive that makes tamper-evident audit trails independently verifiable. Rather than relying on a centralised identity system that an organisation controls and could retrospectively modify, DID-based audit entries are verifiable by any party with access to the DID document — satisfying the EU AI Act's requirement for audit trails that cannot be retrospectively altered.

This specification recommends DID-based agent identity for all production implementations of Layer 5.

---

## UK ICO guidance under DUAA

**Published:** April 2026
**URLs:**
- Recognised legitimate interest: https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/lawful-basis/recognised-legitimate-interests/
- Purpose limitation: https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-protection-principles/purpose-limitation/
- Compatible reuse: https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-protection-principles/purpose-limitation/compatible-reuse-of-personal-information/

The ICO's April 2026 guidance on recognised legitimate interest and purpose limitation under the DUAA is the primary regulatory reference for Layer 3 (validator mesh) purpose compatibility assessment. The compatible reuse guidance specifically defines the test that the purpose compatibility gate in this specification must implement.

**This specification tracks ICO guidance updates.** As the ICO publishes further guidance on agentic AI specifically, the purpose compatibility assessment interface will be updated to reflect it.

---

## EU AI Act

**Enforcement:** August 2, 2026 (high-risk AI systems)
**Reference:** https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689

The EU AI Act's requirements for high-risk AI systems — human oversight, automated audit trails, documented governance processes, incident reporting — are the primary regulatory driver for Layers 3, 4, and 5 of this specification. The compliance mapping table in the main README shows explicitly which layer satisfies which requirement.

Organisations deploying agents in regulated sectors (financial services, healthcare, critical infrastructure, employment) should treat this specification as a component of their EU AI Act compliance programme, not a substitute for it. Legal review of the specific risk classification of their agent deployment is required separately.
