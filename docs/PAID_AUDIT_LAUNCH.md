# Paid audit launch plan

## Campaign overview

**Campaign:** From green badge to verified run

**Objective:** complete three paid repository audits in the first 30 days,
learn which findings buyers value, and obtain permission to publish at least
one anonymized or public case study.

The campaign starts with owned and earned channels. Paid advertising is deferred
until the first purchases demonstrate a repeatable conversion path.

## Audience

Primary: maintainers of public research-code repositories who are preparing a
paper, release, grant report, replication package, or external handoff.

Secondary: lab managers, research-software engineers, methods editors, and
funders responsible for computational reproducibility across several projects.

They care about catching preventable failures before reviewers or collaborators
do, receiving concrete remediation rather than a generic score, and avoiding
claims of scientific endorsement.

## Message

**Core message:** The free badge tells you whether the repository is ready to
inspect; the paid audit tells you what is likely to break for an independent
reproducer and what to fix first.

Proof points:

- transparent public 100-point rubric;
- the Dark-Energy Stress Lab as a versioned flagship demonstration;
- machine-readable reports and frozen evidence;
- an explicit boundary between readiness, reproduction, and scientific
  correctness.

## Channel strategy

| Channel | Role | Effort |
|---|---|---:|
| GitHub Action summary and documentation | Convert existing users | Low |
| Repository README and services page | Establish scope and proof | Low |
| Public, permission-based repository audits | Demonstrate useful findings | Medium |
| Direct outreach to maintainers of relevant public repositories | Acquire first customers | Medium |
| One public case study after customer permission | Build credibility | Medium |

Do not post unsolicited findings as public issues. Contact maintainers
privately or contribute only when repository norms clearly invite it.

## Four-week calendar

| Week | Deliverable | Channel | Success signal |
|---|---|---|---|
| 1 | Publish the offer, checkout, report CTA, and runbook | GitHub + Stripe | Funnel is complete |
| 2 | Run the free Action on 10 suitable public repositories | Internal research | 5 strong prospects |
| 3 | Send concise permission-based outreach | Direct | 3 qualified replies |
| 4 | Deliver first audits and request case-study permission | Email + GitHub | 1 public proof asset |

## Metrics

- free Action workflow runs;
- visits to the paid-audit scope page;
- Stripe checkout starts and completed payments;
- paid audits delivered within the target window;
- fixed-scope requests that require rescoping;
- upgrades to a reproduction sprint or statistical red team.

Review weekly. Do not optimize for badge installations alone; the primary
measure is paid audits completed without owner-heavy intervention.

## Launch risks

- **Overclaiming:** preserve the boundary statement in checkout, reports, and
  delivery.
- **Unsafe execution:** use the fulfillment safety gate; static review is the
  fallback.
- **Scope creep:** keep one repository, one build path, and one clarification
  round at the fixed price.
- **Stripe account review:** confirm live payment capabilities before broad
  promotion.
