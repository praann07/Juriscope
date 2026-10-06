"""Measure how well Juriscope retrieves the right document and states the right facts.

Runs each question through the same LegalDocumentAssistant the API uses, against the
live Pinecone index. The script only reads from the index; it never uploads or deletes.

    python eval/run_eval.py

Writes a summary to eval/results.md. Scoring is keyword-based: it checks that the
expected facts appear in the answer, which is a useful proxy, not a human judgement.
If the language model service returns an error (for example a rate limit), the script
waits for the limit window to reset and retries, and it reports any question that still
fails as a service error rather than a wrong answer.
"""

import json
import sys
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

QUESTIONS_PATH = ROOT / "eval" / "questions.json"
RESULTS_PATH = ROOT / "eval" / "results.md"
PAUSE_SECONDS = 5          # gap between questions
RATE_WINDOW_SECONDS = 65   # a per-minute limit resets within about a minute
MAX_RETRIES = 3
SERVICE_ERROR_PREFIX = "An error occurred while processing your question"


def _cell(text: str) -> str:
    return text.replace("|", "/").replace("\n", " ")


def score_fact_question(item, answer, sources):
    cited = [s.get("source") for s in sources]
    source_hit = item["source"] in cited
    answer_lower = answer.lower()
    missing = [k for k in item["keywords"] if k.lower() not in answer_lower]
    detail = f"missing: {', '.join(missing)}" if missing else ""
    return {
        "source_hit": source_hit,
        "answer_hit": not missing,
        "detail": detail,
    }


def score_refusal_question(item, answer, refusal_phrases):
    answer_lower = answer.lower()
    refused = any(p in answer_lower for p in refusal_phrases)
    leaked = [w for w in item.get("forbidden", []) if w.lower() in answer_lower]
    if leaked:
        detail = f"answered instead of refusing: {', '.join(leaked)}"
    elif not refused:
        detail = "no refusal wording"
    else:
        detail = ""
    return {"refused": refused and not leaked, "detail": detail}


def main():
    from src.vector_store import VectorStore
    from src.chatbot import LegalDocumentAssistant

    spec = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    print("Loading the embedding model and index (first run can take a minute)...")
    vectorstore = VectorStore().load_index()

    def ask(question):
        """Ask one question, retrying after the rate-limit window if the service errors."""
        for attempt in range(MAX_RETRIES + 1):
            bot = LegalDocumentAssistant(vectorstore)  # fresh chat history per question
            answer, sources = bot.chat(question)
            if not answer.startswith(SERVICE_ERROR_PREFIX):
                return answer, sources, True
            if attempt < MAX_RETRIES:
                print(f"  service error; waiting {RATE_WINDOW_SECONDS}s before retry {attempt + 1}")
                time.sleep(RATE_WINDOW_SECONDS)
        return answer, sources, False

    fact_rows, refusal_rows = [], []
    for item in spec["questions"]:
        answer, sources, ok = ask(item["question"])
        if item.get("refusal"):
            if ok:
                result = score_refusal_question(item, answer, spec["refusal_phrases"])
                passed = result["refused"]
            else:
                result = {"refused": False, "detail": "service error after retries"}
                passed = False
            refusal_rows.append((item["question"], result, answer, ok))
        else:
            if ok:
                result = score_fact_question(item, answer, sources)
                passed = result["source_hit"] and result["answer_hit"]
            else:
                result = {"source_hit": False, "answer_hit": False, "detail": "service error after retries"}
                passed = False
            fact_rows.append((item["question"], item["source"], result, answer, ok))
        status = "PASS" if passed else ("ERROR" if not ok else "FAIL")
        print(f"[{status}] {item['question']}  {result.get('detail', '')}")
        time.sleep(PAUSE_SECONDS)

    fact_total = len(fact_rows)
    source_ok = sum(r["source_hit"] for _, _, r, _, _ in fact_rows)
    answer_ok = sum(r["answer_hit"] for _, _, r, _, _ in fact_rows)
    service_errors = sum(1 for *_, ok in fact_rows if not ok) + sum(1 for *_, ok in refusal_rows if not ok)
    refusal_total = len(refusal_rows)
    refusal_ok = sum(r["refused"] for _, r, _, _ in refusal_rows)

    lines = [
        "# Juriscope evaluation results",
        "",
        f"Run on {date.today().isoformat()} against the live `legal-rag` index.",
        "",
        "## Summary",
        "",
        f"- **Correct document cited:** {source_ok}/{fact_total} ({100 * source_ok / fact_total:.0f}%)",
        f"- **Expected facts in the answer:** {answer_ok}/{fact_total} ({100 * answer_ok / fact_total:.0f}%)",
        f"- **Refused out-of-scope questions:** {refusal_ok}/{refusal_total}",
        f"- **Questions that hit a service error even after retries:** {service_errors}",
        "",
        "Scoring is keyword-based: a fact question passes when the expected document is cited and every expected keyword appears in the answer.",
        "",
        "## Fact questions",
        "",
        "| Question | Expected source | Source cited | Facts present | Notes |",
        "|---|---|---|---|---|",
    ]
    for question, source, result, answer, ok in fact_rows:
        note = result["detail"]
        if ok and not result["answer_hit"]:
            note += f" | answer began: {_cell(answer[:160])}"
        lines.append(
            f"| {question} | {source} | {'yes' if result['source_hit'] else 'no'} | "
            f"{'yes' if result['answer_hit'] else 'no'} | {_cell(note)} |"
        )
    lines += ["", "## Out-of-scope questions", "", "| Question | Refused | Notes |", "|---|---|---|"]
    for question, result, answer, ok in refusal_rows:
        note = result["detail"]
        if ok and not result["refused"]:
            note += f" | answer began: {_cell(answer[:160])}"
        lines.append(f"| {question} | {'yes' if result['refused'] else 'no'} | {_cell(note)} |")
    lines += [
        "",
        "## Limits of this evaluation",
        "",
        f"- {fact_total} hand-written fact questions and {refusal_total} out-of-scope questions, all about one judgment. A score on this set does not prove accuracy in general.",
        "- Keyword matching checks that expected facts appear, not that the answer is well written or complete.",
        "- The language model runs on an account with a low per-minute output limit, so the script waits between questions and retries on errors.",
        "",
    ]
    RESULTS_PATH.write_text("\n".join(lines), encoding="utf-8")

    print()
    print(f"Correct document cited: {source_ok}/{fact_total}")
    print(f"Expected facts present: {answer_ok}/{fact_total}")
    print(f"Refused out-of-scope:   {refusal_ok}/{refusal_total}")
    print(f"Service errors after retries: {service_errors}")
    print(f"Wrote {RESULTS_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
