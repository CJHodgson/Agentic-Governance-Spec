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
**Correction — 29 September 2026:** The June 2026 text of this review stated that FalkorDB exposes openCypher over the Bolt wire protocol, that Bolt-compatible client tooling works against it unchanged, and that it provides an in-process query surface. Those statements overstated the position. FalkorDB is a Redis module: it runs as a separate server process and its production query surface is the RESP command `GRAPH.QUERY`. It has had experimental Bolt support since version 4.0.0-a1 (November 2023), disabled by default, which FalkorDB documents as not recommended for production use (docs.falkordb.com/integration/bolt-support). The reference implementation therefore uses RESP. The affected passages are corrected in place below and marked; the reference implementation's ADR-005 carries the matching correction. New material arising from the re-review — the Redis dependency, durability, query semantics and resource bounds — is recorded in the dated entry *FalkorDB — September 2026 update* below.

---

### What FalkorDB is

FalkorDB is a high-performance graph database built on sparse matrix algebra (GraphBLAS) for graph representation. It executes graph traversals using linear algebra operations rather than pointer-chasing, providing order-of-magnitude performance advantages over traditional graph databases for the traversal patterns characteristic of governance decision context queries.

FalkorDB is the direct successor to RedisGraph following its end-of-life in January 2025. It executes the openCypher query language, submitted over RESP (the Redis serialisation protocol) via the `GRAPH.QUERY` command. FalkorDB also offers experimental, non-production Bolt support aimed at Neo4j driver compatibility. *(Corrected 29 September 2026: this sentence previously said FalkorDB exposes openCypher over Bolt and is addressable by Bolt client tooling without modification. That support exists only in experimental form.)*

For the purposes of the LGT.io reference implementation, FalkorDB serves as the query execution layer for the decision context graph. The truc artifact format (a protobuf-enveloped file with Merkle integrity tree and post-quantum cryptographic sealing) is the durable governance artifact. FalkorDB provides the query execution layer against the loaded graph, running as a separate, co-located process inside the customer's deployment unit. *(Corrected 29 September 2026: previously "in-process".)* The relationship is: truc owns the artifact; FalkorDB owns the query execution. When a truc artifact is opened, its graph content is loaded into FalkorDB; queries execute via openCypher; mutations are written back to the artifact on commit.

---

### Capability assessment against the specification

**Performance characteristics**

FalkorDB's sparse matrix algebra implementation provides performance characteristics well-suited to real-time governance decision evaluation:

- Query performance scaling: from approximately 20,000 QPS on a single node to 120,000 QPS on a six-node cluster
- Multi-tenancy: up to 10,000+ isolated graph instances per FalkorDB instance — relevant for multi-customer deployments
- Integrated vector indexing and full-text search alongside graph traversal in a single query surface
- Native GraphRAG implementation showing up to 5× query speed improvement over traditional RAG methods for context-retrieval workloads

These characteristics make FalkorDB viable as a pre-execution governance gate substrate — where query latency must be low enough that governance evaluation does not materially slow agent execution.

**openCypher and wire protocol**

The reference implementation's client-facing surface is specified as openCypher over Bolt 5.x with TLS 1.3 (ADR-005). FalkorDB does not provide that surface itself in production form: it accepts openCypher over RESP, and its Bolt listener is experimental. In truc, the Bolt surface is presented by truc's own server layer, which translates client queries into RESP `GRAPH.QUERY` calls against the bundled FalkorDB instance. The truc-to-FalkorDB connection is internal to the deployment unit and is not exposed to clients. Neo4j-compatible client tooling is intended to work against truc's Bolt surface, not against FalkorDB directly.

*(Corrected 29 September 2026: this passage previously stated that FalkorDB satisfies the Bolt requirement without adaptation and that Neo4j-compatible tooling works against FalkorDB unchanged. Neither holds for production use.)*

---

### How these capabilities map to the specification

**Layer 2 — Decision context.**
FalkorDB directly satisfies the Layer 2 architectural principle. The specification requires that the graph persist client-side, that the LLM or agent framework be stateless against it, and that the graph be the durable artifact capable of multiple verification passes. In the truc reference implementation, FalkorDB provides the query execution surface against the artifact's loaded graph content. Sessions are disposable; the artifact endures.

**Layer 3 — Governance primitive (validator mesh).**
FalkorDB's performance characteristics make real-time validation viable as a pre-execution gate rather than a post-hoc process. The governance primitives — purpose compatibility, reversibility classification, confidence threshold, escalation routing, circuit-breaker — are implemented as openCypher queries against the decision context graph in the reference implementation. FalkorDB is not itself a governance system; it is the substrate against which deterministic governance graph operations execute.

**Layer 4 — System contract registry.**
The system contract registry is graph content within the truc artifact. FalkorDB provides the query surface against that content — no additional capability is required. Registry entries inherit the artifact's integrity and portability properties.

**Layer 5 — Audit integrity (tamper-evident to tamper-proof).**
FalkorDB does not provide Layer 5 directly. In the truc reference implementation, the base tamper-evidence property is provided by the artifact format's file-format-native integrity tree, which collapses Layers 2 and 5 into a single artifact. The specification's full Layer 5 requirement — that integrity strength be a deployment-selectable property up to tamper-proof against the custodian — is addressed by a separate witnessing mechanism layered on top of the artifact format, independent of FalkorDB. FalkorDB is not involved in either property: tamper-evidence and external witnessing are both properties of the artifact format and its surrounding attestation layer, not the query engine.

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

- Self-hosted deployments (where the customer runs FalkorDB on their own infrastructure) do not trigger SSPLv1's service provision clause. For the truc reference implementation's primary deployment model — one self-contained deployment unit (the truc binary plus a bundled FalkorDB instance) on customer-controlled infrastructure — SSPLv1 does not require open-sourcing any additional code.
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

This review does not change the specification's technology-agnostic posture. Any substrate providing equivalent capabilities — full openCypher query execution (the client-facing wire protocol is the implementation's concern, not the substrate's), GraphBLAS-based traversal performance, multi-tenancy, self-hostable sovereignty — satisfies the same requirements.

The review confirms that a production-quality, sovereignty-compliant graph engine substrate is available for implementations targeting the specification. The reference implementation's architecture decision records (github.com/lgt-io/truc) document the specific integration approach, licensing considerations, and design rationale for FalkorDB as the v0.2 substrate.

---

## FalkorDB — September 2026 update

**Reviewed against:** Specification v0.1 (April 2026)
**Canonical sources:** docs.falkordb.com, github.com/FalkorDB/FalkorDB, redis.io/legal/licenses
**Status of review:** Update to the June 2026 review, following integration of FalkorDB (v4.20.7) into the reference implementation. Factual errors in the June entry are corrected in place above. This entry records material the June review did not cover. The June conclusion — that FalkorDB is a suitable, sovereignty-compliant substrate for self-hosted deployments — stands, with the qualifications below.

---

### Wire protocol

FalkorDB's production query surface is RESP (the Redis serialisation protocol): openCypher queries are submitted with the `GRAPH.QUERY` command. FalkorDB has offered experimental Bolt support since version 4.0.0-a1 (November 2023), aimed at compatibility with Neo4j drivers. It is disabled by default (`BOLT_PORT` = -1), and FalkorDB's documentation states that it is not recommended for production use. It can run alongside RESP on a separate port.

The reference implementation uses RESP between its own server layer and FalkorDB, and presents Bolt to its clients itself (ADR-005). FalkorDB's Bolt listener is left disabled.

**Relevance to the specification.** Any query entry point on the substrate that does not pass through the governance layer is a path by which an agent or client could read or change the decision context without validator-mesh evaluation. An enabled substrate-level Bolt listener would be such a path. See *Implications* below.

---

### Dependency on Redis

FalkorDB is a module loaded into a Redis server; it does not run without one. FalkorDB's official container images bundle Redis Open Source 8.x (the pinned version moved from 8.6.3 to 8.10.1 in September 2026). This dependency was not assessed in the June review. It has three consequences.

**Licensing.** A deployment carries two licence layers: FalkorDB (SSPLv1) and Redis Open Source 8.x, which Redis Ltd offers under a choice of RSALv2, SSPLv1 or AGPLv3. Redis versions up to 7.2 were BSD-licensed; 7.4 moved to RSALv2/SSPLv1 (2024); 8.0 added AGPLv3 (2025). For customer self-hosted deployments this is not expected to impose obligations beyond those already noted for FalkorDB. For hosted service deployments, both layers must be assessed — a FalkorDB commercial licence alone may not be sufficient. Implementors should take their own legal advice. The Redis licence has changed twice in two years; implementors should track it as a dependency risk.

**Sovereignty.** Redis Ltd is headquartered in San Francisco, with research and development in Tel Aviv. In a customer self-hosted deployment, Redis runs as open-source code on customer infrastructure, with no runtime connection to any Redis Ltd service and no Redis Ltd custody of data, so there is no compellable-access path to the governance record through Redis Ltd. The component's copyright holder is, however, US-headquartered. The sovereignty constraint in the README is written in terms of the substrate's domicile and does not distinguish between a vendor that operates a service and the copyright holder of open-source code running on customer infrastructure. See *Implications* below.

**Alternatives.** Valkey (Linux Foundation, BSD licence) is the principal Redis-compatible alternative. FalkorDB does not document Valkey compatibility at the date of this review.

---

### Durability, availability and resource bounds

- **Memory residency and durability.** FalkorDB holds graphs in memory. Persistence uses Redis mechanisms: RDB snapshots and the append-only file (AOF). With the recommended `appendfsync everysec`, up to one second of writes can be lost on failure.
- **Replication and failover.** Replication is asynchronous from a single write primary. Replicas are read-only and do not promote automatically without Redis Sentinel or a cluster configuration.
- **Resource bounds.** The per-query memory limit (`QUERY_MEM_CAPACITY`) and result-set size are unlimited by default, and query timeouts apply only as configured (`TIMEOUT_DEFAULT`, `TIMEOUT_MAX`).

**Relevance to the specification.** These characteristics are acceptable where the substrate holds a working copy of the decision context and the governed artifact is the durable record, as in the reference implementation: a substrate failure means the working set is reloaded from the artifact, and no governance record is lost. This clarifies the June review's Layer 2 mapping — the requirement that *the graph be the durable artifact* is met by the artifact format, not by FalkorDB. A pre-execution governance gate also needs bounded evaluation time; implementations should configure timeouts and memory limits and treat an exceeded bound as a refusal or escalation, not a pass.

---

### Query semantics relevant to Layer 3

FalkorDB implements a subset of openCypher and documents known limitations. Three bear directly on validator-mesh queries:

- **Unnamed relationships.** When a relationship in a `MATCH` pattern is not referenced elsewhere in the query, FalkorDB only verifies that at least one matching relationship exists, rather than matching each one. Counts over such patterns can be wrong. A validator that counts (for example, approvals or prior escalations) must name every relationship it matches.
- **`LIMIT` and eager operations.** `LIMIT` does not bound eager operations (`CREATE`, `SET`, `DELETE`, `MERGE`, aggregations), which execute in full before the limit applies.
- **Index use.** Indexes do not serve not-equal (`<>`) filters.

Neo4j-specific syntax and procedures are not available. Validator queries should be written against FalkorDB's documented openCypher support.

---

### Determinism and replay

FalkorDB executes queries using a multi-threaded engine (a thread pool, and OpenMP parallelism within GraphBLAS operations). Where a specification-compliant implementation relies on deterministic replay of governance evaluations, it should not depend on result ordering without an explicit `ORDER BY`, and should record the exact substrate version (FalkorDB and Redis) as part of the evaluation evidence.

---

### Performance figures

The performance figures in the June review (query throughput scaling, multi-tenancy limits, GraphRAG speed-up) are vendor-published and have not been independently measured for this review. The reference implementation's v0.2 definition of done includes an empirical latency measurement of the validator mesh; external performance claims should rest on that measurement.

---

### Implications for the specification

The June conclusion on technology-agnosticism stands. This update identifies two requirements that the specification leaves implicit and that are candidates for the next specification revision:

1. **No bypass path.** A compliant implementation should ensure that the decision context can be read or modified only through the governance layer — the substrate should expose no query entry point (such as an enabled substrate-level Bolt listener, or a network-reachable RESP port) that bypasses validator-mesh evaluation.
2. **Sovereignty of open-source components.** The sovereignty constraint should state how it applies to open-source components running on customer infrastructure whose copyright holder is domiciled in a CLOUD Act jurisdiction, as distinct from vendor-operated services and data custodians.

---

*Reviews are maintained in the order they are added. New reviews append to this document rather than replacing earlier ones. Where a subsequent review of the same technology is material, it is added as a dated entry alongside the earlier review, not as a replacement.*
