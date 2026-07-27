# Prediction-ledger maintenance

`2027-ledger.json` and its prose rendering were frozen on 2026-07-27 at the
annotated tag and GitHub release `prediction-ledger-2027-v1`.

The original files are immutable. Maintenance means preserving and verifying
them—not revising their language as events unfold.

## Integrity

```bash
cd predictions
sha256sum -c 2027-ledger.json.sha256
git diff --exit-code prediction-ledger-2027-v1 -- \
  2027-ledger.json 2027-ledger.json.sha256 2027-ledger.md
```

The scheduled ledger guard repeats these checks against the frozen tag.

## Amendments

A genuine ambiguity or error must be recorded in a new file under
`predictions/amendments/` with:

- a unique amendment ID and UTC date;
- the exact original passage;
- the clarification or correction;
- the reason it is needed;
- an explicit statement of whether scoring is affected;
- a SHA-256 digest; and
- a new annotated tag and release.

Never overwrite the v1 files or silently change a scoring threshold.

## Adjudication

Adjudication begins only after qualifying public data exist. It must cite the
source, record code and data versions, publish the calculations, and create a
separately hashed result. The forecast record itself remains unchanged.
