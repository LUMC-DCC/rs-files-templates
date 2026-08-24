# Contributing

Thanks for working on this.

## Setup

Use Python 3.14 and Poetry.

```bash
poetry install --with dev,docs
poetry run pre-commit install
```

Before opening a pull request, run the hooks and the remaining CI checks:

```bash
poetry run pre-commit run --all-files
poetry run pytest -m "not network"
poetry run sphinx-build -W -b html docs docs/_build/html
```

These correspond to `lint.yml`, `test.yml`, and `docs.yml`. `publish.yml` runs only
for a published release. CI runs network-backed contract and output-schema tests in
a separate job.

## Reporting problems

Open an issue at [LUMC-DCC/rs-files-templates/issues](https://github.com/LUMC-DCC/rs-files-templates/issues).
