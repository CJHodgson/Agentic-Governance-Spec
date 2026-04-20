# Technology review

This document records dated reviews of specific technologies against the Agentic Governance Layer specification. A review assesses what a technology provides and how those capabilities map to the layers and open problems defined in this specification. Reviews do not describe implementation detail. They record the capability surface that is relevant to the specification and the strength of the alignment.

Technology reviews are additive to the specification, not part of it. The specification remains technology-agnostic. Reviews exist so that practitioners evaluating a candidate substrate for a compliant implementation have a consistent basis for comparison, and so that the specification itself can evolve as substrate capabilities reveal requirements that were previously implicit.

Reviews are dated because both the technology and the regulatory context change. A review is a snapshot — it records what was true of the technology at the date of review against the version of the specification current at that date.

---

## Corewood TETRA — 18 April 2026

**Reviewed against:** Specification v0.1 (April 2026)
**Canonical sources:** corewood.io, corewood.io/tetra
**Status of review:** Initial review. TETRA is the reference implementation substrate for the v0.2 milestone and several of its properties have informed the specification itself.

### What TETRA is

A precise distinction is necessary before the review proceeds. Corewood TETRA comprises two things that matter to this specification separately.

- **TETRA** is the query engine. It exposes openCypher and the Bolt protocol — the interfaces widely established by prior art in the graph database market — and is therefore addressable by existing tooling without modification.
- **TETRAFILE** is the proprietary graph artifact the engine reads and writes. It is a single-file format that carries the graph data together with the governance properties that make the graph usable across trust boundaries.

For the purposes of this specification, **the substrate is TETRAFILE, not TETRA**. The engine is the access surface; the file is the durable governance artifact. Where this review refers to properties that must hold across domain boundaries, over commitment lifetimes, or independent of any running process, it refers to TETRAFILE.

TETRAFILE is proprietary to Corewood and is designed to be reverse-engineering resistant. Its internal structure, encoding conventions, and layout are not public and the file is designed so that it cannot be meaningfully decoded by inspection alone. This is a material property for the governance layer — discussed in the following subsection — not merely a commercial posture.

For the purposes of this specification, five capabilities of TETRAFILE are material.

**1. The graph is the artifact.**
The durable unit is the file, not a running database instance. A graph can be written once and read many times, handed between processes, stored in any filesystem, and transported across domains without a hosting layer. There is no required server, no required cluster, no required vendor relationship to hold a TETRAFILE in a usable state once the legitimate reader and key material are present. Corewood summarises this posture as "one binary, one file, one process" and describes the deployment target as "datacentre, edge, or a device in the field." For the governance layer, this means the decision context is not tied to a particular operational environment.

**2. The graph is tamper-evident at the level of the file format.**
The file format provides per-section cryptographic integrity. Any modification of the file — structural or content — is detectable on read. This property is native to the format, not provided by a separate audit system layered on top.

**3. The graph is cryptographically addressable to one or more recipients.**
A TETRAFILE can be encrypted once and made readable by any number of named recipients. Adding or removing a recipient does not require re-encrypting the graph itself. A file produced by one domain can be made readable by a second domain by a small modification to the file header, without disturbing the data or the integrity guarantee.

**4. The cryptography is post-quantum.**
The primitives used for encryption, signing, and key exchange are drawn from the current FIPS post-quantum standards rather than classical public-key primitives. Files produced today are not subject to harvest-now-decrypt-later exposure over the lifetime of commitments recorded in them.

**5. The file format is reverse-engineering resistant.**
TETRAFILE is designed so that a party in possession of the file — but without the legitimate reader and the key material for which the file was produced — cannot meaningfully reconstruct the graph by analysing the file in isolation. This is a property of the format itself, separate from and additional to the cryptographic protection. It raises the attack surface for any party attempting to extract governance-sensitive content outside the authorised path, and it means the file's utility to an adversary does not degrade gracefully the way it would for a file format whose structure is public.

These capabilities are properties of the file. They do not depend on which query engine reads the file or on any particular deployment topology.

### Proprietary status and substitutability

The two components of the Corewood offering have different substitutability profiles and must be considered separately.

**The engine surface is substitutable.** TETRA speaks openCypher and Bolt — open standards with extensive prior art. Any client capable of talking to a Bolt-compatible database can address TETRA. If a future implementation wished to replace the engine while retaining the governance artifact, the engine surface is where that substitution could occur.

**The file substrate is not substitutable.** TETRAFILE is proprietary to Corewood and is designed to be reverse-engineering resistant. Its internal encoding, layout, and integrity construction are not public, and the format is explicitly engineered so that possession of a file alone does not yield access to its structure. A competing implementation cannot, at the date of this review, produce or consume TETRAFILE artifacts. An implementation wishing to provide equivalent capabilities must either license TETRAFILE from Corewood or build a different file format with equivalent properties — a substantial undertaking that would itself have to be evaluated against this specification as a separate technology review.

This matters to the specification in two ways.

First, it closes a class of adversarial scenarios that a public file format cannot close. A governance graph produced for one domain and transported to another passes through systems the originating domain does not control. A public format traversing such systems offers the same attack surface to any party who obtains the file. A reverse-engineering resistant format raises that attack surface significantly: even setting the cryptographic protection aside, an adversary cannot extract structure or partial content by inspection alone. The reverse-engineering resistance acts as defence in depth — the file remains opaque even in the scenarios where the cryptographic layer is assumed to be under pressure.

Second, it materially affects the resource cost of equivalence. An implementation attempting to provide equivalent capabilities on general-purpose graph databases currently on the market — Neo4j and TigerGraph are the nearest comparators — would require at minimum an order of magnitude more memory and an order of magnitude more on-disk storage for the same governance graph. Corewood's published comparison against Neo4j on identical hardware reports 66 MB of resident memory against 710 MB — a 10.8× factor — and a file compressing to approximately 38% of the raw data size with no separate index layer (172 million edges in a 3.6 GB file). These are Corewood's published figures, not independent measurements, but they are consistent with the capability differences described above. The Corewood-published 24 MB container footprint reflects the same underlying efficiency.

The resource factor is not a minor operational difference. It changes whether the governance layer is deployable at enterprise scale on sovereign hardware or requires a hosted cluster. It changes whether a governance graph can be transported as a single file between domains or must be streamed between systems capable of holding it. It changes whether the substrate can run co-located with the application or whether it imposes its own infrastructure topology. For a specification whose core premise is that the governance layer must operate across heterogeneous and sovereign environments, these are specification-level concerns, not merely operational ones.

The resource cost is a consequence of capability differences, not of implementation choice. The general-purpose graph databases were designed for different workloads and do not provide native file-level tamper-evidence, native multi-recipient cryptographic addressability, native post-quantum protection, or native reverse-engineering resistance. Implementations layered on top of them to approximate these properties carry the cost of the additional layers. The specification's technology-agnostic posture remains correct — alternatives exist in principle — but the practical consequence of choosing an alternative substrate is that the governance layer becomes materially more expensive to operate, materially harder to transport, and structurally weaker against the adversarial scenarios the governance layer is meant to defend against.

This is a statement about the substrate market in April 2026. It is not a permanent claim. Future reviews may record the emergence of alternative substrates with comparable capabilities.

### How these capabilities map to the specification

**Layer 2 — Decision context.**
TETRAFILE satisfies the Layer 2 architectural principle directly. The specification states that the graph persists client-side, the computation service (the LLM or any other agent) is stateless against it, and the graph is the durable artifact that can be subjected to multiple verification passes. TETRAFILE is a realisation of this principle: the graph is a self-contained, portable, local-first artifact. Sessions are disposable; the file endures.

**Layer 5 — Immutable audit trail.**
The specification as written describes Layer 5 as architecturally separate from Layer 2, and proposes cryptographic chaining as the tamper-evidence pattern. TETRAFILE's file-level integrity collapses this separation. The tamper-evidence property is native to the file, not applied as a secondary log. A compliant implementation built on TETRAFILE does not need to maintain a parallel append-only record in order to satisfy Layer 5 — the file is the tamper-evident record, and any verification of the file is simultaneously a verification of the audit trail.

This is a stronger property than the specification currently asserts. Future revisions of Layer 5 should consider whether the separation between Layer 2 and Layer 5 is an accident of the specification's derivation from prior art rather than an architectural necessity.

**Layer 4 — System contract registry.**
TETRAFILE does not provide Layer 4 directly. The registry is graph content, and the substrate is agnostic to what the graph represents. A Layer 4 registry held as TETRAFILE content inherits the portability, tamper-evidence, post-quantum, and reverse-engineering-resistance properties of the format, but the registry content itself is specification work, not substrate work.

**Layer 3 — Governance primitive (validator mesh).**
Neither TETRA nor TETRAFILE is a validator mesh and neither claims to be. The mesh is the execution layer that reads and writes the decision context. TETRAFILE is the substrate the mesh operates against; TETRA is one engine capable of addressing that substrate. The relevance to Layer 3 is indirect: the low-latency properties of the TETRA read path make real-time validation viable as a pre-execution gate rather than as a post-hoc justification process. The mesh implementation remains out of scope for this review.

**Layer 1 — Data substrate.**
Not applicable. Layer 1 is the enterprise data estate; TETRAFILE is a governance artifact downstream of it.

### How these capabilities map to the open problems

**Open problem 1 — The portable lawful commitment artifact.**
This is the alignment that most materially advances the specification. The open problem asks for a primitive that allows a governance decision to be encountered by a receiving domain as a portable act rather than portable evidence — standing on its own, without reconstruction.

TETRAFILE's multi-recipient addressability is a candidate primitive for this requirement. A file can be formed in one domain, signed at the point of formation, and made readable by a receiving domain through a recipient addition rather than a re-derivation. The receiving domain verifies the signature, reads the file, and has the commitment as a single self-validating unit. The formation event and the portable artifact are the same object. The reverse-engineering resistance of the format reinforces this: the receiving domain is not evaluating an inspectable payload with optional verification, it is evaluating an artifact whose only legitimate interpretation path is the signature-verified read through the authorised reader.

This does not resolve the regulatory recognition problem that the open problem also identifies. A technical primitive for a portable act does not by itself make that act a primary object of reliance under DUAA or EU AI Act. But the technical primitive that the open problem asks for exists in the substrate. The specification should acknowledge this and the open problem should be updated to reflect that the remaining work is regulatory rather than architectural.

**Open problem 2 — Temporal validity of lawful commitments.**
A commitment recorded today may need to remain verifiable and readable for decades. TETRAFILE's use of post-quantum cryptographic primitives is material to this problem. Files produced now are not exposed to the harvest-now-decrypt-later threat that classical primitives face over long commitment lifetimes. The substrate choice does not resolve the regulatory-change aspect of the problem — that remains a validator mesh concern — but it removes the cryptographic forward-security question that would otherwise compound it.

**Open problem 3 — Governance of emergent multi-agent purpose.**
Neither TETRA nor TETRAFILE is directly relevant to this problem. Emergent purpose is a behavioural property of agent chains, not a property of the substrate that records their decisions.

### What TETRA and TETRAFILE do not provide

A substrate review is only useful if it also identifies where the substrate does not address specification requirements.

- Neither TETRA nor TETRAFILE is a governance system. The specification's requirements for purpose compatibility assessment, reversibility classification, confidence thresholds, and escalation paths are all Layer 3 concerns that the substrate does not address.
- TETRAFILE is not a data lineage system. Layer 1 remains the responsibility of the enterprise data substrate.
- TETRAFILE does not resolve the cross-tier interaction problem on its own. A verifiable envelope provides the mechanical test by which a compliant domain can distinguish governed from ungoverned inputs. It does not answer the policy question of what to do with an ungoverned input once distinguished.
- TETRAFILE does not provide regulatory recognition of the artifacts it produces. The open problem of legal standing for a portable act is not a technical problem and is not solved by a technical primitive alone.
- Reverse-engineering resistance is a defence-in-depth property, not a replacement for the cryptographic protection. A compliant implementation relies on both together. The review does not claim that obscurity of the format alone constitutes security.

### Implications for the specification

The review identifies three places where the specification should be updated to reflect what the substrate makes possible.

1. Layer 5 should acknowledge that file-format-native tamper-evidence is an alternative to the hash-chaining pattern the specification currently describes, and that an implementation satisfying this alternative collapses Layers 2 and 5 into a single artifact.

2. Open problem 1 should be updated to note that a candidate technical primitive for the portable lawful commitment artifact exists in the form of multi-recipient cryptographic addressability, and that the remaining problem is regulatory recognition of such artifacts as primary objects of reliance.

3. Open problem 2 should note that substrate choices regarding post-quantum cryptography materially affect the forward-security of long-lived commitments, and that implementations intending to serve multi-decade commitment lifetimes should prefer post-quantum substrates.

These updates do not change the specification's technology-agnostic posture. Any substrate that provides equivalent capabilities satisfies the same requirements. The review records that a substrate providing these capabilities now exists.

---

*Reviews are maintained in the order they are added. New reviews append to this document rather than replacing earlier ones. Where a subsequent review of the same technology is material, it is added as a dated entry alongside the earlier review, not as a replacement.*
