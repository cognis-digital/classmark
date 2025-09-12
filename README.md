# classmark — CAPCO classification-banner library (PLACEHOLDERS ONLY)

[![CI](https://github.com/cognis-digital/classmark/workflows/CI/badge.svg)](https://github.com/cognis-digital/classmark/actions)
[![Classification](https://img.shields.io/badge/classification-UNCLASSIFIED-green.svg)](./UPSTREAM.md)

> Build CAPCO-shape banner + portion marks. Validate *shape*, not content. Operators supply real values at runtime.

## Upstream

Forks / wraps **(original)**. See [`UPSTREAM.md`](./UPSTREAM.md) for the
licensing posture, supported commits, and how to upgrade.

## What this adds for military / IC use

- ClassificationBanner builder (level/SCI/SAP/dissem/CUI)
- Portion-mark shape validator
- Banner-line scanner for `.txt`/`.md`/`.html`/`.docx`/`.json`
- Operator-supplied content only — no real markings shipped

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
    pip install cognis-classmark
    classmark . --format=oscal --out=assessment-results.json --fail-on=high
- name: Upload to eMASS/Xacta
  run: cognis-rmf-package import assessment-results.json
```

## Part of the Cognis Digital military / IC ecosystem

12 repos. All MIT/Apache-2.0/GPL-3 (per upstream). Cognis additions are
Apache-2.0 unless stated otherwise.

See [the master index](../../MASTER-INDEX.md).
