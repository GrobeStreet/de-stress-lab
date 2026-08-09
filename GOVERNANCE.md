# Governance

`de-stress-lab` is currently maintained by Bobby Morong as a single-maintainer
open-source research project.

## Decisions

Routine fixes and documentation changes are decided through public issues and
pull requests. Changes that affect scientific meaning, public APIs, released
results, archive metadata, or frozen prediction ledgers require an explicit
issue describing the motivation, evidence, compatibility impact, and
provenance consequences before merge.

The maintainer makes the final merge and release decisions and documents the
reason when a substantial proposal is declined. Scientific disagreement is
not resolved by authority: competing implementations, validation evidence, and
clearly scoped alternatives are welcome.

## Releases and compatibility

Package releases follow semantic versioning and are recorded in
`CHANGELOG.md`. Released scientific artifacts and frozen ledgers are never
silently replaced. Corrections are published as new, separately versioned
artifacts with an erratum or provenance note.

## Contributions and credit

Contributors should follow `CONTRIBUTING.md`. Authorship on a software paper is
based on substantial intellectual or technical contribution and requires each
author's agreement and accountability. Smaller contributions are credited in
release notes, the repository history, or acknowledgements as appropriate.

## Support and conduct

Support channels are defined in `SUPPORT.md`; community behavior is governed by
`CODE_OF_CONDUCT.md`. Security-sensitive reports should use GitHub's private
security-advisory channel.

## Continuity

If the maintainer can no longer sustain the project, a demonstrated contributor
may be invited to co-maintain or take over maintenance. Any transfer will be
announced publicly and will preserve the repository, license, release history,
DOI relationships, and frozen-artifact provenance.
