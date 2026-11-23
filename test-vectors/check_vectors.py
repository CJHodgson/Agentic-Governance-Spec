#!/usr/bin/env python3
"""Independent check of record-format-v2.json using only the Python standard library.
Recomputes every hash in the vectors from the described rules (not from any engine code)."""
import base64, hashlib, hmac, json, struct, sys

V = json.load(open(sys.argv[1]))
H = lambda b: hashlib.sha256(b).digest()
x = bytes.fromhex
fails = []
def eq(name, got, want):
    if got != want:
        fails.append(name); print("FAIL", name, "\n  got ", got.hex() if isinstance(got, bytes) else got, "\n  want", want.hex() if isinstance(want, bytes) else want)
    else:
        print("ok  ", name)

u32 = lambda n: struct.pack(">I", n)
u64 = lambda n: struct.pack(">Q", n)
lp = lambda b: u32(len(b)) + b

# ---- minimal protobuf reader (varint / length-delimited only) ----
def varint(b, i):
    n = s = 0
    while True:
        c = b[i]; i += 1; n |= (c & 0x7f) << s; s += 7
        if not c & 0x80: return n, i
def fields(b):
    i, out = 0, []
    while i < len(b):
        k, i = varint(b, i); f, w = k >> 3, k & 7
        if w == 0: v, i = varint(b, i)
        elif w == 2:
            n, i = varint(b, i); v = b[i:i+n]; i += n
        else: raise ValueError("wire type %d" % w)
        out.append((f, v))
    return out

A = V["artifact"]
raw = base64.b64decode(A["file_base64"])
top = fields(raw)
get = lambda f: [v for k, v in top if k == f]
fmt_v = get(1)[0]; art_id = get(2)[0].decode(); created = get(3)[0]
mode = get(4)[0] if get(4) else 0
ap = dict(fields(get(5)[0])); head = get(6)[0] if get(6) else b""
tree = dict((k, v) for k, v in fields(get(8)[0]) if k == 1)
secs = []
for sb in get(10):
    d = dict(fields(sb)); secs.append((d.get(1, 0), d.get(2, b""), d.get(3, b""), d.get(4, 0)))
eq("artifact_id", art_id.encode(), A["artifact_id"].encode())

# ---- section hashes and merkle root ----
secs.sort(key=lambda s: s[0])
leaves = [H(u32(t) + lp(n) + u32(sv) + lp(p)) for (t, p, n, sv) in secs]
for (t, *_), lf, want in zip(secs, leaves, A["section_hashes"]):
    eq("section hash type %d" % t, lf, x(want["hash_hex"]))
def merkle(ls):
    if not ls: return H(b"lgt.io/truc/v1/integrity-tree/empty-sections")
    while len(ls) > 1:
        ls = [H(ls[i] + (ls[i+1] if i+1 < len(ls) else ls[i])) for i in range(0, len(ls), 2)]
    return ls[0]
content_root = merkle(leaves)

# ---- header fields ----
domain = b"lgt.io/truc/v2/integrity-tree/header-field"
hf = [
 ("format_version", u32(fmt_v)), ("artifact_id", art_id.encode()), ("created_at", u64(created)),
 ("integrity_mode", u32(mode)),
 ("algorithm_params", u32(ap.get(1, 0)) + u32(ap.get(2, 0)) + u32(ap.get(3, 0))),
 ("audit_chain_head", head),
]
hhs = [H(domain + lp(n.encode()) + lp(v)) for n, v in hf]
for (n, _), h, want in zip(hf, hhs, A["header_field_hashes"]):
    eq("header field " + n, h, x(want["hash_hex"]))
header = H(b"".join(hhs))
root = H(content_root + header)
eq("integrity root", root, x(A["integrity_root_hex"]))
eq("root stored in file", tree[1], root)
_hf0 = [("format_version", u32(2)), ("artifact_id", A["artifact_id"].encode()), ("created_at", u64(A["created_at_unix_nanos"])),
        ("integrity_mode", u32(1)), ("algorithm_params", u32(1) + u32(1) + u32(2)), ("audit_chain_head", b"")]
_hh0 = H(b"".join(H(domain + lp(n.encode()) + lp(v)) for n, v in _hf0))
eq("empty-sections root", H(merkle([]) + _hh0), x(V["empty_artifact"]["integrity_root_hex"]))

# ---- chain ----
genesis = H(b"lgt.io/truc/v1/audit-chain/genesis")
eq("genesis head", genesis, x(V["chain"]["genesis_head_hex"]))
prev = genesis
for e in V["chain"]["entries"]:
    dec = x(e["decision_hex"])
    body = u64(e["sequence_number"]) + lp(x(e["prev_head_hash_hex"])) + u32(e["integrity_mode"]) + u64(e["recorded_at_unix_nanos"]) + bytes([e["decision_kind"]]) + lp(dec)
    eq("entry %d prev link" % e["sequence_number"], x(e["prev_head_hash_hex"]), prev)
    h = H(body)
    eq("entry %d hash" % e["sequence_number"], h, x(e["entry_hash_hex"]))
    eq("entry %d signed message" % e["sequence_number"],
       b"lgt.io/truc/v1/audit-chain/entry-signature" + lp(A["artifact_id"].encode())[0:0] + u32(len(A["artifact_id"])) + A["artifact_id"].encode() + h,
       x(e["signed_message_hex"]))
    prev = h
eq("audit_chain_head in header (entry 2)", head, x(V["chain"]["entries"][1]["entry_hash_hex"]))

# ---- resolutions (section 8.1): a second standalone chain, plus an unrecognised-schema entry ----
KNOWN_SCHEMAS = {"truc.decision/v1", "truc.decision/v2", "truc.resolution/v1"}
eq("resolutions genesis head", genesis, x(V["resolutions"]["genesis_head_hex"]))
prev = genesis
for e in V["resolutions"]["entries"]:
    dec = x(e["decision_hex"])
    body = u64(e["sequence_number"]) + lp(x(e["prev_head_hash_hex"])) + u32(e["integrity_mode"]) + u64(e["recorded_at_unix_nanos"]) + bytes([e["decision_kind"]]) + lp(dec)
    eq("resolution entry %d prev link" % e["sequence_number"], x(e["prev_head_hash_hex"]), prev)
    h = H(body)
    eq("resolution entry %d hash" % e["sequence_number"], h, x(e["entry_hash_hex"]))
    eq("resolution entry %d signed message" % e["sequence_number"],
       b"lgt.io/truc/v1/audit-chain/entry-signature" + lp(A["artifact_id"].encode()) + h,
       x(e["signed_message_hex"]))
    schema = json.loads(e["decision_text"])["schema"]
    outcome = "RECOGNIZED" if schema in KNOWN_SCHEMAS else "NOT VERIFIED"
    eq("resolution entry %d schema outcome (%s)" % (e["sequence_number"], schema), outcome, e["expected_schema_outcome"])
    prev = h

# ---- keys ----
sk = V["signing_key"]
eq("signing key fingerprint", H(x(sk["ed25519_public_hex"]) + x(sk["ml_dsa_65_public_hex"])), x(sk["fingerprint_hex"]))
r = V["recipient"]
eq("recipient fingerprint", H(b"truc-recipient-key/X-Wing/" + x(r["x_wing_public_key_hex"])), x(r["fingerprint_hex"]))

# ---- key wrap KDF and AAD (HKDF-SHA256, RFC 5869) ----
w = r["wrap_example"]
def hkdf(ikm, info, n):
    prk = hmac.new(b"\x00" * 32, ikm, hashlib.sha256).digest()
    okm, t = b"", b""
    i = 1
    while len(okm) < n:
        t = hmac.new(prk, t + info + bytes([i]), hashlib.sha256).digest(); okm += t; i += 1
    return okm[:n]
dom = "lgt.io/truc/v1/content-key-wrap"
fp = x(r["fingerprint_hex"])
eq("wrapping key", hkdf(x(w["shared_secret_hex"]), (dom + "/key/" + fp.hex()).encode(), 32), x(w["wrapping_key_hex"]))
aad = (dom + "/aad/").encode()
for f in (fp, x(w["ml_kem_ciphertext_hex"]), x(w["x25519_ciphertext_hex"])):
    aad += str(len(f)).encode() + b":" + f
eq("wrap aad", aad, x(w["aad_hex"]))
eq("wrapped key starts with nonce", x(w["wrapped_content_key_hex"])[:12], x(w["nonce_hex"]))
eq("wrapped key length (12 + 32 + 16)", len(x(w["wrapped_content_key_hex"])), 60)

# ---- policy bundle hash ----
eq("policy bundle sha256", H(x(A["policy_bundle_hex"])), x(A["policy_bundle_sha256_hex"]))

# ---- canonical GraphData encoding, written from the rules in the document ----
def tag(f, w): return bytes([(f << 3) | w])
def vi(n):
    out = b""
    while True:
        b = n & 0x7f; n >>= 7
        if n: out += bytes([b | 0x80])
        else: return out + bytes([b])
def ld(f, b): return tag(f, 2) + vi(len(b)) + b
def prop(v):
    if isinstance(v, str): return ld(1, v.encode())
    if isinstance(v, bool): return tag(4, 0) + vi(1 if v else 0) if v else tag(4, 0) + vi(0)  # oneof: present even when false
    if isinstance(v, int): return tag(2, 0) + vi(v & 0xFFFFFFFFFFFFFFFF)
def node(nid, labels, props):
    b = ld(1, nid.encode()) + b"".join(ld(2, l.encode()) for l in labels)
    for k in sorted(props, key=lambda s: s.encode()):
        b += ld(3, ld(1, k.encode()) + ld(2, prop(props[k])))
    return b
g = ld(1, node("dataset-0001", ["Dataset"], {"region": "UK", "age_days": 30, "special": False}))
eq("graph data canonical encoding", g, x(V["graph_data"]["deterministic_encoding_hex"]))
eq("graph data sha256", H(g), x(V["graph_data"]["sha256_hex"]))


# ---- outcome cases (document section 11): structure-level classification ----
def classify(raw):
    """What the structure alone decides: INVALID (tree mismatch or a repeated section type),
    NOT VERIFIED (a field this version does not define), else VALID so far. Signatures and
    decryption are checked by check_crypto, not here."""
    top = fields(raw)
    known = set(range(1, 11))
    unknown = sorted({k for k, _ in top if k not in known})
    g = lambda f: [v for k, v in top if k == f]
    secs = []
    for sb in g(10):
        d = dict(fields(sb)); secs.append((d.get(1, 0), d.get(2, b""), d.get(3, b""), d.get(4, 0)))
    types = [t for t, *_ in secs]
    dup = len(types) != len(set(types))
    secs.sort(key=lambda s: s[0])
    leaves = [H(u32(t) + lp(n) + u32(sv) + lp(p)) for (t, p, n, sv) in secs]
    ap = dict(fields(g(5)[0])); head = g(6)[0] if g(6) else b""
    art_id = g(2)[0]; hf = [("format_version", u32(g(1)[0])), ("artifact_id", art_id), ("created_at", u64(g(3)[0])),
        ("integrity_mode", u32(g(4)[0] if g(4) else 0)),
        ("algorithm_params", u32(ap.get(1, 0)) + u32(ap.get(2, 0)) + u32(ap.get(3, 0))), ("audit_chain_head", head)]
    hh = H(b"".join(H(domain + lp(n.encode()) + lp(v)) for n, v in hf))
    root_ok = H(merkle(leaves) + hh) == dict(fields(g(8)[0]))[1]
    if dup or not root_ok: return "INVALID", dict(duplicate=dup, root_matches=root_ok)
    if unknown: return "NOT VERIFIED", dict(unknown_fields=unknown)
    return "VALID", {}

for c in V["cases"]:
    if "file_base64" in c: data = base64.b64decode(c["file_base64"])
    else:
        data = bytearray(base64.b64decode(A["file_base64"]))
        m = c["mutation"]
        if m:
            if "append_hex" in m: data += x(m["append_hex"])
            if "flip_byte_offset" in m: data[m["flip_byte_offset"]] ^= 1
        data = bytes(data)
    got, why = classify(data)
    eq("case %s -> %s %s" % (c["id"], c["expected_outcome"], why), got, c["expected_outcome"])

print("\nFAILED: %s" % fails if fails else "\nall checks passed")
sys.exit(1 if fails else 0)
