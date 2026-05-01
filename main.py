"""
Support Triage Agent - Main Pipeline
=====================================

This script reads support tickets, classifies them, retrieves relevant support
material, decides whether to escalate, and writes safe structured output.

Run:
    python main.py

Input:
    support_tickets/support_tickets.csv if available,
    otherwise data/support_issues.csv

Output:
    output/output.csv
    output/log.txt
"""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from classifier import classify_request, detect_product_area
from decision import should_escalate
from retriever import load_corpus, retrieve_document
from response import generate_response


PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_ROOT / "output"
LOG_FILE = OUTPUT_DIR / "log.txt"
OUTPUT_FILE = OUTPUT_DIR / "output.csv"
CORPUS_DIR = PROJECT_ROOT / "knowledge_base"
INPUT_CSV_CANDIDATES = [
    PROJECT_ROOT / "support_tickets" / "support_tickets.csv",
    PROJECT_ROOT / "data" / "support_issues.csv",
]
OUTPUT_COLUMNS = ["status", "product_area", "response", "justification", "request_type"]
ESCALATED_JUSTIFICATION = (
    "Escalated due to high-risk keywords, low confidence input, or lack of relevant support documentation"
)
REPLIED_JUSTIFICATION = (
    "Replied using relevant support documentation retrieved from the corpus with sufficient keyword match"
)


def ensure_output_dir() -> None:
    """Create the output directory if it does not already exist."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def resolve_input_csv() -> Path:
    """Pick the first available support-ticket CSV from the known locations."""
    for candidate in INPUT_CSV_CANDIDATES:
        if candidate.exists():
            return candidate
    return INPUT_CSV_CANDIDATES[0]


def normalize_row(row: Dict[str, str]) -> Dict[str, str]:
    """Normalize CSV keys so the pipeline works with mixed header casing."""
    return {str(key).strip().lower(): (value or "").strip() for key, value in row.items()}


def load_tickets(csv_path: Path) -> List[Dict[str, str]]:
    """Load ticket rows from CSV and keep the raw data minimal and safe."""
    if not csv_path.exists():
        raise FileNotFoundError(f"Support ticket CSV not found: {csv_path}")

    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("Support ticket CSV is empty")
        return [normalize_row(row) for row in reader]


def get_issue_text(ticket: Dict[str, str]) -> str:
    """Combine subject and issue into one text block for downstream modules."""
    subject = ticket.get("subject", "").strip()
    issue = ticket.get("issue", "").strip()

    if subject and issue:
        return f"{subject}\n{issue}"
    return subject or issue


def build_justification(status: str) -> str:
    """Return the exact justification text expected in the output file."""
    return ESCALATED_JUSTIFICATION if status == "escalated" else REPLIED_JUSTIFICATION


def write_log_block(log_handle, lines: Iterable[str]) -> None:
    """Write a structured log block for one ticket."""
    block = "\n".join(lines) + "\n"
    log_handle.write(block)
    log_handle.flush()


def format_ticket_log(
    ticket_number: int,
    issue_text: str,
    request_type: str,
    product_area: str,
    doc: Optional[str],
    status: str,
    reasoning: str,
) -> List[str]:
    """Create a readable log block with separators for a single ticket."""
    retrieved_doc_label = "found" if doc else "not found"
    retrieved_doc_preview = "None" if doc is None else "Present"

    return [
        "=" * 72,
        f"Ticket {ticket_number}",
        "-" * 72,
        f"Input text: {issue_text if issue_text else '[empty issue text]'}",
        f"Classification: request_type={request_type}, product_area={product_area}",
        f"Retrieval result: {retrieved_doc_label} ({retrieved_doc_preview})",
        f"Final decision: {status}",
        f"Reasoning: {reasoning}",
        "=" * 72,
    ]


def process_tickets(tickets: List[Dict[str, str]], docs: List[str], log_handle) -> List[Dict[str, str]]:
    """Run the full triage pipeline for each ticket and return output rows."""
    results: List[Dict[str, str]] = []

    for ticket_number, ticket in enumerate(tickets, start=1):
        print(f"Processing ticket {ticket_number}...")

        issue_text = get_issue_text(ticket)
        # Domain awareness: use the optional `company` field to set a domain
        # value that can later be used for routing or filtering decisions.
        # We do not include `domain` in the CSV output per requirements.
        company = ticket.get("company", "None")
        if company != "None":
            domain = company
        else:
            domain = "General"
        request_type = classify_request(issue_text)
        product_area = detect_product_area(issue_text)
        retrieved_doc = retrieve_document(issue_text, docs)

        # Safety check: ensure retrieved doc mentions the product_area keyword
        # If not, drop the document to avoid incorrect grounding.
        if retrieved_doc and product_area:
            if product_area.lower() not in retrieved_doc.lower():
                retrieved_doc = None

        # Final validation layer: keep the answer grounded in the detected
        # product area so we do not return the wrong document for a ticket.
        if retrieved_doc:
            doc_lower = retrieved_doc.lower()
            if product_area == "api" and "api" not in doc_lower:
                retrieved_doc = None
            elif product_area == "billing" and "billing" not in doc_lower:
                retrieved_doc = None
            elif product_area == "authentication" and "password" not in doc_lower:
                retrieved_doc = None

        escalate = should_escalate(issue_text, retrieved_doc)
        status = "escalated" if escalate else "replied"
        response = generate_response(status, retrieved_doc, issue_text)
        justification = build_justification(status)

        if status == "escalated":
            reasoning = "Escalated because the issue was high-risk, too short, or had no relevant document."
        else:
            reasoning = "Replied because the issue matched the corpus and the response was grounded only in retrieved text."

        log_block = format_ticket_log(
            ticket_number=ticket_number,
            issue_text=issue_text,
            request_type=request_type,
            product_area=product_area,
            doc=retrieved_doc,
            status=status,
            reasoning=reasoning,
        )
        write_log_block(log_handle, log_block)

        results.append(
            {
                "status": status,
                "product_area": product_area,
                "response": response,
                "justification": justification,
                "request_type": request_type,
            }
        )

    return results


def save_results(results: List[Dict[str, str]], output_path: Path) -> None:
    """Write only the required columns to output.csv in a deterministic order."""
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(results)


def write_log_header(log_handle, input_csv: Path, corpus_dir: Path, ticket_count: int) -> None:
    """Write a short header describing the run."""
    lines = [
        "Support Triage Agent Execution Log",
        f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Input CSV: {input_csv}",
        f"Corpus directory: {corpus_dir}",
        f"Tickets loaded: {ticket_count}",
        "=" * 72,
    ]
    write_log_block(log_handle, lines)


def main() -> None:
    """Orchestrate loading, retrieval, decision, response generation, and output."""
    ensure_output_dir()
    input_csv = resolve_input_csv()

    try:
        tickets = load_tickets(input_csv)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}")
        return
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return

    corpus_docs = load_corpus(str(CORPUS_DIR))

    with LOG_FILE.open("w", encoding="utf-8") as log_handle:
        write_log_header(log_handle, input_csv, CORPUS_DIR, len(tickets))
        results = process_tickets(tickets, corpus_docs, log_handle)
        log_handle.write("\n" + "=" * 72 + "\n")
        log_handle.write(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_handle.write(f"Total tickets processed: {len(results)}\n")
        log_handle.write("=" * 72 + "\n")

    save_results(results, OUTPUT_FILE)
    print("Done. Output saved.")


if __name__ == "__main__":
    main()
