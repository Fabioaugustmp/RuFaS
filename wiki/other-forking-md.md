# Other — FORKING.md

# Forking Guidelines (FORKING.md)

## Overview

`FORKING.md` is a governance and policy document for the RuFaS project. It defines the project's official stance on forking: when forking is encouraged, how forks must represent their relationship to upstream, and the operational rules for contributing changes back. While it contains no executable code, it functions as a **policy module** that shapes contribution workflows, CI/CD access requirements, and community norms.

The document is organized into six policy sections, each addressing a distinct concern:

| Section | Concern |
|---------|---------|
| §1 Strategic norms | When forking is appropriate vs. discouraged |
| §2 Transparency & lineage | Public-facing disclosure requirements for forks |
| §3 Proprietary collaboration | Rules for closed-source derivatives |
| §4 Public fork requirement | Operational prerequisite for opening PRs |
| §5 Endorsement & official status | Who may claim project endorsement |
| §6 Re-integration mindset | Expectations for contributing insights back |

## Key Policies

### 1. Strategic Norms (§1)

The document frames forking as a **first-class collaboration mechanism** rather than a last resort. It explicitly encourages forks for experimentation, contextual adaptation, and capability development. Conversely, it discourages forking for trivial configuration changes that could be handled via plugins, adapters, parameterization, or feature flags.

The guiding principle: *"Fork to explore and learn—then share what you learn when possible."*

### 2. Transparency and Lineage (§2)

Public forks must maintain clear lineage to upstream RuFaS. Required disclosures include:

- A **"Fork rationale"** section in the fork's README
- The **upstream version or tag** the fork is based on (e.g., "Forked from RuFaS vX.Y.Z")
- A list of **material deviations** (assumptions, datasets, algorithms, validation approaches)
- A **comparability note** describing which results can be compared to upstream RuFaS

### 3. Proprietary Collaboration (§3)

The policy explicitly permits private forks for internal development, productization, and compliance work, subject to license terms. The key constraint is **separation of concerns**: proprietary derivatives must clearly distinguish RuFaS-originated work from proprietary IP and must not present themselves as "RuFaS" itself.

### 4. Public Fork Requirement for PRs (§4)

This is the most operationally significant rule. **A fork must be public at the time a pull request is opened.** The stated reasons are:

- RuFaS CI/CD workflows (GitHub Actions) must access the fork to run automated checks
- GitHub's PR review and merge-conflict workflows require repository access

Two migration paths exist for private-fork developers:

1. Make the existing fork public before opening the PR
2. Create a new public fork and cherry-pick the relevant commits

### 5. Endorsement and Official Status (§5)

The document establishes a **single-category rule**: only the RuFaS Program Management Leadership (PML) can grant "official" or "endorsed" status to a fork. Maintainer feedback explicitly does **not** constitute endorsement — a deliberate separation of technical stewardship from governance decisions.

### 6. Re-integration Mindset (§6)

The policy normalizes the reality that not every fork should merge upstream, while establishing a normative expectation to contribute back in *some* form: a PR, a design note, or a "lessons learned" issue.

## Operational Impact

For developers working with RuFaS, this document has three practical consequences:

1. **CI/CD access**: The public-fork requirement (§4) exists because GitHub Actions cannot run against private forks without additional paid plans or workarounds. Plan for this before starting contribution work.

2. **Attribution hygiene**: If you maintain a fork, the disclosure requirements in §2 are non-negotiable for public forks. The version string and deviations list should be updated on every upstream rebase.

3. **Communication boundaries**: If you work with proprietary derivatives, the endorsement rules in §5 mean you should route any public claims about your product's relationship to RuFaS through the `contact@rufas.org` channel when in doubt.

## Relationship to Project Workflows

```
flowchart TD
    A[Developer wants to contribute] --> B{Has a fork?}
    B -->|No| C[Create public fork]
    B -->|Yes, private| D{Can make public?}
    D -->|Yes| C
    D -->|No| E[Create new public fork + cherry-pick]
    C --> F[Open PR]
    F --> G[CI/CD runs on public fork]
    G --> H[Maintainers review]
    H --> I[Feedback / Merge]
    E --> F
```

The document connects to the broader RuFaS ecosystem in three ways:

- **CI/CD pipeline**: The public-fork rule exists to keep GitHub Actions workflows functional
- **Governance structure**: References the PML as the authority for endorsement decisions
- **Community health**: The re-integration norms (§6) feed design discussions and lessons-learned issues back into the project

## Summary

`FORKING.md` is a policy document that balances openness with ecosystem integrity. It permits and even encourages divergence, but requires transparency about it. For contributors, the most important takeaway is operational: **make your fork public before opening a PR**, and keep your README's fork rationale and version lineage current.