# classmark — CAPCO classification-banner library (PLACEHOLDERS ONLY)

[![CI](https://github.com/cognis-digital/classmark/workflows/CI/badge.svg)](https://github.com/cognis-digital/classmark/actions)
[![Classification](https://img.shields.io/badge/classification-UNCLASSIFIED-green.svg)](./UPSTREAM.md)

> Build CAPCO-shape banner + portion marks. Validate *shape*, not content. Operators supply real values at runtime.

<!-- cognis:layman:start -->
## What is this?

classmark is a command-line tool that checks documents for correct classification markings — the kind used in government and military settings to label how sensitive a file is. You point it at a folder or file and it tells you if any documents are missing a classification banner, have inconsistent banners, or contain portion marks that are formatted incorrectly. It is designed for teams who need to verify that documents follow CAPCO (the U.S. government's standard for classification markings) before sharing or publishing them — without requiring the tool itself to contain any real classified content.
<!-- cognis:layman:end -->

## Upstream

Forks / wraps **(original)**. See [`UPSTREAM.md`](./UPSTREAM.md) for the
licensing posture, supported commits, and how to upgrade.

## What this adds for military / IC use

- ClassificationBanner builder (level/SCI/SAP/dissem/CUI)
- Portion-mark shape validator
- Banner-line scanner for `.txt`/`.md`/`.html`/`.docx`/`.json`
- Operator-supplied content only — no real markings shipped

<!-- cognis:install:start -->
## Install

`classmark` is source-available (not published to PyPI) — every method below installs
straight from GitHub. Pick whichever you prefer; the one-line scripts auto-detect
the best tool available on your machine.

**One-liner (Linux / macOS):**
```sh
curl -fsSL https://raw.githubusercontent.com/cognis-digital/classmark/HEAD/install.sh | sh
```

**One-liner (Windows PowerShell):**
```powershell
irm https://raw.githubusercontent.com/cognis-digital/classmark/HEAD/install.ps1 | iex
```

**Or install manually — any one of:**
```sh
pipx install "git+https://github.com/cognis-digital/classmark.git"     # isolated (recommended)
uv tool install "git+https://github.com/cognis-digital/classmark.git"  # uv
pip install "git+https://github.com/cognis-digital/classmark.git"      # pip
```

**From source:**
```sh
git clone https://github.com/cognis-digital/classmark.git
cd classmark && pip install .
```

Then run:
```sh
classmark --help
```
<!-- cognis:install:end -->

## Install

```bash
# Shared library (only once for the whole ecosystem):
pip install -e ../../shared

# This tool:
pip install -e .
```

## Demo

```bash
classmark demos/
```

Outputs are available in five formats — all respect an operator-supplied
classification banner (passed via `--classification`):

```bash
classmark <target> --format=console     # default
classmark <target> --format=json
classmark <target> --format=sarif       # for code-scanning pipelines
classmark <target> --format=markdown    # for PRs / briefings
classmark <target> --format=oscal       # OSCAL Assessment Results skeleton
```

## Classification banner

All output is wrapped with an operator-supplied classification banner.
**Default**: `UNCLASSIFIED//FOR PUBLIC RELEASE`.

> ⚠️ This tool **does not** generate or validate the *content* of higher
> classifications. Operators on cleared systems supply real markings at runtime.
> See [`../shared/cognis_mil/classmark.py`](../../shared/cognis_mil/classmark.py).

## Compliance crosswalks (built in)

Every finding can carry references to:
- **NIST 800-53 Rev 5** controls (e.g. `AC-2(1)`)
- **DISA STIG** rule IDs (e.g. `V-242414`)
- **MITRE ATT&CK** technique IDs (e.g. `T1078`)
- **CCI** (Control Correlation Identifier)

These are emitted in JSON, SARIF, and the OSCAL skeleton.

## CI / RMF integration

```yaml
- name: classmark scan
  run: |
    pip install "git+https://github.com/cognis-digital/classmark.git"
    classmark . --format=oscal --out=assessment-results.json --fail-on=high
- name: Upload to eMASS/Xacta
  run: cognis-rmf-package import assessment-results.json
```

## Part of the Cognis Digital military / IC ecosystem

12 repos. All MIT/Apache-2.0/GPL-3 (per upstream). Cognis additions are
Apache-2.0 unless stated otherwise.

See [the master index](../../MASTER-INDEX.md).

<a name="verification"></a>
## Verification

[![tests](https://img.shields.io/badge/tests-5%20passing-2ea44f.svg)](AUDIT.md)

Every push is verified end-to-end. Latest audit (2026-06-13):

```text
tests        : 5 passed, 0 failed, 0 errored
compile      : all modules parse
cli          : classmark 0.1.0
package      : classmark
```

<details><summary>CLI surface (<code>--help</code>)</summary>

```text
usage: classmark [-h] [--format {console,json,markdown,sarif,oscal}]
                 [--out OUT] [--fail-on {very_high,high,moderate,low,none}]
                 [--classification CLASSIFICATION] [-v]
                 [target]

classmark — Cognis Digital · Military/IC ecosystem

positional arguments:
  target                Path/target

options:
  -h, --help            show this help message and exit
  --format {console,json,markdown,sarif,oscal}
  --out OUT             Write output to file
```
</details>

Full machine-readable results: [`AUDIT.md`](AUDIT.md) · regenerate with `python -m classmark --help` + `pytest -q`.

<div align="right"><a href="#top">↑ back to top</a></div>

