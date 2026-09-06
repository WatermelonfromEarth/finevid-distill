# Notebooks

Use notebooks only for development-set exploration. Test-set inspection before final configuration selection is outside the experiment contract.

- `01_inspect_finqa.ipynb` documents the raw FinQA schema and gold mappings.
- `02_colab_teacher.ipynb` runs the GPU-only Qwen cache and development quality gate from Google Drive.
- `03_colab_hard_label.ipynb` records the earlier temperature-1 workflow; keep its completed checkpoints as historical results.
- `04_colab_distilled.ipynb` is the current entry point. Upload the portable source bundle, then train the matched-temperature hard-label control and distilled student on GPU, verify their development comparison, and download the run records.
- `05_colab_final_evaluation.ipynb` validates the frozen selection, caches test teacher scores, runs the six-model final comparison, and benchmarks efficiency.
- `06_colab_error_analysis.ipynb` reproduces four model rankings and creates the deterministic post-test failure-review packet.

Reusable logic remains in `src/`; the notebooks invoke those tested modules rather than copying model or metric implementations.
