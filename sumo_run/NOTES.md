# Runs of the authors' code (jault/StateStreetSumo)

**Environment:** WSL2 Ubuntu 22.04, SUMO 1.12.0 (the authors used 1.0.1), Python 3.6.15 (conda),
tensorflow 1.12.0, Keras 2.2.4, gym 0.12.1, cma 2.7.0, numpy 1.19.5. No code patches.
Note: the Miniforge installer was downloaded with certificate checking disabled because of the corporate proxy.

**Command (actuated agent, headless, 1 trial, 1 episode):**
`python -c "import main; main.run_trial('actu', <file>, 1, <trial>, render=False)"`
with `<file>` = 0 (Low), 1 (Medium), 2 (High) from `shared.py`, and a different `<trial>` id per run.

| Run | Demand | Trial | Wall time | Trips | Missed | Mean timeLoss | Max delay | Rush-hour mean |
|---|---|---|---|---|---|---|---|---|
| 1 | Low | 0 | 20 m 07 s | 47,088 | 0 | 42.1386 s | 265.3 s | 64.3097 s |
| 2 | Medium | 2 | not timed | 53,687 | 0 | 47.3203 s | 331.2 s | 76.7484 s |
| 3 | High | 3 | not timed | 64,395 | 0 | 54.7140 s | 256.8 s | 75.8539 s |
| 4 | High | 4 | not timed | 64,784 | 0 | 58.3718 s | 377.5 s | 92.5320 s |

Every simulation ended at 55,001 s. Medium and High trial 3 ran in parallel; High trial 4 ran alone.

## Independent check
`checks/recompute_delay_from_tripinfo.py` recomputes the metrics from each run's `tripinfo.xml`
and reproduces trips, mean time lost, max delay and the rush-hour mean exactly.

## Observation about the released code
`traci_env.get_delay()` (line 353) returns `dh_loss / rh_trips`, dividing the dead-hour total by the
rush-hour trip count although `dh_trips` is counted (lines 334, 349). Screenshot: `5_get_delay_source.png`.

| Run | Printed "dead" | Corrected | Dead-hour trips | Rush-hour trips |
|---|---|---|---|---|
| Low (trial 0) | 19.4636 s | 30.8478 s | 2,927 | 4,639 |
| Medium (trial 2) | 27.5628 s | 40.1548 s | 3,476 | 5,064 |
| High (trial 3) | 24.0915 s | 37.3997 s | 3,664 | 5,688 |
| High (trial 4) | 26.2524 s | 40.4963 s | 3,723 | 5,743 |

## Data check
Shipped demand files sum to 47,058 / 53,848 / 64,489 vehicles (Low / Medium / High; 14 h, 168 five-minute bins).
The paper's Table 1 gives 45,112 / 51,298 / 61,261. We could not reconcile this.
Simulated trips differ from the files by +30, -161, -94 and +295; the paper (Sec. 6.1) spawns vehicles randomly.

## Scope
One actuated episode for Low and Medium and two for High; no learning agent was trained.
This is not a reproduction of the paper's results.

## Files in this folder
- `1_run_log_and_perf.png`, `2_recompute_check.png`, `3_three_demand_results.png`, `4_high_run2_and_perf.png`, `5_get_delay_source.png`: screenshots
- `actu_low_headless.log`, `actu_med_t2.log`, `actu_high_t3.log`, `actu_high_t4.log`: terminal logs
- `actu_low_perf.csv`, `perf_all_three.csv`, `perf_all_runs.csv`: results rows written by the authors' code
  (no header; columns: trial, episode, trips, missed, loss, steps, rush, dead, max delay, max queue)
- `RESULTS_actuated_three_demand.md`: results tables
