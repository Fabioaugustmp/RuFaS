# Other — changelog_WIP.md

# WIP Changelog (changelog_WIP.md)

## Overview

`changelog_WIP.md` is the work-in-progress changelog for the RuFaS (Ruminant Farm Systems) codebase. It records development changes that have been merged but are **not yet included in a version release**. Once a version is tagged, the entries in this file are moved into the release changelog and the WIP file is reset for the next development cycle.

The file serves two audiences:

- **Developers** — a running record of what changed, why, and where, so that team members can track the evolution of the codebase between releases.
- **Release managers** — a curated list of changes that feeds directly into version release notes.

## Entry Format

Every changelog entry must follow a strict format:

```
- [<PR #>](<link to PR>) - [Major change|minor change] [Impact Area] [Additional Impact Areas...] Description of the change.
```

### Required Fields

| Field | Requirement |
|---|---|
| **PR number** | The pull request number only — omit "PR" and "#". Must be a hyperlink to the PR using the format `[<PR #>](<link to PR>)`. |
| **Change magnitude** | Either `[Major change]` or `[minor change]`. A major change is one that would warrant a major version upgrade. |
| **Impact area** | One or more bracketed tags describing which parts of the codebase, inputs, or outputs are affected. Multiple impact areas are allowed (e.g., `[Animal] [InputChange] [OutputChange]`). |
| **Description** | A brief, concise description of the change. Avoid vague statements like "update xyz" — instead say "update xyz to abc". |

### Example

```
- [123](https://github.com/RuminantFarmSystems/RuFaS/pull/123) - [Major change] [Animal] [InputChange] [OutputChange] Adds a new user input for calf mortality rate and applies it to pre-wean survival calculations.
```

## Impact Area Tags

The changelog uses a controlled vocabulary of impact area tags. The most common ones observed in the current entries:

| Tag | Meaning |
|---|---|
| `[Animal]` | Animal module (herd management, reproduction, growth, rations) |
| `[Manure]` | Manure module |
| `[Crop and Soil]` | Crop and Soil module |
| `[Feed]` / `[Feeds]` | Feed module or feed input structure |
| `[Feed Storage]` | Feed storage inputs and validation |
| `[SimulationEngine]` | Core simulation loop and orchestration |
| `[OutputManager]` | Output data management and padding |
| `[GraphGenerator]` | Graph/report generation |
| `[ReportGenerator]` | Report generation |
| `[DataValidator]` | Input validation logic |
| `[Cross Validation]` | Cross-validation rules between modules |
| `[InputChange]` | Changes user input structure or adds new inputs |
| `[OutputChange]` | Changes output structure, variable names, or units |
| `[NoInputChange]` | No change to user inputs |
| `[NoOutputChange]` | No change to outputs |
| `[Docs]` | Documentation updates |
| `[Tests]` / `[Testing]` / `[E2ETesting]` | Test changes |
| `[pyproject.toml]` | Dependency or packaging changes |
| `[Properties]` | Properties/config file changes |
| `[Weather]` | Weather data handling |
| `[EEE]` | EEE module |
| `[Utility]` | Utility functions |
| `[Config]` | Configuration files |
| `[Dependabot]` | Dependency automation |
| `[Dependency - Black]` | Black formatter version |
| `[Verbosity]` | CLI verbosity controls |
| `[main.py]` | Entry point changes |
| `[Maintenance]` | General maintenance |
| `[TractorDataset]` | Tractor dataset input |
| `[Output]` | Output structure (general) |

## Structure

The file is organized into two sections:

### 1. Readme

Explains what a changelog is and why it matters. It documents the four required fields for each entry and provides a concrete example. This section is intended for contributors who are adding entries for the first time.

### 2. Changelog Entries

The actual list of changes, grouped under the heading **Next Version Updates**. Each entry is a single bullet line. The list is ordered by PR number (roughly chronological), with the most recent entries at the bottom.

## How It Connects to the Codebase

The changelog is a **documentation artifact**, not a code module. It has no runtime behavior, no imports, and no execution flow. Its connection to the codebase is through the PRs it references:

- Each entry links to a GitHub pull request in the `RuminantFarmSystems/RuFaS` repository.
- The impact tags map to actual modules and subsystems in the codebase (e.g., `[Animal]` corresponds to the Animal module, `[SimulationEngine]` to the simulation orchestration code).
- The file is maintained as part of the development workflow — contributors add entries when their PRs are merged, and release managers consume the entries when preparing version notes.

The changelog also references specific code artifacts by name, such as:

- `SimulationEngine._daily_simulation()`
- `Reproduction.execute_cow_ed_protocol()`
- `HerdManager.formulate_rations()`
- `Pen.formulate_optimized_ration`
- `Growth._calculate_pregnant_heifer_target_daily_growth()`
- `MineralizationDecomposition._calculate_nutrient_cycling_residue_composition_factor`
- `GraphGenerator._draw_graph()`
- `tractor_dataset.csv`
- `pyproject.toml`
- `constraints-release.txt`

## Contributing

When adding a new entry:

1. Use the PR number and link for the merged pull request.
2. Classify the change as `[Major change]` or `[minor change]` — most changes are minor; reserve major for breaking changes or significant new features.
3. Tag all impact areas that apply. Use multiple bracketed tags when the change spans multiple areas.
4. Write a description that is specific enough for a reader to understand what changed and why, without needing to open the PR.
5. Add the entry under the **Next Version Updates** heading, at the bottom of the list.

## Relationship to Release Changelog

When a version is released, the entries in this file are moved into the release changelog (e.g., `v1.0.0` release notes). The WIP file is then reset to an empty state for the next development cycle. This workflow is described in the project's branching and versioning policy documentation (see PR #2813).