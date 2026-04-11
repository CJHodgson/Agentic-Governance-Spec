# Contributing to the Agentic Governance Layer Specification

Thank you for your interest in contributing. This specification exists because the governance gap in agentic AI is too important and too urgent to be solved by any single organisation. We welcome contributions from practitioners, researchers, legal professionals, and organisations deploying AI agents in regulated environments.

---

## What we are looking for

This is a technical and legal specification, not a general AI discussion forum. Contributions are most valuable in the following areas:

**Technical contributions**
- Implementation experience against specific legacy system types — what did you learn deploying agents against ACID systems, eventual consistency systems, or mainframe environments?
- Reference implementations of individual layers — working code that demonstrates a layer interface in a specific technology stack
- Test cases and validation scenarios — how should a compliant implementation behave in edge cases?
- Performance and scalability findings — what are the practical limits of the validator mesh at agent scale?
- Integration patterns — how does this specification compose with MCP, A2A, did:wba, and other emerging standards?

**Legal and regulatory contributions**
- Review of the DUAA compliance mapping — is the purpose compatibility assessment framework legally sound under current ICO guidance?
- Review of the EU AI Act compliance mapping — does each layer satisfy the requirements as stated?
- Jurisdiction-specific analysis — how does this specification need to adapt for specific EU member state implementations of the AI Act?
- Case studies — real deployment scenarios where the governance gap created compliance risk

**Specification contributions**
- Gap analysis — what has this specification missed or underspecified?
- Interface refinements — are the API definitions in each layer precise enough to be implementable?
- Terminology — is the language consistent and unambiguous?

---

## What we are not looking for

To keep the specification focused and practically useful, we ask contributors to avoid:

- General commentary on AI ethics or policy not directly connected to the specification
- Vendor-specific implementation advocacy — this specification is intentionally vendor-neutral
- Proposals that would introduce dependencies on any single cloud provider or platform
- Contributions that have not been tested or validated in some form — speculation is less useful than experience

---

## How to contribute

**For small corrections** (typos, broken links, factual errors in compliance mappings):
Open a GitHub Issue describing the problem and the correction. For straightforward fixes, a Pull Request is welcome directly.

**For substantive additions** (new layer definitions, compliance mappings, reference implementations):
Open a GitHub Issue first, describing what you want to contribute and why. This allows discussion before significant work is invested. Label your issue with the relevant layer (Layer-1 through Layer-5) or with `compliance`, `implementation`, or `standards-alignment` as appropriate.

**For legal and regulatory review:**
Open a GitHub Issue labelled `legal-review`. Describe your professional context (legal practitioner, compliance officer, academic, etc.) so contributors can assess the basis for your input. Anonymous legal contributions are welcome but should be clearly marked as such.

**For research contributions:**
If you are contributing findings from academic or applied research, please include a reference to the underlying work. Lorenzo Moriondo's research at tuned.org.uk on embeddings and generative retrieval is an example of the kind of research contribution that strengthens the evidence infrastructure layer.

---

## Review process

At v0.1, this specification is maintained by LGT.io. All Pull Requests are reviewed by the maintainer before merging.

**Review criteria:**

1. Is the contribution technically accurate and based on verifiable evidence or experience?
2. Is it consistent with the vendor-neutral, compliance-first principles of the specification?
3. Does it strengthen or clarify — not replace — existing content without good reason?
4. For legal contributions: is it grounded in current ICO, EU AI Act, or relevant jurisdiction guidance?
5. Does it move the specification toward the v0.2 reference implementation milestone?

**Response time:** We aim to respond to Issues within five working days and to Pull Requests within ten working days. This is a small team. If your contribution is urgent, note that in your Issue.

---

## Becoming a reviewer

As the specification matures, we will invite contributors who have made substantive, high-quality contributions to become reviewers. Reviewers are credited in the specification and have a voice in major architectural decisions.

If you believe your expertise makes you a strong candidate for a reviewer role before you have contributed, introduce yourself in a GitHub Issue labelled `reviewer-interest` and describe your background and what you would bring to the review process.

---

## Code of conduct

Contributions to this repository are subject to the following basic expectations:

- Be precise. Vague contributions are not useful in a specification context.
- Be constructive. Identify problems and propose solutions wherever possible.
- Respect the regulatory context. This specification operates in a legally sensitive space. Contributions that could expose users to compliance risk will not be accepted without careful review.
- Respect other contributors. This community includes practitioners, researchers, and legal professionals from different backgrounds. Engage with the substance of contributions, not the identity of contributors.

---

## Attribution

Contributors whose work is incorporated into the specification will be credited in the relevant section and in the specification's intellectual foundations. Significant contributors may be invited to be named as co-authors of specific sections.

We follow the Apache 2.0 licence for all contributions. By submitting a Pull Request, you confirm that you have the right to contribute the content and that you agree to it being distributed under Apache 2.0.

---

## Current priorities for v0.2 (target: June 2026)

The following areas are most urgently needed for the reference implementation milestone:

- A working implementation of Layer 2 (decision context graph) using Corewood TETRA
- A purpose compatibility assessment function implementing the ICO's compatible reuse test
- A minimal validator mesh implementation demonstrating asynchronous probabilistic consensus
- did:wba integration with Layer 5 (immutable audit trail)

If you are working on any of these, please open an Issue to coordinate and avoid duplicating effort.

---

*LGT.io — vendor-neutral agentic governance for UK and EU enterprise*
*Maintained by CJ Hodgson | chris@lgt.io*
