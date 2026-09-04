# Processed ranking data

`train.jsonl`, `dev.jsonl`, and `test.jsonl` are deterministic evidence-ranking pools built from the corresponding pinned official FinQA splits. Each line contains one question, all prose sentences and table rows from its report, and the candidate IDs mapped from `qa.gold_inds`.

Regenerate all three files from the repository root with:

```powershell
python src/data/build_dataset.py --seed 42
```

The validator byte-compares these files with a fresh seed-42 build. Raw source data remains ignored.

Milestone 7 additionally creates `teacher_dev_scores.jsonl` and `teacher_train_scores.jsonl` in the persistent Google Drive artifact directory on a GPU runtime. They are generated artifacts and are not committed to Git. Each line stores candidate IDs in processed order and finite raw Qwen logit differences before any temperature transformation. The cache command validates every row before finalizing the file.
