"""Generate interview prep PDF for Downloads folder."""

from __future__ import annotations

from pathlib import Path

from fpdf import FPDF

OUTPUT = Path.home() / "Downloads" / "Coding-RL-Environment-Interview-Prep.pdf"


class PrepPDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(120, 120, 120)
            self.cell(0, 8, "PayStream Webhook RL Environment - Interview Prep", align="C")
            self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def section_title(self, title: str):
        self.ln(4)
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(20, 60, 120)
        self.multi_cell(0, 8, title)
        self.ln(2)

    def sub_title(self, title: str):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 7, title)
        self.ln(1)

    def body(self, text: str):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def code_block(self, text: str):
        self.set_font("Courier", "", 9)
        self.set_fill_color(245, 245, 245)
        self.set_text_color(20, 20, 20)
        for line in text.splitlines():
            self.cell(0, 5, "  " + line, ln=1, fill=True)
        self.ln(3)

    def bullet(self, text: str):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 5.5, f"- {text}")
        self.ln(1)


def build_pdf() -> Path:
    pdf = PrepPDF()
    pdf.set_margins(20, 20, 20)
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # Cover
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(20, 60, 120)
    pdf.cell(0, 12, "Coding RL Environment", ln=1)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Interview Preparation Guide", ln=1)
    pdf.ln(4)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(
        0,
        6,
        "PayStream Webhook Signature Verifier\n"
        "Synthium Labs Assignment\n"
        "GitHub: github.com/chakrinani/coding-rl-environment",
    )
    pdf.ln(8)

    pdf.section_title("1. One-Line Summary")
    pdf.body(
        "Built a reproducible coding RL environment where an AI agent must fix a Flask "
        "webhook service that rejects valid PayStream events because HMAC verification "
        "uses re-serialized JSON instead of the raw HTTP request body."
    )

    pdf.section_title("2. What You Built (Assignment Checklist)")
    for item in [
        "Realistic backend task (not LeetCode) - webhook HMAC bug",
        "task/instruction.md + task.yaml - agent-facing spec",
        "environment/Dockerfile + environment/repo/ - starting buggy codebase",
        "solution/ - reference fix (signature.py + webhooks.py)",
        "tests/ - external pytest grader (12 tests, not inside agent repo)",
        "analysis/grader_attacks.md - 10 adversarial attack scenarios",
        "analysis/model_runs.md - AI agent run documentation",
        "README.md - full documentation answering all 9 required questions",
        "Verified: starting state FAILS (4 failed), reference solution PASSES (12 passed)",
    ]:
        pdf.bullet(item)

    pdf.section_title("3. The Bug (Know This Cold)")
    pdf.sub_title("Root cause")
    pdf.body(
        "PayStream signs the RAW HTTP request body bytes using HMAC-SHA256. "
        "The buggy code in signature.py parses JSON into a Python dict, then re-serializes "
        "it with json.dumps() before computing HMAC. Re-serialization changes bytes "
        "(whitespace, key order), so valid signatures never match."
    )
    pdf.sub_title("Buggy code pattern")
    pdf.code_block(
        "body = json.dumps(payload, separators=(',', ':'))\n"
        "digest = hmac.new(secret.encode(), body.encode(), hashlib.sha256)"
    )
    pdf.sub_title("Correct fix")
    pdf.code_block(
        "raw_body = request.get_data()          # exact bytes PayStream signed\n"
        "payload = json.loads(raw_body)\n"
        "verify_signature(raw_body, header, secret)  # HMAC on raw bytes"
    )

    pdf.section_title("4. Project Structure")
    pdf.code_block(
        "coding-rl-environment/\n"
        "  task/           -> instruction.md, task.yaml\n"
        "  environment/    -> Dockerfile, repo/app/\n"
        "  solution/       -> fixed signature.py, webhooks.py\n"
        "  tests/          -> external grader (12 pytest tests)\n"
        "  scripts/        -> run_grader.py, apply_solution.py\n"
        "  analysis/       -> grader_attacks.md, model_runs.md\n"
        "  README.md"
    )

    pdf.section_title("5. How To Run (Live Demo Commands)")
    pdf.sub_title("Setup (once)")
    pdf.code_block(
        'cd "C:\\Users\\chakr\\OneDrive\\Desktop\\Assign\\coding-rl-environment"\n'
        "pip install -r environment/repo/requirements.txt -r tests/requirements.txt"
    )
    pdf.sub_title("Demo 1 - Buggy starting code (EXPECT FAIL)")
    pdf.code_block("python scripts/run_grader.py")
    pdf.body("Expected output: 4 failed, 8 passed")
    pdf.sub_title("Demo 2 - Reference solution (EXPECT PASS)")
    pdf.code_block("python scripts/run_grader.py --apply-solution")
    pdf.body("Expected output: 12 passed")
    pdf.sub_title("Optional - Run Flask app")
    pdf.code_block(
        "cd environment/repo\n"
        '$env:WEBHOOK_SECRET="dev-secret-key"\n'
        "python -m flask --app app.main run --port 5000\n"
        "Open: http://localhost:5000/health"
    )

    pdf.section_title("6. Why Run 1 Shows Red FAILED Lines")
    pdf.body(
        "Those are NOT errors in your submission. The grader intentionally tests broken "
        "code first. Failed tests mean valid webhooks return 401 - exactly the bug. "
        "Run 2 proves the fix works. In the interview say: "
        "'Starting state fails by design; reference solution passes all 12 tests.'"
    )

    pdf.section_title("7. Grader / Verifier (12 Tests)")
    pdf.sub_title("Valid signature tests (must return 200)")
    for item in [
        "Canonical JSON body",
        "Pretty-printed JSON (indent=2)",
        "Non-alphabetical key order in JSON",
    ]:
        pdf.bullet(item)
    pdf.sub_title("Invalid signature tests (must return 401)")
    for item in [
        "Missing signature header",
        "Wrong shared secret",
        "Tampered body with original signature",
        "Malformed signature header (sha256=000...0 bypass attempt)",
    ]:
        pdf.bullet(item)
    pdf.sub_title("Other behavior tests")
    for item in [
        "Health endpoint returns {\"status\": \"healthy\"}",
        "Duplicate event_id does not double-count payment total",
        "Invalid JSON returns 400",
        "Missing amount_cents returns 400",
    ]:
        pdf.bullet(item)

    pdf.section_title("8. Edge Cases Covered")
    for item in [
        "Pretty-printed vs compact JSON - catches re-serialize fixes",
        "Alternate JSON key order - catches sort_keys=True workarounds",
        "Tampered body - catches hardcoded verify_signature=True",
        "Idempotency - duplicate event_id must not increase total twice",
        "Health regression - /health must still work after fix",
    ]:
        pdf.bullet(item)

    pdf.section_title("9. Grader Attacks (Top 5 To Mention)")
    attacks = [
        "Hardcode verify_signature to return True -> caught by invalid sig + tamper tests",
        "Modify tests inside repo -> no effect, grader is external in tests/",
        "Fix only compact JSON with sort_keys -> fails pretty-print and key-order tests",
        "Break idempotency while fixing sigs -> duplicate total test fails",
        "Disable verification via env flag -> invalid signature tests still require 401",
    ]
    for a in attacks:
        pdf.bullet(a)

    pdf.section_title("10. Mock Interview Q&A")
    qa = [
        (
            "Q: What did you build?",
            "A: A coding RL environment - a Flask webhook service with a realistic HMAC "
            "bug, external pytest grader, reference solution, and adversarial analysis. "
            "An AI agent must fix signature verification without breaking idempotency.",
        ),
        (
            "Q: Why is this non-trivial?",
            "A: The bug is subtle - code looks like it verifies signatures, but re-serializing "
            "JSON changes the bytes. Agents that only test one JSON format miss the real fix.",
        ),
        (
            "Q: How do you know the agent succeeded?",
            "A: External grader sends signed HTTP requests. All 12 behavioral tests must pass. "
            "We grade outcomes, not specific implementation details.",
        ),
        (
            "Q: Why did run_grader.py show failures?",
            "A: That tests the starting buggy repo on purpose. Starting fails, solution passes. "
            "That proves the task is solvable and the grader works.",
        ),
        (
            "Q: Is there a deploy link?",
            "A: No - it is a reproducible local/Docker environment. Reviewers clone the repo "
            "and run python scripts/run_grader.py.",
        ),
        (
            "Q: What would an AI agent do wrong?",
            "A: Use json.dumps with sort_keys hoping it matches, hardcode True in verify, "
            "or fix signatures but break idempotency. All caught by the grader.",
        ),
        (
            "Q: Why keep the grader outside the repo?",
            "A: Prevents agents from modifying tests. Also matches real RL eval where "
            "verification is hidden from the agent.",
        ),
    ]
    for q, a in qa:
        pdf.sub_title(q)
        pdf.body(a)

    pdf.section_title("11. Key Files To Open During Interview")
    for item in [
        "environment/repo/app/signature.py - shows the bug",
        "solution/signature.py - shows the fix",
        "tests/test_webhook_grader.py - shows what grader checks",
        "analysis/grader_attacks.md - shows adversarial thinking",
        "task/instruction.md - what the agent sees",
    ]:
        pdf.bullet(item)

    pdf.section_title("12. Email Submission Template")
    pdf.code_block(
        "To: sangamesh@synthiumlabs.tech\n"
        "Subject: Coding RL Environment Assignment | Chakravarthi\n\n"
        "Full name: Chakravarthi\n"
        "Phone: [your phone number]\n"
        "GitHub: https://github.com/chakrinani/coding-rl-environment\n\n"
        "Summary:\n"
        "Built a Dockerized Flask PayStream webhook receiver RL environment.\n"
        "Agents must fix HMAC verification that incorrectly re-serializes JSON\n"
        "instead of verifying raw request bytes. Includes external pytest grader\n"
        "with tamper, idempotency, and formatting edge cases, plus reference\n"
        "solution and adversarial grader analysis. Starting state fails;\n"
        "reference solution passes."
    )

    pdf.section_title("13. Pre-Interview Checklist")
    for item in [
        "Run both grader commands successfully on your laptop",
        "Open GitHub repo in browser",
        "Know the bug: re-serialized JSON vs raw body bytes",
        "Know expected outputs: 4 failed then 12 passed",
        "Skim grader_attacks.md (at least 3 attacks)",
        "Send submission email if not done yet",
    ]:
        pdf.bullet(item)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(OUTPUT))
    return OUTPUT


if __name__ == "__main__":
    path = build_pdf()
    print(f"PDF saved to: {path}")
