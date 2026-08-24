# Testing

Local checks:

```bash
poetry run pre-commit run --all-files
poetry run pytest -m "not network"
poetry run sphinx-build -W -b html docs docs/_build/html
```

Validation with network:

```bash
poetry run pytest -m network
```

The network suite checks published output schemas and the upstream RSM contract.
