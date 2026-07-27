# Zenodo deposition specification

The DOI has not yet been minted. The authenticated depositor should create one
public **Software** record with the following exact scope.

## Files

Upload the immutable assets from the `v1.0` GitHub release:

- `canonical-reproduction-v1.0.tar.gz`
- `whitepaper.pdf`
- `SHA256SUMS-v1.0.txt`

Do not rebuild or rename the archive after deposition. Verify its digest
against `CANONICAL_RELEASE.json`.

## Metadata

- **Title:** de-stress-lab: Selection-aware stress tests and frozen prediction
  ledgers for scientific likelihoods
- **Resource type:** Software
- **Publication date:** 2026-07-21
- **Version:** 1.0
- **Creator:** Morong, Bobby
- **License:** MIT
- **Access:** Open
- **Related identifier:** the GitHub `v1.0` release, relation “is identical to”
- **Description and keywords:** use `.zenodo.json`

Add an ORCID only if it belongs to the creator and the creator elects to make
it public.

## After publication

Zenodo will provide a version DOI and normally a concept DOI. Record both in a
new commit:

1. add the version DOI to `archive/CANONICAL_RELEASE.json`;
2. add the appropriate software DOI to `CITATION.cff`;
3. replace the pending language in `README.md` and `ERRATA.md`;
4. add the DOI badge only after `https://doi.org/<doi>` resolves;
5. publish a small metadata-only follow-up release or pull request.

Never move the existing `v1.0` tag or replace its assets after DOI publication.
