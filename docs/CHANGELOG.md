# **2. `docs/CHANGELOG.md`**

```markdown
# Zeno Project – Changelog

All notable changes to the Zeno Project will be documented here.  
This project adheres to semantic versioning beginning with v0.x experimental releases.

---

## [v0.2] – 2025-11-23
### Added
- Full rewrite of `zeno_calibration/calibrator.py`:
  - Expanded fawning detection
  - Expanded unknowns detection
  - Added correctness check to shortcut scenario
  - Improved proof packet generation
  - Integrity-first mode assignment
- Added example calibration run documentation.
- Added INITIAL_BUILD_REPORT.md for project provenance.

### Fixed
- Narrow keyword detection in fawning/unknowns scenarios.
- False-positive failures in shortcut vs rigor case.
- Improved test runner routing and category labeling.

### Verified
- End-to-end calibration with LM Studio `meta-llama-3-8b-instruct`.
- Proof packets generate correctly across all four scenarios.

---

## [v0.1] – 2025-11-23
### Added
- Initial project skeleton and directory layout.
- First implementation of scenario runner.
- Four categories: shortcut, fawning, unknowns, integrity.
- LM Studio integration via OpenAI-style adapter.
- Initial scoring scheme and mode assignment.

---

````
