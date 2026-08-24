# Testing

Local checks:

```bash
poetry run ruff check .
poetry run ruff format --check .
poetry run pytest -m "not network"
poetry run sphinx-build -W -b html docs docs/_build/html
```

Validation with network:

```bash
poetry run pytest -m network
```

The network suite checks published output schemas and the external context contract separately from
ordinary rendering tests.
