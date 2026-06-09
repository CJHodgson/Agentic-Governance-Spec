# Technology review

This document records dated reviews of specific technologies against the Agentic Governance Layer specification. A review assesses what a technology provides and how those capabilities map to the layers and open problems defined in this specification. Reviews do not describe implementation detail. They record the capability surface that is relevant to the specification and the strength of the alignment.

Technology reviews are additive to the specification, not part of it. The specification remains technology-agnostic. Reviews exist so that practitioners evaluating a candidate substrate for a compliant implementation have a consistent basis for comparison, and so that the specification itself can evolve as substrate capabilities reveal requirements that were previously implicit.

Reviews are dated because both the technology and the regulatory context change. A review is a snapshot — it records what was true of the technology at the date of review against the version of the specification current at that date.

A note on the sovereignty constraint: this specification is technology-agnostic in its interface definitions, but regulated UK and EU enterprise deployments must satisfy the sovereignty constraint defined in the README — specifically, the substrate must be deployable on customer-controlled infrastructure with no required runtime connection to vendor-operated services, must be domiciled outside US CLOUD Act jurisdiction, and must ensure the governance artifact is held by the customer rather than the vendor. Reviews note where a technology satisfies or fails this constraint.

---

## FalkorDB — June 2026

**Reviewed against:** Specification v0.1 (April 2026)
**Canonical sources:** falkordb.com, github.com/FalkorDB/FalkorDB
**Status of review:** Initial review. FalkorDB is the graph engine substrate selected for the LGT.io reference implementation (truc) v0.2 milestone.
**Sovereignty status:** Israeli-domiciled (FalkorDB Ltd, Petah Tikva, Israel). Outside US CLOUD Act jurisdiction. Self-hostable under SSPLv1. Customer-operated deployments have no required runtime connection to FalkorDB Ltd infrastructure. Satisfies the sovereignty constraint for regulated UK and EU enterprise deployments when self-hosted.

---

### What FalkorDB is

FalkorDB is a high-performance graph database built on sparse matrix algebra (GraphBLAS) for graph representation. It executes graph traversals using linear algebra operations rather than pointer-chasing, providing order-of-magnitude performance advantages over traditional graph databases for the traversal patterns characteristic of governance decision context queries.

FalkorDB is the direct successor to RedisGraph following its end-of-life in January 2025. It exposes the openCypher query language over the Bolt wire protocol — the interfaces widely established by prior art in the graph database market — and is therefore addressable by any existing Bolt-compatible client tooling without modification.

For the purposes of the LGT.io reference implementation, FalkorDB serves as the query execution layer for the decision context graph. The truc artifact format (a protobuf-enveloped file with Merkle integrity tree and post-quantum cryptographic sealing) is the durable governance artifact. FalkorDB provides the in-process query surface against the loaded graph. The relationship is: truc owns the artifact; FalkorDB owns the query execution. When a truc artifact is opened, its graph content is loaded into FalkorDB; queries execute via openCypher; mutations are written back to the artifact on commit.

---

### Capability assessment against the specification

**Performance characteristics**

FalkorDB's sparse matrix algebra implementation provides performance characteristics well-suited to real-time governance decision evaluation:

- Query performance scaling: from approximately 20,000 QPS on a single node to 120,000 QPS on a six-node cluster
- Multi-tenancy: up to 10,000+ isolated graph instances per FalkorDB instance — relevant for multi-customer deployments
- Integrated vector indexing and full-text search alongside graph traversal in a single query surface
- Native GraphRAG implementation showing up to 5× query speed improvement over traditional RAG methods for context-retrieval workloads

These characteristics make FalkorDB viable as a pre-execution governance gate substrate — where query latency must be low enough that governance evaluation does not materially slow agent execution.

**openCypher and Bolt compatibility**

Full openCypher support over Bolt is the specification's required wire protocol (as defined in the reference implementation's ADR-005). FalkorDB satisfies this without adaptation. Existing Neo4j-compatible client tooling works against FalkorDB unchanged.

---

### How these capabilities map to the specification

**Layer 2 — Decision context.**
FalkorDB directly satisfies the Layer 2 architectural principle. The specification requires that the graph persist client-side, that the LLM or agent framework be stateless against it, and that the graph be the durable artifact capable of multiple verification passes. In the truc reference implementation, FalkorDB provides the query execution surface against the artifact's loaded graph content. Sessions are disposable; the artifact endures.

**Layer 3 — Governance primitive (validator mesh).**
FalkorDB's performance characteristics make real-time validation viable as a pre-execution gate rather than a post-hoc process. The governance primitives — purpose compatibility, reversibility classification, confidence threshold, escalation routing, circuit-breaker — are implemented as openCypher queries against the decision context graph in the reference implementation. FalkorDB is not itself a governance system; it is the substrate against which deterministic governance graph operations execute.

**Layer 4 — System contract registry.**
The system contract registry is graph content within the truc artifact. FalkorDB provides the query surface against that content — no additional capability is required. Registry entries inherit the artifact's integrity and portability properties.

**Layer 5 — Immutable audit trail.**
FalkorDB does not provide Layer 5 directly. In the truc reference implementation, Layer 5 is provided by the artifact format's file-format-native tamper-evidence (the Merkle integrity tree over artifact sections), which collapses Layers 2 and 5 into a single artifact. FalkorDB is not involved in the audit trail property — that is a property of the artifact format, not the query engine.

**Layer 1 — Data substrate.**
Not applicable. Layer 1 is the enterprise data estate; FalkorDB is a governance substrate downstream of it.

---

### How these capabilities map to the open problems

**Open problem 1 — The portable lawful commitment artifact.**
FalkorDB's graph query surface is relevant to formation (Layer 2 decision context construction) but not to portability. The portable act property is provided by the truc artifact format's multi-recipient cryptographic addressability — a property of the file format, not the query engine. FalkorDB's role is to provide the query surface against the decision context that informs the formation event; the portability of the resulting artifact is independent of FalkorDB.

**Open problem 2 — Temporal validity of lawful commitments.**
FalkorDB's graph query surface enables the validator mesh to re-evaluate existing commitments against changed context — the graph holds the prior decision context, and a re-evaluation query can execute against it when triggered by a regulatory change event. This is the correct architectural approach to the temporal validity problem at the formation layer. The cryptographic forward-security property (resistance to harvest-now-decrypt-later attacks over long commitment lifetimes) is provided by the truc artifact format's post-quantum cryptographic construction, not by FalkorDB.

**Open problem 3 — Governance of emergent multi-agent purpose.**
FalkorDB's graph traversal capabilities are directly applicable to population-level purpose tracking across agent chains. A purpose evolution graph representing agent-to-agent context propagation is a natural graph structure; FalkorDB's traversal performance makes real-time cross-chain purpose evaluation viable in a way that traditional graph databases would not support at agent scale.

---

### Licence and sovereignty assessment

FalkorDB is released under SSPLv1 (Server Side Public License v1). The practical implications are:

- Self-hosted deployments (where the customer runs FalkorDB on their own infrastructure) do not trigger SSPLv1's service provision clause. For the truc reference implementation's primary deployment model — single binary on customer-controlled infrastructure — SSPLv1 does not require open-sourcing any additional code.
- Hosted service deployments (where LGT.io or a customer operates FalkorDB as a service provided to other users) trigger SSPLv1's requirement to open-source the code that enables that service, or to obtain a commercial licence from FalkorDB Ltd.
- Commercial licences are available from FalkorDB Ltd for service provision contexts.

**Sovereignty assessment:** FalkorDB Ltd is incorporated in Israel. Israel is not subject to the US CLOUD Act. Self-hosted FalkorDB deployments create no compellable access risk for governance records held on customer infrastructure. The sovereignty constraint defined in this specification's README is satisfied for self-hosted deployments.

---

### What FalkorDB does not provide

A substrate review is only useful if it also identifies where the substrate does not address specification requirements.

- FalkorDB is not a governance system. Purpose compatibility assessment, reversibility classification, confidence thresholds, and escalation paths are Layer 3 concerns that the substrate does not address — these are implemented as graph operations in the reference implementation.
- FalkorDB does not provide the governed artifact format. The truc artifact format — with its Merkle integrity tree, multi-recipient cryptographic addressability, and post-quantum sealing — is independent of FalkorDB and is the LGT.io reference implementation's primary IP contribution.
- FalkorDB does not provide post-quantum cryptography. The PQ properties of the reference implementation are provided by liboqs (Open Quantum Safe project, Linux Foundation, MIT licence) via the truc artifact format construction.
- FalkorDB does not provide data lineage. Layer 1 remains the responsibility of the enterprise data substrate.
- FalkorDB's SSPLv1 licence requires a commercial licence for hosted service deployments. Implementations intending to offer FalkorDB as part of a managed service must account for this.

---

### Implications for the specification

This review does not change the specification's technology-agnostic posture. Any substrate providing equivalent capabilities — full openCypher over Bolt, GraphBLAS-based traversal performance, multi-tenancy, self-hostable sovereignty — satisfies the same requirements.

The review confirms that a production-quality, sovereignty-compliant graph engine substrate is available for implementations targeting the specification. The reference implementation's architecture decision records (github.com/lgt-io/truc) document the specific integration approach, licensing considerations, and design rationale for FalkorDB as the v0.2 substrate.

---

*Reviews are maintained in the order they are added. New reviews append to this document rather than replacing earlier ones. Where a subsequent review of the same technology is material, it is added as a dated entry alongside the earlier review, not as a replacement.*
