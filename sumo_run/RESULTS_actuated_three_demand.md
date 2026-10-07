# Actuated baseline, three demand levels (authors' code, unpatched)

Environment: WSL2 Ubuntu 22.04, SUMO 1.12.0 (authors: 1.0.1), Python 3.6.15, tensorflow 1.12.0.
Each run: 1 trial, 1 episode, headless, via `main.run_trial('actu', <file>, 1, <trial>, render=False)`.
Demand index from shared.py: 0 = Low.txt, 1 = Med.txt, 2 = High.txt.

| Demand | Command args | Trips | Missed | Mean timeLoss (s) | Max delay (s) | Rush-hour mean (s) | Rush trips |
|---|---|---|---|---|---|---|---|
| Low | ('actu', 0, 1, 0) | 47,088 | 0 | 42.1386 | 265.3 | 64.3097 | 4,639 |
| Medium | ('actu', 1, 1, 2) | 53,687 | 0 | 47.3203 | 331.2 | 76.7484 | 5,064 |
| High | ('actu', 2, 1, 3) | 64,395 | 0 | 54.7140 | 256.8 | 75.8539 | 5,688 |

All values were reproduced independently from each run's tripinfo.xml with `checks/recompute_delay_from_tripinfo.py`.
Rush-hour start (shared.py): Low 33,900 s; Medium and High 34,200 s. Simulation ended at 55,001 s in all three runs.

## Dead-hour average: authors' formula vs corrected
`traci_env.get_delay()` divides the dead-hour total by the rush-hour trip count.

| Demand | Printed by authors' code (s) | Corrected, dh_loss / dh_trips (s) | Dead-hour trips |
|---|---|---|---|
| Low | 19.4636 | 30.8478 | 2,927 |
| Medium | 27.5628 | 40.1548 | 3,476 |
| High | 24.0915 | 37.3997 | 3,664 |

The same discrepancy appears in all three runs.

## Trips vs shipped demand files
| Demand | Sum of shipped file | Paper Table 1 | Simulated trips |
|---|---|---|---|
| Low | 47,058 | 45,112 | 47,088 |
| Medium | 53,848 | 51,298 | 53,687 |
| High | 64,489 | 61,261 | 64,395 |

Not reconciled with Table 1. Simulated trips differ from the shipped files by +30, -161 and -94.

## Scope
One actuated-controller episode per demand level. No learning agent was trained. Not a reproduction of the paper's DRHQ results.
