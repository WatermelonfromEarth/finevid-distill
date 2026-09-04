# Notebooks

Use notebooks only for development-set exploration. Test-set inspection before final configuration selection is outside the experiment contract.

- `01_inspect_finqa.ipynb` documents the raw FinQA schema and gold mappings.
- `02_colab_teacher.ipynb` runs the GPU-only Qwen cache and development quality gate from Google Drive.

Reusable logic remains in `src/`; the notebooks invoke those tested modules rather than copying model or metric implementations.
