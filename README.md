# PayStream Webhook Signature Verifier — Coding RL Environment

A reproducible evaluation environment where an AI coding agent must debug a broken Flask webhook receiver. Valid PayStream events are rejected with HTTP 401 because HMAC verification uses re-serialized JSON instead of the raw request body.

## 1. What did you build?

A Dockerized Flask microservice plus an external pytest grader. The starting repo contains a realistic multi-file webhook integration with one subtle security bug. A reference solution and adversarial grader analysis are included.

## 2. What capability does it test?

Repository-level backend debugging: tracing HTTP handler → crypto helper → config, understanding third-party webhook signing contracts, and fixing verification without breaking idempotency or health checks.

## 3. Why is this useful for evaluating a coding agent?

Webhook signature bugs are common in production and require reasoning about byte-exact payloads, not just “calling HMAC.” Agents that patch superficially or hardcode bypasses are caught by formatting edge cases and invalid-signature tests.

## 4. How do we run the environment?

```bash
cd environment
docker build -t paystream-webhook .
docker run --rm -p 5000:5000 -e WEBHOOK_SECRET=dev-secret-key paystream-webhook
```

Local (no Docker):

```bash
cd environment/repo
pip install -r requirements.txt
set WEBHOOK_SECRET=dev-secret-key   # Windows
export WEBHOOK_SECRET=dev-secret-key  # Linux/macOS
python -m flask --app app.main run --port 5000
```

## 5. How do we run the reference solution?

```bash
pip install -r environment/repo/requirements.txt
pip install -r tests/requirements.txt

# Grade starting state (expect FAIL)
python scripts/run_grader.py

# Grade reference solution (expect PASS)
python scripts/run_grader.py --apply-solution
```

Or apply manually:

```bash
python scripts/apply_solution.py
python scripts/run_grader.py
```

## 6. How does the verifier work?

The grader (`tests/`) imports the agent's Flask app via `GRADER_REPO_ROOT`, spins up a test client, and sends signed HTTP requests. It independently computes HMAC-SHA256 over raw bytes (matching PayStream's contract) and asserts:

- 200 for valid signatures (multiple JSON formats)
- 401 for missing, wrong, or tampered signatures
- 400 for malformed payloads
- Idempotent payment totals for duplicate `event_id`
- Health endpoint still returns 200

## 7. What edge cases are covered?

- Pretty-printed JSON vs compact JSON
- Non-alphabetical JSON key order
- Tampered body with original signature
- Wrong shared secret
- Missing / malformed signature header
- Duplicate event idempotency (total must not double)
- Invalid JSON body
- Missing required payload fields

## 8. What grader exploits did you test?

See [analysis/grader_attacks.md](analysis/grader_attacks.md) — includes hardcoded verification bypass, weak header checks, re-serialize “fixes,” breaking idempotency, and external test tampering.

## 9. What happened when you ran an AI coding agent?

See [analysis/model_runs.md](analysis/model_runs.md). Reference solution passes all tests; starting state fails signature acceptance tests.

---

## Project layout

```
coding-rl-environment/
├── task/              # Agent-facing instruction + metadata
├── environment/       # Dockerfile + starting repo
├── solution/          # Reference fix
├── tests/             # External verifier (not visible to agent)
├── scripts/           # Grader runner + solution applier
├── analysis/          # Adversarial notes + model runs
└── README.md
```

## License / attribution

Original task and code authored for this assignment. Built with Python 3.11, Flask 3.x, pytest. No third-party repository code was copied.

## Submission summary (3–5 lines)

Built a Dockerized Flask PayStream webhook receiver RL environment. Agents must fix HMAC verification that incorrectly re-serializes JSON instead of verifying raw request bytes. Includes external pytest grader with tamper, idempotency, and formatting edge cases, plus reference solution and adversarial grader analysis. Starting state fails; reference solution passes.
