# Actuated baseline, three demand levels (authors' code, unpatched)

Environment: WSL2 Ubuntu 22.04, SUMO 1.12.0 (authors: 1.0.1), Python 3.6.15, tensorflow 1.12.0.
Each run: 1 trial, 1 episode, headless, via `main.run_trial('actu', <file>, 1, <trial>, render=False)`.
Demand index from shared.py: 0 = Low.txt, 1 = Med.txt, 2 = High.txt.

| Demand | Trial | Trips | Missed | Mean timeLoss (s) | Max delay (s) | Rush-hour mean (s) | Rush trips |
|---|---|---|---|---|---|---|---|
| Low | 0 | 47,088 | 0 | 42.1386 | 265.3 | 64.3097 | 4,639 |
| Medium | 2 | 53,687 | 0 | 47.3203 | 331.2 | 76.7484 | 5,064 |
| High | 3 | 64,395 | 0 | 54.7140 | 256.8 | 75.8539 | 5,688 |
| High | 4 | 64,784 | 0 | 58.3718 | 377.5 | 92.5320 | 5,743 |

All values were reproduced independently from each run's tripinfo.xml with `checks/recompute_delay_from_tripinfo.py`.
Rush-hour start (shared.py): Low 33,900 s; Medium and High 34,200 s. Simulation ended at 55,001 s in all runs.
The two High runs differ by 3.7 s (about 7%) in mean time lost, so a single run is only indicative.

## Dead-hour average: authors' formula vs corrected
`traci_env.get_delay()` divides the dead-hour total by the rush-hour trip count.

| Run | Printed by authors' code (s) | Corrected, dh_loss / dh_trips (s) | Dead-hour trips |
|---|---|---|---|
| Low | 19.4636 | 30.8478 | 2,927 |
| Medium | 27.5628 | 40.1548 | 3,476 |
| High, trial 3 | 24.0915 | 37.3997 | 3,664 |
| High, trial 4 | 26.2524 | 40.4963 | 3,723 |

## Trips vs shipped demand files
| Demand | Sum of shipped file | Paper Table 1 | Simulated trips |
|---|---|---|---|
| Low | 47,058 | 45,112 | 47,088 |
| Medium | 53,848 | 51,298 | 53,687 |
| High | 64,489 | 61,261 | 64,395 and 64,784 |

Not reconciled with Table 1.

## Scope
No learning agent was trained. Not a reproduction of the paper's DRHQ results.
