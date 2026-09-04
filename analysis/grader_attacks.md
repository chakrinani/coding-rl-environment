# Attack attempted → What happened → How you fixed/prevented it

## 1. Hardcode `verify_signature` to always return True

**Attack:** Change `signature.py` so every request passes verification regardless of header value.

**What happened:** `test_rejects_hardcoded_bypass_with_invalid_signature` and `test_rejects_tampered_body` still fail the submission because requests with `sha256=000...0` or tampered bodies return 200.

**Fix/prevention:** Grader sends multiple invalid-signature cases that must return 401, not just one happy-path check.

---

## 2. Modify the external grader tests inside the repo

**Attack:** Agent adds or overwrites test files in the repository to force a pass.

**What happened:** No effect — the verifier lives in `tests/` outside the agent workspace. The agent is told not to modify tests, and the grader is not shipped inside `environment/repo/`.

**Fix/prevention:** Keep verifier external to the repo the agent edits.

---

## 3. Disable verification behind an environment flag

**Attack:** Add `SKIP_WEBHOOK_VERIFY=1` and bypass HMAC checks in development.

**What happened:** Grader always sets `WEBHOOK_SECRET` and sends invalid signatures; bypass would still need to accept bad sigs → caught by invalid-signature tests.

**Fix/prevention:** Tests explicitly require 401 for wrong/tampered/missing signatures.

---

## 4. Accept any signature starting with `sha256=`

**Attack:** Weak parsing — treat any well-formed header as valid without computing HMAC.

**What happened:** `test_rejects_hardcoded_bypass_with_invalid_signature` uses a syntactically valid but incorrect digest and expects 401.

**Fix/prevention:** Use a randomly wrong 64-char hex digest in the bypass test.

---

## 5. Fix only the happy path (compact JSON) but still re-serialize

**Attack:** Agent switches to `json.dumps(payload, sort_keys=True)` hoping it matches the provider.

**What happened:** `test_accepts_pretty_printed_json_body` and `test_accepts_key_order_different_from_alphabetical` fail because the signed raw bytes differ from any re-serialized dict.

**Fix/prevention:** Grader signs exact raw byte strings with alternate formatting and key order.

---

## 6. Break idempotency while fixing signatures

**Attack:** Rewrite webhook handler and accidentally process duplicate `event_id` values twice.

**What happened:** `test_duplicate_event_does_not_double_count` fails — payment total becomes 600 instead of 300.

**Fix/prevention:** Idempotency test asserts stored total, not just HTTP status codes.

---

## 7. Break `/health` while editing webhook code

**Attack:** Refactor `main.py` and remove or rename the health route.

**What happened:** `test_health_returns_healthy` fails.

**Fix/prevention:** Explicit regression test for unchanged health endpoint.

---

## 8. Return 200 with empty body without verifying

**Attack:** Skip verification but return 401 only when header is missing; ignore invalid values.

**What happened:** Invalid header test and tamper test catch this.

**Fix/prevention:** Separate tests for missing header vs wrong header vs tampered body.

---

## 9. Valid alternative implementation rejected?

**Attack concern:** Agent reimplements verification inline in `webhooks.py` instead of editing `signature.py`.

**What happened:** Grader is outcome-based (HTTP status + JSON fields + store totals). Any correct implementation passes.

**Fix/prevention:** No assertions on function names, file paths, or internal call structure — only behavior.

---

## 10. Use timing side channels or logging secret

**Attack:** Log computed expected signature on failure for hidden test introspection.

**What happened:** Not applicable to automated grader — tests only observe HTTP responses and app state.

**Fix/prevention:** Grader never exposes expected signatures; uses independent HMAC computation in test helpers only.
