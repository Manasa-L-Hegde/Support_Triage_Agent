# Support Triage Agent

[![HackerRank](https://img.shields.io/badge/HackerRank-Verified-brightgreen?logo=hackerrank)](https://www.hackerrank.com)

A deterministic support triage system. It reads support tickets, classifies them, retrieves grounded documentation, decides whether to reply or escalate, and writes structured outputs for review.

## Overview

The system is built to be explainable, reproducible, and safe. Every decision is rule-based, so the same ticket always produces the same result.

## Architecture

Pipeline:
1. Classification - `classifier.py` detects `request_type` and `product_area`.
2. Retrieval - `retriever.py` searches the knowledge-base corpus for the best document.
3. Decision - `decision.py` chooses reply vs escalation using safety rules.
4. Response - `response.py` generates a concise, grounded reply.
5. Orchestration - `main.py` ties everything together and writes the batch outputs.

## Key Properties

- Deterministic: no randomness, no hidden model behavior.
- Corpus-grounded: replies are based only on retrieved documentation.
- Safety-first: high-risk or undocumented tickets escalate.
- Validated output: retrieved documents are checked against the detected product area before use.
- Clean schema: `output/output.csv` contains only the required columns.

## How It Avoids Hallucination

Responses are generated only from retrieved corpus text. If no reliable document is found, the ticket is escalated instead of inventing an answer.

## Escalation Logic

- Always escalate high-risk issues such as fraud, stolen access, unauthorized access, and hacking.
- Escalate when no relevant document is available.
- Prefer a safe reply when grounded documentation exists.

## Limitations

- Keyword-based retrieval can miss semantic matches, typos, and multi-intent requests.
- The system does not use embeddings or LLM reasoning.
- Very ambiguous tickets may still require human review.

## Run

From the project root:

```bash
python main.py
```

## Outputs

- `output/output.csv` - final triage results
- `output/log.txt` - structured execution log

## Example Output

Below are the first rows from `output/output.csv` showing the triage schema and example results:

```csv
status,product_area,response,justification,request_type
escalated,api,This issue requires further assistance and has been escalated to the support team.,"Escalated due to high-risk keywords, low confidence input, or lack of relevant support documentation",product_issue
replied,billing,"It appears to be a billing-related issue.\n\nHere’s what you can do:\nBilling and Subscription FAQ...",Replied using relevant support documentation retrieved from the corpus with sufficient keyword match,product_issue
replied,billing,"Here’s what you can do:\nBilling and Subscription FAQ...",Replied using relevant support documentation retrieved from the corpus with sufficient keyword match,bug
escalated,fraud,This issue requires further assistance and has been escalated to the support team.,"Escalated due to high-risk keywords, low confidence input, or lack of relevant support documentation",product_issue
```
