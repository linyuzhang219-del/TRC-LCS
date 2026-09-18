# Contributing to TRC-LCS

Contributions are welcome, especially small, reviewable changes that improve reproducibility or backend interoperability.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
python -m pip install -U pip
pip install -e ".[dev]"
pytest
```

## Pull requests

1. Open an issue first for substantial API or algorithm changes.
2. Keep PRs focused and include tests for behavior changes.
3. Do not add large datasets, model weights, or generated benchmark artifacts to Git.
4. Document new CLI flags and input formats.
5. Report the exact command used for any benchmark result.

## Good first contributions

- Dataset-format adapters.
- Additional unit tests and regression cases.
- Documentation fixes and minimal examples.
- Retrieval/verifier plugin interfaces.

## Research claims

Do not present synthetic-demo output as a real-world benchmark. Public-dataset results should identify the dataset split, trajectory source, camera setup, and exact configuration.
