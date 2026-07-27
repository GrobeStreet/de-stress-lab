# Contributing

Contributions that improve correctness, generality, documentation, or test
coverage are welcome.

1. Open an issue describing the scientific or software change.
2. Create a focused branch and include tests for changed behavior.
3. Run `python -m pip install -e ".[test]"` and `pytest`.
4. Open a pull request explaining the numerical and scientific consequences.

Changes to released result files or a frozen prediction ledger require an
explicit provenance note. A frozen ledger is never edited in place; corrections
are appended as a new, separately hashed amendment.

Please report security-sensitive problems privately through GitHub's security
advisory feature. Use ordinary issues for scientific and reproducibility bugs.

