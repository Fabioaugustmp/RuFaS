# Other — changelog.md

# changelog.md

## Overview

`changelog.md` is the project-level changelog for the RuFaS (Ruminant Farm Systems) model. It provides a structured, human-readable record of all changes made to the codebase across releases. The file is intended for both developers and users: it documents new features, bug fixes, improvements, and dependency updates, and it makes the evolution of the model transparent and auditable.

This module is a static Markdown document. It contains no executable code, no functions, and no runtime behavior. Its "interface" is the set of conventions it defines for describing changes, and its primary consumers are developers who need to understand what changed in a given release and contributors who need to add new entries.

## File Location and Role

The file lives at the repository root as `changelog.md`. It is referenced by the project's contribution workflow and release process. The changelog is manually maintained: every pull request that introduces a user-visible or code-structure change is expected to add an entry under the appropriate version heading.

The changelog is not generated from Git history. It is curated so that entries can carry additional context—impact area, input/output change flags, and a concise description—that a raw commit log does not provide.

## Document Structure

The file is divided into two top-level sections:

1. **Readme** – explains what a changelog is, why RuFaS maintains one, and the required format for each entry.
2. **Changelog Entries** – the actual list of changes, grouped by version number.

### Readme Section

The Readme section defines the purpose of the changelog and the mandatory components of every entry. It emphasizes that each entry must include:

- **PR number** – the numeric GitHub pull request number, without the `PR` prefix or `#` symbol.
- **PR link** – a Markdown link to the pull request, formatted as `[<PR #>](<link to PR>)`.
- **Change magnitude** – either `[Major change]` or `[minor change]`, indicating whether the PR warrants a major version bump.
- **Impact area** – one or more bracketed tags describing which part of the codebase or which inputs/outputs are affected (e.g., `[Animal]`, `[Manure]`, `[OutputManager]`, `[NoInputChange]`).
- **Description** – a brief, specific sentence or two explaining what changed and why. Vague descriptions such as "update xyz" are discouraged; the description should state the concrete change, e.g., "update xyz to abc".

The Readme also includes a canonical example entry:

```
- [123](https://github.com/RuminantFarmSystems/RuFaS/pull/123) - [Major change/ minor change] [Impact Area] Short description of the change or feature.
```

### Changelog Entries Section

The entries are organized under version headings in descending order (newest first). Each version heading is an `###` Markdown heading, and the current release is also listed under a `### Current version` heading immediately above the newest version block.

Example:

```
### Current version

v1.0.3

### v1.0.3

- [3121](https://github.com/RuminantFarmSystems/RuFaS/pull/3121) - [minor change] [Animal] [NoInputChange] [OutputChange] Adds separate tracking for unmitigated vs. mitigated enteric methane for cows.
```

## Entry Format

Every entry is a single bullet point with the following structure:

```
- [<PR number>](<PR URL>) - [<change magnitude>] [<impact area>]... <description>
```

The fields are separated by spaces and hyphens. The impact area tags are repeatable, so an entry can affect multiple modules or explicitly state that inputs or outputs did not change.

Common impact area tags observed in the changelog include:

- `[Animal]`
- `[Manure]`
- `[Crop & Soil]` / `[Crop and Soil]` / `[Soil]`
- `[Feed]` / `[Feed Storage]` / `[FeedManager]`
- `[OutputManager]` / `[ReportGenerator]` / `[GraphGenerator]`
- `[InputManager]` / `[DataValidator]`
- `[TaskManager]`
- `[EEE]` (Energy and Emissions Evaluation)
- `[Weather]`
- `[Testing]` / `[E2E Testing]`
- `[Documentation]` / `[Readme]` / `[Wiki]`
- `[GitHub Actions]` / `[Github action]`
- `[Metadata]`
- `[Formatting]`
- `[NoInputChange]` / `[InputChange]`
- `[NoOutputChange]` / `[OutputChange]`

The `[NoInputChange]` and `[NoOutputChange]` tags are used to explicitly communicate that a PR does not alter the model's input schema or output structure. This is important for users who need to know whether a version upgrade will require changes to their input files or downstream output processing.

## Versioning Scheme

The changelog tracks semantic version numbers (`v1.0.3`, `v1.0.2`, etc.). The `### Current version` heading identifies the latest release. The version numbers correspond to tags or releases in the RuFaS repository and are also reflected in `pyproject.toml`.

The distinction between `[Major change]` and `[minor change]` in an entry is the signal used to decide whether a release should increment the major or minor version component. Most entries in the changelog are marked `[minor change]`; a `[major change]` tag is reserved for substantial architectural shifts or user-facing overhauls, such as the integration of the Data Collection App or the refresh of the Animal module.

## Relationship to the Codebase

Although `changelog.md` is not code, it is tightly coupled to the development workflow:

- **Pull requests** – every entry references a GitHub pull request. The PR number and link are the traceability mechanism back to the actual diff, discussion, and review history.
- **Release process** – the changelog is the authoritative list of changes included in a release. When a new version is cut, the entries are grouped under a new version heading and the `Current version` line is updated.
- **Contribution guidelines** – the Readme section acts as a lightweight specification for contributors. It is referenced by the PR template and by `CONTRIBUTING.md` to ensure that all changes are documented consistently.
- **Documentation ecosystem** – the changelog complements the Sphinx-generated API documentation and the scientific documentation. It provides the "what changed over time" view that API docs cannot.

The changelog has no runtime dependencies and is not imported by any module. It is a documentation artifact, not a data source.

## Maintenance Guidelines

To keep the changelog useful and accurate, contributors should follow these practices:

1. **Add an entry for every user-relevant PR.** If a PR changes inputs, outputs, module behavior, or project infrastructure, it belongs in the changelog.
2. **Place the entry under the correct version.** If the change is part of an unreleased version, add it to the top version block. If a new version is being started, create a new `### vX.Y.Z` heading and update `### Current version`.
3. **Use the exact entry format.** Include the PR number, link, change magnitude, impact area tags, and a specific description.
4. **Be precise in descriptions.** Avoid generic phrases. State what was changed and, where relevant, why.
5. **Use `[NoInputChange]` and `[NoOutputChange]` deliberately.** These tags are valuable to downstream users and should be included whenever a PR does not affect the input schema or output reporting.
6. **Keep the changelog in sync with release metadata.** When the version in `pyproject.toml` is updated, the changelog's `Current version` and version headings should match.

## Summary

`changelog.md` is the project's memory. It records the rationale and scope of every significant change in a format that is easy to scan, linkable to the underlying PRs, and aligned with the project's versioning strategy. For developers, it is the first place to look when investigating when a behavior changed or why a particular module was refactored. For users, it is the definitive list of what a new version brings.