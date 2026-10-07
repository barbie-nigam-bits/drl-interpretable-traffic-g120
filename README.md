# DRL Assignment 1 – Group 120 – Interpretable Traffic Signal Control (Ault, Hanna, Sharon, AAMAS 2020)
Paper: https://arxiv.org/abs/1912.11023 | Authors' code: https://github.com/jault/StateStreetSumo

## What is here (our own work)
| Folder | Purpose | How to run |
|---|---|---|
| src/precedence.py | Eq. (1) precedence function, parameter counting | imported by checks |
| checks/check_parameters_and_monotonicity.py | 352/256 parameter counts; Definition 1 / Lemma 1 numerical test + negative control | `python checks/check_parameters_and_monotonicity.py` |
| checks/table1_and_arithmetic_checks.py | Table 1 and quoted arithmetic; optional parse of repo demand files | `python checks/table1_and_arithmetic_checks.py <path-to>/StateStreetSumo/utils` |
| results/ | Outputs (JSON, PNG) | generated |
| sumo_run/ | Logs/screenshots from running the authors' code (to be added) | |

These are sanity checks of the paper's definitions, not a replication of its SUMO results.
Requires: numpy, matplotlib.
