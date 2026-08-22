# Other — README.md

# README.md — Project Entry Point and Overview

## Purpose

The `README.md` file serves as the primary entry point for the RuFaS (Ruminant Farm Systems) repository. It is the first document a developer, researcher, or contributor encounters and provides a high-level orientation to the project's goals, scientific foundation, setup procedure, contribution guidelines, and licensing. It is a static documentation file with no executable code — it contains no functions, classes, or runtime behavior.

## Role in the Codebase

The README is the hub that links outward to the rest of the project's documentation and infrastructure. It references:

| Target | Purpose |
|---|---|
| `main.py` | The entry-point script users run to execute a simulation |
| `output/output_filters/_csv_all_variables.txt` | A filter file that must be renamed to enable CSV output |
| `CONTRIBUTING.md` | Contribution guidelines and standards |
| `COPYING.md` / `COPYING.LESSER.md` | GPLv3 license texts |
| GitHub Pages site (`ruminantfarmsystems.github.io/RuFaS/`) | Full documentation, including the GitHub Actions wiki and end-to-end testing guides |
| YouTube onboarding playlist | Video walkthroughs for new users |
| `rufas.org` team and partner pages | Acknowledgement of contributors and organizations |

The README also displays CI status badges (Flake8, Pytest, Coverage, Mypy) that link to the `combined_format_lint_test_mypy.yml` GitHub Actions workflow, giving readers an at-a-glance view of the repository's health.

## Key Sections

### Vision and Mission

The README opens with the project's vision — supporting research and sustainable decision-making in ruminant animal production — and its mission: building an integrated whole-farm modeling platform that simulates milk/meat/crop production, greenhouse gas emissions, water quality, soil health, and other sustainability outcomes. It also states quality standards for prediction accuracy, code structure, and documentation.

### Scientific Foundation

Briefly establishes that RuFaS is grounded in peer-reviewed science and maintained by a community of researchers, developers, and stakeholders committed to transparency and reproducibility.

### Getting Started

A six-step setup procedure for new users:

1. Install Python 3.12 or 3.13
2. Create and activate a virtual environment (`python -m venv venv`)
3. Install dependencies with `pip install .`
4. Rename `output/output_filters/_csv_all_variables.txt` to `csv_all_variables.txt` to enable output display
5. Run the simulation with `python main.py`
6. Consult the GitHub Pages documentation or onboarding videos for further questions

### How to Contribute

Lists the types of contributions accepted — testing, feature suggestions, scientific discussion, code, documentation, user support, UI design, and promotion. Points readers to the Contributor Covenant code of conduct and `CONTRIBUTING.md` for full details, and to the GitHub Pages wiki for prerequisites and end-to-end testing information.

### License

States that RuFaS is licensed under GPLv3, with links to the license texts.

### Contact and Acknowledgements

Provides the project contact email (`contact@rufas.org`) and acknowledges contributing individuals and organizations, with links to the team page, partners page, and the GitHub contributors graph.

## Usage Notes for Developers

- The README is not imported or executed by any code in the repository. It is purely informational.
- When modifying the README, keep the setup steps in sync with the actual behavior of `main.py` and the output filter directory — these are the two code-adjacent details most likely to drift out of date.
- The CI badge URLs point to the `combined_format_lint_test_mypy.yml` workflow; if that workflow is renamed or moved, the badges must be updated accordingly.
- The Mypy badge currently reports 1134 errors, which is a known status indicator — do not assume it reflects a passing state.

## Relationship to Other Modules

The README has no runtime dependencies. Its connections to the codebase are purely referential: it documents how to invoke `main.py`, how to configure output via the filter file, and where to find the contribution and licensing documents. It is the recommended starting point for anyone onboarding to the repository, after which they should read `CONTRIBUTING.md` and the GitHub Pages wiki for operational details.