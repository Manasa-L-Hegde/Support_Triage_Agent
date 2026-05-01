# HackerRank Submission Checklist

Files for submission (upload these three on the HackerRank submission page):

- `code.zip` — a ZIP of the `code/` directory (exclude `data/` and `support_issues` files).
- `support_tickets/output.csv` — predictions CSV produced by the runner.
- `support_tickets/log.txt` — chat transcript / execution log.

Quick verification (run locally in project root):

```powershell
# show files and sizes
ls -File code.zip, support_tickets\output.csv, support_tickets\log.txt

# preview first 5 rows of predictions
python -c "import csv; print('\n'.join([','.join(row) for i,row in enumerate(csv.reader(open('support_tickets/output.csv', encoding='utf-8'))) if i<5]))"
```

Upload checklist for HackerRank UI:

1. Open the problem submission page.
2. Attach `code.zip` to the file upload field for code submission.
3. Attach `support_tickets/output.csv` to the predictions / output upload field.
4. Attach `support_tickets/log.txt` to the transcript / log upload field.
5. Provide any brief comments per the problem description and submit.

Notes:

- The `code.zip` contains the runnable pipeline under `code/`. To reproduce locally run:

```powershell
python code\main.py
```

- The predictions file uses the required columns and was generated from `data/support_issues.csv`.

If you want, I can also add this file to git and push it now (I will commit only this documentation file).
