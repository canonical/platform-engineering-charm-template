# Copilot Instructions

## Project overview

This is a Juju Kubernetes sidecar charm template built with the [Ops framework](https://ops.readthedocs.io/). It deploys a workload container (`httpbin`) managed via Pebble, and is intended to be customised into a real charm.

## Commands

### Environment setup

```bash
uv python install
uv tool install tox --with tox-uv
uv sync --all-groups
source .venv/bin/activate
```

### Testing and linting

```bash
tox                        # runs lint, unit, static, coverage-report
tox -e fmt                 # auto-format with ruff
tox -e lint                # ruff + mypy + codespell
tox -e static              # bandit security scan
tox -e unit                # unit tests with coverage
tox -e integration         # integration tests (requires a live Juju model)
tox -e unit -- tests/unit/test_base.py::test_reconcile_on_pebble_ready  # single test
```

### Docs

```bash
make docs-check            # runs vale + lychee on docs
make vale                  # prose linting only
```

### Build and deploy

```bash
charmcraft pack            # build .charm file
juju add-model charm-dev
juju deploy ./<charm-name>.charm
```

## Architecture

All charm logic lives in `src/charm.py` as a single `Charm` class. The charm follows the **holistic reconciliation pattern**: every event handler (e.g. `_on_httpbin_pebble_ready`, `_on_config_changed`) delegates immediately to a single `reconcile()` method. `reconcile()` is idempotent and re-evaluates all state from scratch on every call — validate config, check Pebble connectivity, push layers, replan, set status.

Integration tests use [jubilant](https://jubilant.readthedocs.io/) as the Juju client. The `juju` fixture in `tests/integration/conftest.py` manages model lifecycle automatically (creates a temp model unless `--use-existing` or `--model` flags are passed).

The `terraform/` directory contains a Juju Terraform module that deploys the charm as an application — it is tested separately via `test_terraform_modules.yaml`.

## Key conventions

**Holistic reconciliation**: Do not write stateful delta-style event handlers. Add new event handlers only to trigger `reconcile()`; keep all state logic inside `reconcile()`.

**Unit tests**: Use `ops.testing.Context` + `ops.testing.State` (the Scenario testing API). Tests are structured with `arrange / act / assert` docstring sections. Test files live under `tests/unit/`.

**Copyright header**: Every Python file must start with:
```python
# Copyright <year> Canonical Ltd.
# See LICENSE file for licensing details.
```

**Docstrings**: Google style (`pydocstyle.convention = "google"`). Line length 99 chars.

**Ruff linters enabled**: `A, B, C, CPY, D, E, F, I, N, RUF, S, SIM, TC, UP, W`. Run `tox -e fmt` before committing.

**Commits**: Must be cryptographically signed. PRs are squash-merged onto `main`. Reference issue numbers in PR descriptions.

**AI contributions**: Disclose AI usage in the PR description. The [`copilot-collections`](https://github.com/canonical/copilot-collections) repo contains Canonical-specific quality standards that can be passed to AI tools to avoid common review issues.
