# Contributing

Thanks for working on this.

## Setup

Use Python 3.14 and Poetry.

```bash
poetry install --with dev,docs
```

Before opening a pull request, run what CI runs:

```bash
poetry run ruff check .
poetry run ruff format --check .
poetry run pytest -m "not network"
poetry run sphinx-build -W -b html docs docs/_build/html
```

Those map to `lint.yml` (the first three), `test.yml`, and `docs.yml`. `publish.yml`
runs only on a published release.
Network-backed contract and output-schema tests are run separately in CI.

## Reporting problems

Open an issue at [LUMC-DCC/rs-files-templates/issues](https://github.com/LUMC-DCC/rs-files-templates/issues).