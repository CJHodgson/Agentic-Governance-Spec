// Independent check of the signature, decryption and key-unwrapping parts of
// record-format-v2.json using only the Go standard library (crypto/mldsa,
// crypto/ed25519, crypto/aes, crypto/hkdf).
package main

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/ed25519"
	"crypto/hkdf"
	"crypto/mldsa"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"os"
)

func h(s string) []byte {
	b, err := hex.DecodeString(s)
	if err != nil {
		panic(err)
	}
	return b
}

func main() {
	var v map[string]any
	raw, _ := os.ReadFile(os.Args[1])
	if err := json.Unmarshal(raw, &v); err != nil {
		panic(err)
	}
	sk := v["signing_key"].(map[string]any)
	ed := h(sk["ed25519_public_hex"].(string))
	pk, err := mldsa.NewPublicKey(mldsa.MLDSA65(), h(sk["ml_dsa_65_public_hex"].(string)))
	if err != nil {
		panic(err)
	}
	a := v["artifact"].(map[string]any)
	check := func(name string, msg, pq, cl []byte) {
		e1 := mldsa.Verify(pk, msg, pq, nil)
		e2 := ed25519.Verify(ed, msg, cl)
		fmt.Printf("%-28s ML-DSA-65 %v  Ed25519 %v\n", name, e1 == nil, e2)
		if e1 != nil || !e2 {
			os.Exit(1)
		}
	}
	seal := a["seal_signature"].(map[string]any)
	check("seal", h(seal["message_hex"].(string)), h(seal["ml_dsa_65_signature_hex"].(string)), h(seal["ed25519_signature_hex"].(string)))
	entries := v["chain"].(map[string]any)["entries"].([]any)
	for i, es := range a["entry_signatures"].([]any) {
		m := es.(map[string]any)
		check(fmt.Sprintf("entry %d", i+1), h(entries[i].(map[string]any)["signed_message_hex"].(string)), h(m["ml_dsa_65_signature_hex"].(string)), h(m["ed25519_signature_hex"].(string)))
	}
	// a flipped message must fail
	bad := h(seal["message_hex"].(string))
	bad[0] ^= 1
	if mldsa.Verify(pk, bad, h(seal["ml_dsa_65_signature_hex"].(string)), nil) == nil {
		fmt.Println("tampered message verified!")
		os.Exit(1)
	}
	fmt.Println("tampered message rejected")

	// content key unwrap from the vector's shared secret
	w := v["recipient"].(map[string]any)["wrap_example"].(map[string]any)
	wrapped := h(w["wrapped_content_key_hex"].(string))
	wk, _ := hkdf.Key(sha256.New, h(w["shared_secret_hex"].(string)), nil,
		"lgt.io/truc/v1/content-key-wrap/key/"+v["recipient"].(map[string]any)["fingerprint_hex"].(string), 32)
	blk, _ := aes.NewCipher(wk)
	g, _ := cipher.NewGCM(blk)
	key, err := g.Open(nil, wrapped[:12], wrapped[12:], h(w["aad_hex"].(string)))
	if err != nil || hex.EncodeToString(key) != a["content_key_hex"].(string) {
		fmt.Println("unwrap failed", err)
		os.Exit(1)
	}
	fmt.Println("content key unwrapped")
	// decrypt every section and compare with the plaintext in the vector
	blk, _ = aes.NewCipher(key)
	g, _ = cipher.NewGCM(blk)
	for _, s := range a["sections"].([]any) {
		m := s.(map[string]any)
		pt, err := g.Open(nil, h(m["nonce_hex"].(string)), h(m["encrypted_payload_hex"].(string)), nil)
		if err != nil || string(pt) != m["plaintext_text"].(string) {
			fmt.Println("section decrypt failed", m["section_type"], err)
			os.Exit(1)
		}
		fmt.Printf("section type %v decrypts (%d bytes)\n", m["section_type"], len(pt))
	}
	fmt.Println("go stdlib check passed")
}
