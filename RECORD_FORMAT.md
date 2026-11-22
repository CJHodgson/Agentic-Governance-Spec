# Governed Artifact Record Format, version 2

**Status:** draft for review. **Applies to:** Layer 5 (audit integrity) of the Agentic Governance Layer specification.

This document describes the file that records governance decisions and the procedure that checks it, in enough detail for someone with no access to any existing implementation to write a verifier. It describes the format and the procedure only. It says nothing about how a decision is reached, how a file is stored or served, or how keys are kept.

All example values are synthetic. The machine-readable test vectors in [`test-vectors/record-format-v2.json`](test-vectors/record-format-v2.json) were produced by one implementation and reproduced by a second, independent one (see [Test vectors](#12-test-vectors)).

Contents: [1 Conventions](#1-conventions) · [2 The file](#2-the-file) · [3 Sections](#3-sections) · [4 Recipients and the content key](#4-recipients-and-the-content-key) · [5 Writer keys and signatures](#5-writer-keys-and-signatures) · [6 Integrity tree, version 2](#6-integrity-tree-version-2) · [7 The audit chain](#7-the-audit-chain) · [8 The decision record](#8-the-decision-record) · [9 Policy bundle and graph-data hashes](#9-policy-bundle-and-graph-data-hashes) · [10 Integrity modes and witnesses](#10-integrity-modes-and-witnesses) · [11 The verification procedure](#11-the-verification-procedure) · [12 Test vectors](#12-test-vectors) · [13 Versioning and what this document does not cover](#13-versioning-and-what-this-document-does-not-cover)

---

## 1. Conventions

* **Bytes and integers.** Where a hash input is built from fields, integers are big-endian and fixed width: `u32(n)` is 4 bytes, `u64(n)` is 8 bytes. `lp(b)` ("length-prefixed") is `u32(len(b)) || b`. `||` is concatenation. A string is its UTF-8 bytes.
* **Hash.** `SHA256(x)` is SHA-256 (FIPS 180-4). Every hash in this format is SHA-256. Digests are 32 bytes, written in lower-case hex wherever this document shows or compares text.
* **Domain strings.** Several hashes begin with a fixed ASCII string that keeps one use of a hash from being mistaken for another. They are literal values, reproduced exactly, and are opaque: they are not names to be looked up. Each appears in the section that uses it.
* **Enumerations** are given by number where a number is hashed, and by name in the JSON documents in the sections.
* **"Must" and "should".** *Must* is a requirement for a verifier to give a correct answer. *Should* is advice.

## 2. The file

A governed artifact is one file: the Protocol Buffers (proto3) binary encoding of the message `Artifact` below, with no header, trailer or framing around it. Field numbers are part of the format.

```proto
syntax = "proto3";

message Artifact {
  uint32          format_version        = 1;   // 2 for this document
  string          artifact_id           = 2;   // a UUID, lower-case, 8-4-4-4-12
  int64           created_at_unix_nanos = 3;
  IntegrityMode   integrity_mode        = 4;
  AlgorithmParams algorithm_params      = 5;
  bytes           audit_chain_head      = 6;   // empty when the chain has no entries
  repeated RecipientHeader recipients   = 7;
  IntegrityTree   integrity_tree        = 8;
  Signature       signature             = 9;   // the seal: signs integrity_tree.root_hash
  repeated Section sections             = 10;
}

enum IntegrityMode {
  INTEGRITY_MODE_UNSPECIFIED = 0;
  INTEGRITY_MODE_E = 1;   // embedded: the chain is signed and hash-linked
  INTEGRITY_MODE_H = 2;   // reserved
  INTEGRITY_MODE_W = 3;   // witnessed by write-once storage (section 10)
  INTEGRITY_MODE_P = 4;   // reserved
}

message AlgorithmParams {
  SignatureAlgorithm signature_algorithm = 1;
  KemAlgorithm       kem_algorithm       = 2;
  HashAlgorithm      hash_algorithm      = 3;
}
enum SignatureAlgorithm {
  SIGNATURE_ALGORITHM_UNSPECIFIED = 0;
  SIGNATURE_ALGORITHM_ML_DSA_65_ED25519_HYBRID = 1;   // the only algorithm defined for use
  SIGNATURE_ALGORITHM_SLH_DSA_SHA2_128S = 2;          // reserved
}
enum KemAlgorithm {
  KEM_ALGORITHM_UNSPECIFIED = 0;
  KEM_ALGORITHM_ML_KEM_768_X25519_HYBRID = 1;         // X-Wing, section 4
  KEM_ALGORITHM_STUB_X25519 = 255;                    // development only: an artifact naming it is never valid
}
enum HashAlgorithm {
  HASH_ALGORITHM_UNSPECIFIED = 0;
  HASH_ALGORITHM_SHA3_256 = 1;                        // reserved
  HASH_ALGORITHM_SHA256 = 2;                          // written by every writer
}

message RecipientHeader {
  string recipient_id                    = 1;   // a label, not checked
  bytes  recipient_public_key_fingerprint = 2;  // section 4
  bytes  ml_kem_ciphertext               = 3;   // 1088 bytes
  bytes  x25519_ephemeral_public_key     = 4;   // 32 bytes (the X25519 part of the KEM ciphertext)
  bytes  wrapped_content_key             = 5;   // section 4
  int64  added_at_unix_nanos             = 6;
}

message IntegrityTree {
  bytes root_hash                          = 1;
  repeated SectionHash     section_hashes      = 2;
  repeated HeaderFieldHash header_field_hashes = 3;
}
message SectionHash     { SectionType section_type = 1; bytes hash = 2; }
message HeaderFieldHash { string field = 1;             bytes hash = 2; }

message Signature {
  SignatureAlgorithm algorithm = 1;
  bytes pq_signature           = 2;   // ML-DSA-65, 3309 bytes
  bytes classical_signature    = 3;   // Ed25519, 64 bytes
  bytes signer_key_fingerprint = 4;   // section 5
}

enum SectionType {
  SECTION_TYPE_UNSPECIFIED = 0;
  SECTION_TYPE_GRAPH_DATA = 1;
  SECTION_TYPE_SYSTEM_REGISTRY = 2;      // reserved: not written by this version
  SECTION_TYPE_AUDIT_CHAIN = 3;
  SECTION_TYPE_ATTESTATION_CHAIN = 4;    // reserved
  SECTION_TYPE_METADATA = 5;
  SECTION_TYPE_POLICY_BUNDLE = 6;
  SECTION_TYPE_RESERVED_SEGMENT = 7;     // reserved
}
message Section {
  SectionType section_type    = 1;
  bytes       encrypted_payload = 2;   // ciphertext followed by the 16-byte GCM tag
  bytes       nonce             = 3;   // 12 bytes
  uint32      schema_version    = 4;   // 1
}
```

The messages that appear *inside* sections are in [section 3](#3-sections) and [section 7](#7-the-audit-chain).

**Version.** `format_version` must be 2. Version 1 files left `format_version`, `artifact_id` and `created_at_unix_nanos` outside the integrity seal; they are not accepted, and a verifier must not check them under a weaker rule.

**Sections present.** An artifact written under this version has exactly four sections: `GRAPH_DATA` (1), `AUDIT_CHAIN` (3), `METADATA` (5) and `POLICY_BUNDLE` (6). A writer produces at most one section of each type. The integrity tree orders sections by type only, so the order of two sections of one type is undefined: a verifier **must report a file with two sections of one type INVALID**, even when its integrity tree and seal are consistent. A verifier that cannot find a required section cannot verify the file and must not report it valid.

**Unrecognised content.** A field number that is not in the messages of this document, or an enum value that is not listed in them, is *unrecognised*. Protocol Buffers parsers skip such fields, and the integrity tree does not cover them, so a verifier cannot tell whether they were written by a newer version of the format or added afterwards. A verifier therefore **must not report a file with unrecognised content VALID, and must not report it INVALID on that ground alone**: it carries on with every check below on what it does recognise, and if nothing else fails the outcome is **NOT VERIFIED** (the file may be in a newer format than the verifier supports). The same applies to the JSON documents of section 3.2: a field in a section that is not in that section's message is unrecognised. (The decision record of section 8 is different: it gains optional fields without a change of schema, and unknown fields in it are ignored.)

## 3. Sections

### 3.1 Encryption

Each section's plaintext is encrypted with **AES-256-GCM** (NIST SP 800-38D) under the artifact's 32-byte *content key* (section 4), with the 12-byte `nonce` of that section, no additional authenticated data, and the standard 128-bit tag appended to the ciphertext. `encrypted_payload` is that ciphertext-and-tag. A nonce is never used twice under one content key. A section that does not decrypt (tag failure) is not an artifact that can be verified.

The integrity tree (section 6) hashes the **encrypted** form, so a file's integrity can be checked without the content key; reading the chain, the policy bundles and the metadata needs it.

### 3.2 Plaintext encoding

Each section's plaintext is the **JSON** form of a Protocol Buffers message, in the canonical Protobuf JSON mapping: field names in lower camel case (`prevHeadHash`), 64-bit integers as decimal **strings** (`"sequenceNumber":"1"`), `bytes` as standard base64 with padding, enums by name, fields at their default value omitted, any amount of white space between tokens. A reader should accept both the lower-camel and the original field names, must accept any white space, and must not rely on byte-for-byte identity of the JSON text: no hash in this format is taken over it. Hashes are taken over field *values*, as set out below.

| Section | Type | Message |
|---|---|---|
| `METADATA` | 5 | `Metadata` |
| `POLICY_BUNDLE` | 6 | `PolicyBundleSet` |
| `GRAPH_DATA` | 1 | `GraphData` |
| `AUDIT_CHAIN` | 3 | `AuditChain` (section 7) |

```proto
message Metadata {
  string content_schema_version = 1;          // "1"
  map<string, string> attributes = 2;
}
message PolicyBundleSet { repeated PolicyBundle bundles = 1; }
message PolicyBundle {
  bytes  bundle_hash             = 1;   // SHA-256 of bundle_data, 32 bytes
  bytes  bundle_data             = 2;   // the policy bundle, as bytes; its content is not interpreted here
  string version_label           = 3;
  int64  activated_at_unix_nanos = 4;
  int64  superseded_at_unix_nanos = 5;  // 0 while in force
}
message GraphData {
  repeated Node         nodes         = 1;
  repeated Relationship relationships = 2;
}
message Node {
  string node_id = 1;
  repeated string labels = 2;
  map<string, PropertyValue> properties = 3;
}
message Relationship {
  string relationship_id = 1;
  string type            = 2;
  string start_node_id   = 3;
  string end_node_id     = 4;
  map<string, PropertyValue> properties = 5;
}
message PropertyValue {
  oneof value {
    string       string_value = 1;
    int64        int_value    = 2;
    double       double_value = 3;
    bool         bool_value   = 4;
    bytes        bytes_value  = 5;
    PropertyList list_value   = 6;
  }
}
message PropertyList { repeated PropertyValue values = 1; }
```

`GRAPH_DATA` holds the reference data the decisions were made against (what a data set was collected for, where it may be held, and similar). Its meaning is defined by the layer that uses it; for this document it is a message that must hash as set out in [section 9](#9-policy-bundle-and-graph-data-hashes).

### 3.3 Metadata attributes

Two attribute keys have a defined meaning:

| Key | Value |
|---|---|
| `enrolled_signing_key_fingerprints` | The fingerprints (section 5) of the writer signing keys enrolled for this artifact: lower-case hex, comma-separated, no spaces. |
| `graph_data_history/<hex>` | A superseded `GRAPH_DATA` message: the standard base64 of its canonical encoding (section 9), where `<hex>` is the SHA-256 of those bytes. One attribute per superseded version. |

Other attributes are allowed and are ignored by a verifier (an attribute key is data, not a field of the message).

## 4. Recipients and the content key

The content key is a random 32-byte value made for one artifact. It is never stored in the clear: each recipient has a `RecipientHeader` holding the key encapsulated to that recipient. A verifier needs a recipient's private key to read the chain.

**Recipient key.** A recipient holds an **X-Wing** key pair (draft-connolly-cfrg-xwing-kem-09: ML-KEM-768 combined with X25519). The public key is 1216 bytes (`pk_M || pk_X`, 1184 and 32). The recipient fingerprint is

```
SHA256( "truc-recipient-key/X-Wing/" || public_key )
```

**Header.** `recipient_public_key_fingerprint` is that fingerprint. `ml_kem_ciphertext` (1088 bytes) and `x25519_ephemeral_public_key` (32 bytes) are the two parts of the X-Wing ciphertext (their concatenation is the draft's 1120-byte `ct`). The shared secret `ss` (32 bytes) is the draft's `Decapsulate(ct, sk)`.

**Unwrapping.** With `fp` the recipient fingerprint and `D = "lgt.io/truc/v1/content-key-wrap"`:

```
wrapping_key = HKDF-SHA256( ikm = ss, salt = (none), info = D || "/key/" || hex(fp), length = 32 )   # RFC 5869
aad          = D || "/aad/" || for each of fp, ml_kem_ciphertext, x25519_ephemeral_public_key, in that order:
                                  decimal(len) || ":" || bytes
wrapped_content_key = nonce(12) || AES-256-GCM-seal( wrapping_key, nonce, content_key, aad )   # 12 + 32 + 16 = 60 bytes
```

`decimal(len)` is the length in ASCII decimal digits; `hex(fp)` is lower case. HKDF with no salt uses a salt of 32 zero bytes (RFC 5869, section 2.2). Opening the header is the reverse: split off the 12-byte nonce, decrypt with the wrapping key and `aad`, and require 32 bytes of plaintext. A header that does not open under the recipient key is a failure to read the artifact.

**Consistency.** If `algorithm_params.kem_algorithm` is 1, every recipient header must carry a non-empty `ml_kem_ciphertext`; a header without one misstates the protection and makes the artifact invalid. Value 255 marks development use only; an artifact naming it is never valid. Value 0 is invalid, and a value not listed in section 2 is unrecognised content.

## 5. Writer keys and signatures

The writer signs with a **hybrid** key: an Ed25519 key (RFC 8032) and an ML-DSA-65 key (FIPS 204). A signature is valid only if **both** halves verify, over the same message. Neither half alone is accepted.

* Ed25519: public key 32 bytes, signature 64 bytes, the "pure" scheme with no context.
* ML-DSA-65: public key 1952 bytes, signature 3309 bytes, the pure `ML-DSA.Sign` interface with the **empty context string**.
* **Fingerprint** of a signing key: `SHA256( ed25519_public_key || ml_dsa_65_public_key )`, 32 bytes. It is what `Signature.signer_key_fingerprint` carries and what `enrolled_signing_key_fingerprints` lists.
* **Signature message.** A signature in the file signs one of two messages and nothing else: the 32-byte `integrity_tree.root_hash` (the seal, section 6), or the entry-signature message of section 7. The two are built differently, so one can never stand for the other.

**Trust anchor.** The verifier's trust in a signature comes from a writer public key it holds already, obtained from the writer by some other route. It does not come from the file. The file lists enrolled fingerprints (3.3), and a verifier requires that the key it holds is enrolled, but a file that names a key does not establish that the key is the right one.

A signature in the file is checked as follows: `signer_key_fingerprint` equals the fingerprint of the trust-anchor key; `Signature.algorithm` equals `algorithm_params.signature_algorithm` in the header and both are 1; then Ed25519 and ML-DSA-65 both verify over the message. A signature that carries no real signature (a development placeholder) is never valid.

For exchanging the trust anchor, one implementation uses a small JSON file; it is informative, and a verifier may take the keys in any form:

```json
{ "format": "truc-public-key/v1", "algorithm": "ML-DSA-65+Ed25519",
  "fingerprint": "<64 hex>", "ed25519": "<base64, 32 bytes>", "ml_dsa_65": "<base64, 1952 bytes>" }
```

## 6. Integrity tree, version 2

The tree makes any change to a section's encrypted bytes, or to a header field below, change a single 32-byte **root**, which the writer signs (the seal). It is recomputed from the file alone.

**Section hash.** For a section `s`:

```
H_s = SHA256( u32(section_type) || lp(nonce) || u32(schema_version) || lp(encrypted_payload) )
```

**Content root.** Sort the sections by `section_type`, ascending. The leaves are the `H_s` in that order. Combine leaves pairwise: `SHA256(left || right)`; when a level has an odd number of nodes, the last node is paired with **itself**; repeat on the results until one node remains. That node is the content root. With **no sections**, the content root is `SHA256("lgt.io/truc/v1/integrity-tree/empty-sections")`. With one section, the content root is that section's hash.

**Header fields.** Six header fields are covered, each hashed on its own, in this fixed order. With `DF = "lgt.io/truc/v2/integrity-tree/header-field"`:

```
F_name = SHA256( DF || lp(name) || lp(value) )
```

| # | name | value |
|---|---|---|
| 1 | `format_version` | `u32(format_version)` |
| 2 | `artifact_id` | the string's UTF-8 bytes |
| 3 | `created_at` | `u64(created_at_unix_nanos)` (the two's-complement bits of the signed value) |
| 4 | `integrity_mode` | `u32(integrity_mode)` |
| 5 | `algorithm_params` | `u32(signature_algorithm) || u32(kem_algorithm) || u32(hash_algorithm)` |
| 6 | `audit_chain_head` | the `audit_chain_head` bytes (empty for an empty chain) |

`header_hash = SHA256( F_1 || F_2 || F_3 || F_4 || F_5 || F_6 )`.

**Root.**

```
root_hash = SHA256( content_root || header_hash )
```

**What the file stores.** `integrity_tree.root_hash` is the root. `section_hashes` lists `(section_type, H_s)` for each section in ascending type order, and `header_field_hashes` lists the six `(name, F_name)` pairs in the order above. Only the root is signed. A verifier recomputes all three and requires them to be equal to the stored values: the per-item hashes are not signed, but a file whose stored per-item hashes differ from a recomputation has been altered. When the roots differ, the per-item hashes are a way to say which header field or section changed; they are advice, never proof.

**What the tree does not cover.** `recipients`, `integrity_tree` and `signature` are outside the tree (the first must be able to change when a recipient is added; the other two are its output). The seal signature covers the tree, and so the sections and the six fields, and nothing more.

**Worked example.** The vector file gives an artifact with four sections. Its header fields hash (in order) to `681ab620…`, `0273a78e…`, `3e4769e3…`, `920a241d…`, `22759af6…` and `737333ee…`. Its sections of types 1, 3, 5 and 6 hash to `3c673efd…`, `b8245b29…`, `f23c6388…` and `04d85142…`. The root is `121220ca013b7c4deec3d9147374894cdbcbbdcc9b41bf91b436f312e7e16fc1`. An artifact with the same header and no sections has a root of `cf291061cd1cabcfe52a6554728b7e8b03dee56a693eeeeaf19deeb87b16a1c2`.

## 7. The audit chain

The `AUDIT_CHAIN` section is the ordered record of decisions. Entries are appended and never rewritten; each commits to the one before it.

```proto
message AuditChain { repeated AuditChainEntry entries = 1; }

message AuditChainEntry {
  uint64          sequence_number        = 1;   // 1, 2, 3, ... with no gaps
  bytes           prev_head_hash         = 2;
  bytes           entry_hash             = 3;
  IntegrityMode   integrity_mode         = 4;
  int64           recorded_at_unix_nanos = 5;
  DecisionPayload decision               = 6;
  WitnessProof    witness_proof          = 7;   // outside entry_hash (section 10)
  ExecutionEvidence execution_evidence   = 8;   // outside entry_hash; not interpreted here
  Signature       signature              = 9;   // section 5
}
message DecisionPayload {
  oneof payload {
    bytes inline_decision           = 1;   // the decision record (section 8), JSON
    bytes graph_data_reference_hash = 2;   // a 32-byte reference; its meaning is outside this document
  }
}
message WitnessProof {
  oneof proof {
    TpmAttestation         tpm_attestation        = 1;   // reserved (mode H)
    WormReceipt            worm_receipt           = 2;   // mode W, section 10
    TransparencyLogProof   transparency_log_proof = 3;   // reserved (mode P)
  }
}
message WormReceipt {
  string object_version = 1;
  int64  retention_until_unix_nanos = 2;
  string lock_mode = 3;
  string storage_identity = 4;
  string bucket = 5;
  string object_key = 6;
  string etag = 7;
}
// TpmAttestation, TransparencyLogProof and ExecutionEvidence hold opaque bytes and are not part of verification in this version.
```

**Genesis head.** The `prev_head_hash` of entry 1 is

```
GENESIS = SHA256( "lgt.io/truc/v1/audit-chain/genesis" )
```

**Entry hash.** For entry `e`:

```
entry_hash = SHA256(
    u64(sequence_number) ||
    lp(prev_head_hash)   ||
    u32(integrity_mode)  ||
    u64(recorded_at_unix_nanos) ||
    D )
```

where `D` is `0x01 || lp(inline_decision)` for an inline decision, `0x02 || lp(graph_data_reference_hash)` for a reference, and the single byte `0x00` if neither is set (a verifier treats an entry with no decision as invalid). `witness_proof`, `execution_evidence` and `signature` are not in the entry hash, so a witness receipt or evidence can be attached after an entry is written without changing it.

**Links.** Entry `i` (counting from 1) must have `sequence_number = i`, `prev_head_hash` equal to the previous entry's `entry_hash` (`GENESIS` for entry 1), and an `entry_hash` equal to the recomputation above. Every break is reported, not only the first.

**Head.** The artifact header's `audit_chain_head` must be empty when the chain has no entries, and otherwise equal to the last entry's `entry_hash`. (The genesis head is never stored in the header.) The header field is under the seal, so a chain that was cut short, or a header whose head was removed, is caught here.

**Entry signature.** The writer signs, for each entry, the message

```
M_entry = "lgt.io/truc/v1/audit-chain/entry-signature" || lp(artifact_id) || entry_hash
```

so an entry signed for one artifact does not verify in another, even under the same key. Verify with the rule in section 5.

**Worked example.** The first entry in the vector file has sequence number 1, `prev_head_hash` = `GENESIS` = `9e2f687b…6a73`, mode 1, time `1767323051000000000` and a 402-byte inline decision. Its `entry_hash` is `c7500bb0ad5f5d3f2bbc2c0aa6534b56c6dc129a300c2a9029621e54a5e5cde4`. The second entry's `prev_head_hash` is that value; its own hash, `b1f206e7…f8a0`, is the artifact's `audit_chain_head`. A third entry in the vector uses the reference form (`0x02`) so that the hash of that form can be tested; no writer of this version produces it (see step 10 of the procedure).

## 8. The decision record

An `inline_decision` is a JSON document (UTF-8, any white space; the bytes are what the entry hash covers). It records one decision. The fields a verifier reads are `schema`, `agent_id`, `policy_bundle_sha256` and `graph_data_sha256`; the others are listed so the record can be read:

| Field | Meaning |
|---|---|
| `schema` | `"truc.decision/v2"` (current) or `"truc.decision/v1"` (read, no longer written). Any other value is invalid. |
| `agent_id` | The identity of the caller who proposed the action. **Required in v2, forbidden in v1.** A v1 record is read as written by the agent `"cli"`. |
| `decided_at` | RFC 3339, UTC, nanosecond precision. |
| `action_sha256` | SHA-256 (hex) of the proposed-action document exactly as received. |
| `action` | The proposed action in typed form, absent if the document was rejected. |
| `action_error`, `action_error_code`, `action_raw` | Why a document was rejected, a stable code for it, and the rejected bytes (base64, when small). |
| `context` | The information the decision was made on, or `null` when none could be assembled. Its content is defined by the layer that makes the decision. |
| `policy_bundle_sha256` | Hex SHA-256 of the policy bundle evaluated, or the literal `policy-bundle-unavailable` when none could be loaded. |
| `graph_data_sha256` | Hex SHA-256 of the `GRAPH_DATA` in force (section 9). |
| `verdict` | `ALLOW`, `ESCALATE` or `REFUSE`. |
| `reasons` | A list of strings. |

A verifier must ignore fields it does not know: records gain optional fields without a change of `schema`, and an older record never has them. It must not require the others to be present, other than as stated.

## 9. Policy bundle and graph-data hashes

**Policy bundle.** `bundle_hash` is `SHA256(bundle_data)`. Every `policy_bundle_sha256` a record names must be the hash of a bundle held in `POLICY_BUNDLE`, whose stored bytes hash to it, except the literal `policy-bundle-unavailable`. A bundle whose stored bytes do not hash to its `bundle_hash` is an error whether or not a record names it.

**Graph data: the canonical encoding.** `graph_data_sha256` is `SHA256` of the **canonical protobuf encoding** of the `GraphData` message in force. This is the one place where a verifier must *write* a protobuf, not read one, so the encoding is fixed here. It is the ordinary proto3 binary encoding with these rules:

1. Fields are written in ascending field-number order.
2. A field holding its default value is omitted (an empty string, `0`, `false`, an empty list, an unset message), **except** a field inside a `oneof`, which is written whenever it is set, even at its default: a `bool_value` of `false` is written, as the two bytes `0x20 0x00`.
3. Repeated scalar fields are not used here; repeated messages and strings are written one element at a time.
4. A `map` is written as a repeated entry message (`key` = field 1, `value` = field 2), the entries **sorted by key** in ascending order of the keys' UTF-8 bytes. A map entry is written even when its value is empty.
5. A nested message is written as a length-delimited field, its fields under the same rules.
6. Integers use the shortest varint; a negative `int64` is written as ten bytes (the two's-complement 64-bit value). A `double` is 8 bytes, little-endian IEEE 754. No unknown fields.

The vector file gives a small `GraphData` and its canonical bytes and hash (`6707450811ca60cef6821f5d7a72d5a4c2a4d43ebde907f49ee088a7c08c5718`), so these rules can be tested before they are relied on. A verifier built on a Protocol Buffers library with a *deterministic* serialisation option should check it against the vector: deterministic serialisation is not guaranteed to be the same across libraries.

**Resolving a recorded hash.** A record's `graph_data_sha256` resolves if it equals the hash of the artifact's current `GRAPH_DATA`, or if `METADATA` holds an attribute `graph_data_history/<that hash>` whose base64 decodes to bytes that hash to the same value. A history entry whose bytes do not hash to their key is an error.

**The current graph is tied to the last decision.** The `graph_data_sha256` of the **last** record must equal the hash of the current `GRAPH_DATA`, and must not be empty. Without this, an altered current graph would still appear to resolve through the earlier versions kept in the history.

## 10. Integrity modes and witnesses

**Mode E (1)** is the base mode: everything above, with the writer holding the signing key. It detects any change that is not accompanied by a consistent rewrite and re-signing of the whole chain, which a holder of the key could do. A mode E file proves integrity against everyone but the key holder.

**Mode W (3)** adds an external witness: after each entry, the entry's head is written to an S3-compatible bucket with Object Lock in **COMPLIANCE** mode, and the entry carries a receipt. A rewritten and re-signed chain then disagrees with the locked heads.

* **Head object.** Key: `<artifact_id>/<sequence, 20 decimal digits, zero-padded>-<entry_hash, hex>`. Content (JSON, at most 4096 bytes): `{"format":"truc-worm-head/v1","artifact_id":"…","sequence":N,"entry_hash":"<hex>"}`.
* **Receipt** (`WormReceipt`): `lock_mode` is `COMPLIANCE`; `bucket` and `object_key` name the object (the key as above); `object_version` is non-empty; `etag`, `retention_until_unix_nanos` and `storage_identity` describe it. Storage layout, credentials and the transport are outside this document.

For a mode W file the verifier does the following (it needs read access to the bucket; without it, mode W cannot be fully checked):

1. Every entry must be recorded under mode W (an entry under another mode inside a mode W file is a downgrade) and must carry a `WormReceipt`.
2. For each entry, fetch the object the receipt names at its version. Its content must name this `artifact_id`, this sequence number and this entry hash; its `etag` must equal the receipt's when both are present; its retention must be COMPLIANCE with a retain-until date. A matching head whose retain-until date has passed is **lapsed**: it still matches, but the store no longer guarantees it (see the outcome below).
3. List every head under the prefix `<artifact_id>/`. A sequence number with two different hashes is a fork. A sequence number greater than the chain's length is a truncation. Any locked head at all under a file that is *not* mode W is a downgrade.

Modes H and P are reserved: a verifier must not report a file in those modes valid.

## 11. The verification procedure

**Inputs:** the artifact file; the trust-anchor writer public key (section 5); a recipient private key (section 4); optionally, access to the witness store (section 10).

**Outcomes:**

* **VALID:** every check passed, all signatures are real, and, for a mode W file, the witness was consulted and every head is within its retention.
* **INVALID:** a check failed. The verifier names each failing item. Anything that shows the file was altered, truncated, has two sections of one type, or was not written by the trust-anchor key is invalid.
* **NOT VERIFIED:** nothing failed, but something could not be established: the file carries content this version does not define (section 2, "Unrecognised content": a newer format than the verifier supports), a mode W file with no witness available, a witnessed head whose retention has lapsed, a signature that is a development placeholder, or a development-only KEM. It is never reported as VALID.

An error that stops the procedure (a section that will not decrypt, a missing required section, a file that does not parse) is reported as a failure to verify, not as a verdict on the file; it is never VALID.

**Steps.** Each step uses only what the earlier ones have established.

1. **Parse** the file as `Artifact`. Require `format_version = 2`. Require at most one section of each type (a repeat is INVALID). Note any unrecognised content (section 2); it does not stop the procedure, and it makes the final outcome NOT VERIFIED unless a check fails.
2. **Integrity tree** (section 6). Require a stored tree. Recompute the root and compare it with `integrity_tree.root_hash`; if they differ, report INVALID, naming the header fields and sections whose stored per-item hash differs from the recomputation, and **stop**: no section can be trusted. Then require the stored `section_hashes` and `header_field_hashes` to equal the recomputation.
3. **Algorithm parameters** (section 4, "Consistency"): the KEM named in the header against the recipient headers.
4. **Open the content key**: find the recipient header whose fingerprint equals the supplied recipient key's, decapsulate and unwrap it. Decrypt the sections (3.1).
5. **Enrolment.** From `METADATA`, require that the trust-anchor fingerprint is listed in `enrolled_signing_key_fingerprints`.
6. **Seal signature.** Check `signature` over `integrity_tree.root_hash` (section 5).
7. **Chain.** Parse `AUDIT_CHAIN`. Check sequence, links and entry hashes (section 7), and the header's `audit_chain_head`. Check every entry's signature over `M_entry`. Report every failure, entry by entry.
8. **Witness** (section 10), for a mode W file, or whenever a witness store is supplied: with a store supplied, always look at what it holds under this `artifact_id`, whatever mode the file now claims.
9. **Policy bundles.** Every stored bundle's bytes must hash to its `bundle_hash` (section 9).
10. **Records.** For each entry, parse its inline decision (section 8) and require the schema rules (an entry that holds a reference instead of an inline record has no record to read, and fails this step); require its `policy_bundle_sha256` to resolve to a stored bundle (or be `policy-bundle-unavailable`); require its `graph_data_sha256` to resolve (section 9). Then apply the last-decision rule: the last record's `graph_data_sha256` is non-empty and equals the hash of the current `GRAPH_DATA`.

A verifier that stops at the first failure is conforming; one that reports every failure is more useful. The verdict is INVALID if any step failed, otherwise NOT VERIFIED if any outcome above was unresolved, otherwise VALID.

**Appending.** A writer adding an entry to an existing file should run this procedure first, with its own key as trust anchor, and refuse to append to a file that is not valid: an entry added to an altered chain would otherwise lend it credibility.

## 12. Test vectors

[`test-vectors/record-format-v2.json`](test-vectors/record-format-v2.json) is a complete synthetic artifact with every intermediate value written out. All names, identifiers, keys and decisions in it are made up, and its keys protect nothing. It contains:

* `artifact.file_base64`: the whole file (section 2), a mode E artifact with two entries, the four sections, one recipient and a valid seal. Under `artifact`, `content_key_hex` opens its sections, and `sections[]` gives every section's nonce, plaintext JSON and encrypted payload.
* `signing_key`: the Ed25519 and ML-DSA-65 public keys and the fingerprint (section 5). `artifact.seal_signature` and `artifact.entry_signatures` give both halves of the seal's and each entry's signature, and the message each signs, so a signature check can be tested on its own.
* `recipient`: an X-Wing key pair's seed and public key, the fingerprint (section 4), and a worked key wrapping (shared secret, ciphertext parts, wrapping key, additional data, nonce, wrapped key) that opens to `content_key_hex`.
* `artifact.header_field_hashes`, `artifact.section_hashes`, `artifact.integrity_root_hex`, and `empty_artifact` (a file with no sections): section 6.
* `chain`: the genesis head and three entries with their hashes and signature messages, the third using the reference form of a decision to test its hash (section 7); it is not in the artifact.
* `graph_data`: a canonical `GraphData` encoding and its hash (section 9).

* `cases`: the outcome each of four files must get under section 11 and why. `valid` is the artifact above. `duplicate-section` is a second file (`file_base64`) with a repeated `GRAPH_DATA` section, **re-sealed and re-signed so that its tree, seal and chain are all consistent**: the duplicate is the only fault, and the expected outcome is INVALID. `unknown-field` is the artifact above with one undefined field (number 99) appended to the `Artifact` message: nothing the tree covers changes, every check passes, and the expected outcome is **NOT VERIFIED**. `altered-section` flips one byte of the `GRAPH_DATA` payload: INVALID, by the integrity tree. A mutation is given as an operation on the first file (`append_hex`, `flip_byte_offset`).

Two checkers are included. Neither is part of the format.

* [`test-vectors/check_vectors.py`](test-vectors/check_vectors.py) recomputes everything above that is a hash, a message or a key derivation, from the file bytes and the rules in this document, using only the Python standard library. It also classifies each case by structure (a repeated section type or a root mismatch is INVALID; an undefined field with a matching root is NOT VERIFIED) and compares that with `expected_outcome`. It exits non-zero on any difference.
* [`test-vectors/check_crypto`](test-vectors/check_crypto) (Go 1.26 or later, standard library only) verifies the Ed25519 and ML-DSA-65 halves of the seal and entry signatures with the empty ML-DSA context, confirms that a changed message fails, unwraps the content key from the vector's shared secret and decrypts every section to the plaintext shown. Run it with `go run . ../record-format-v2.json` in that directory.

The values were first produced by one implementation (the signatures and the key encapsulation by its post-quantum library); both checkers were written from this document, in other languages and with other libraries, and agree. Not checked by them, and to be tested by a verifier against the vector with its own library: the X-Wing decapsulation that produces the shared secret (the recipient's seed, public key and ciphertext are given, and the X-Wing draft has its own vectors), the signature on the `duplicate-section` file's seal (it is a valid seal over its own tree, made with the same key), and parsing the protobuf `Artifact` from `file_base64` with a real Protocol Buffers library (the Python checker reads it with a hand-written reader).

## 13. Versioning and what this document does not cover

**Versioning.** `format_version` names the layout of the whole file and of the integrity tree: a change to any hash input in sections 6 and 7 is a new `format_version`, and the layouts for a shipped version never change. The decision record's `schema` is versioned separately and may gain optional fields without a new schema. A future format version may replace the `lgt.io/truc/...` domain-separation constants with neutral ones; a verifier selects the constants by `format_version`, so files already written are unaffected.

**Not covered here:**

* how a policy bundle is evaluated, or what `context` and `action` contain (a verifier checks that the record is intact and refers to material held in the file; it does not re-run the decision);
* how a decision is re-run from a record to confirm it comes out the same;
* key custody, rotation and revocation, beyond the enrolment list and the trust anchor;
* where files are kept, how they are served and how access to them is controlled;
* modes H and P, and the reserved sections.

Corrections and extensions are welcome through the process in [CONTRIBUTING.md](CONTRIBUTING.md).
