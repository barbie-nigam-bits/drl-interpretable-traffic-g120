# Runs of the authors' code (jault/StateStreetSumo)

**Environment:** WSL2 Ubuntu 22.04, SUMO 1.12.0 (the authors used 1.0.1), Python 3.6.15 (conda),
tensorflow 1.12.0, Keras 2.2.4, gym 0.12.1, cma 2.7.0, numpy 1.19.5. No code patches.
Note: the Miniforge installer was downloaded with certificate checking disabled because of the corporate proxy.

**Commands (headless, 1 trial, 1 episode, different trial id per run):**
- Actuated baseline: `python -c "import main; main.run_trial('actu', <file>, 1, <trial>, render=False)"`
- DRHQ: `python -c "import main; main.run_trial('drhq', 0, 1, 5, render=False)"`

with `<file>` = 0 (Low), 1 (Medium), 2 (High) from `shared.py`.

| Run | Agent | Demand | Trial | Wall time | Trips | Missed | Mean timeLoss | Max delay | Rush-hour mean |
|---|---|---|---|---|---|---|---|---|---|
| 1 | actuated | Low | 0 | 20 m 07 s | 47,088 | 0 | 42.1386 s | 265.3 s | 64.3097 s |
| 2 | actuated | Medium | 2 | not timed | 53,687 | 0 | 47.3203 s | 331.2 s | 76.7484 s |
| 3 | actuated | High | 3 | not timed | 64,395 | 0 | 54.7140 s | 256.8 s | 75.8539 s |
| 4 | actuated | High | 4 | not timed | 64,784 | 0 | 58.3718 s | 377.5 s | 92.5320 s |
| 5 | DRHQ (exploratory) | Low | 5 | about 21 min (from file timestamps) | 47,152 | 0 | 42.6146 s | 334.8 s | 52.2107 s |

Actuated runs ended at 55,001 simulated seconds. The DRHQ run reports 10,343 in the `steps` column of `perf.csv`;
we did not check what that column counts for each agent, so the two are not compared.
Medium and High trial 3 ran in parallel; High trial 4 and the DRHQ run ran alone.

## Independent check
`checks/recompute_delay_from_tripinfo.py` recomputes the metrics from each run's `tripinfo.xml`
(compressed copies are in `tripinfo/`) and reproduces trips, mean time lost, max delay and the rush-hour mean exactly.

## Run 5: single exploratory DRHQ episode
A fresh DRHQ agent trained for one episode (5% random actions, exploration is switched off only at episode 20 in `drxq.py`).
Mean time lost is about 1% above the actuated Low run, smaller than the 7% difference between our two High actuated runs;
we draw no conclusion about DRHQ versus actuated control. The rush-hour mean is about 12 s lower, but our two High runs
differed by 16.7 s in rush-hour mean, so we do not claim an improvement. The first-hour mean ("dead hour") is much higher
(corrected 66.43 s vs 30.85 s for actuated); a plausible reason is an untrained policy early in the episode, not tested.
The run wrote `poly.fn` (23,904 bytes, from the polynomial agent in `drxq.py`; not opened) and `policy.net` (not uploaded).

## Observation about the released code
`traci_env.get_delay()` (line 353) returns `dh_loss / rh_trips`, dividing the dead-hour total by the
rush-hour trip count although `dh_trips` is counted (lines 334, 349). Screenshot: `5_get_delay_source.png`.

| Run | Printed "dead" | Corrected | Dead-hour trips | Rush-hour trips |
|---|---|---|---|---|
| Low (trial 0) | 19.4636 s | 30.8478 s | 2,927 | 4,639 |
| Medium (trial 2) | 27.5628 s | 40.1548 s | 3,476 | 5,064 |
| High (trial 3) | 24.0915 s | 37.3997 s | 3,664 | 5,688 |
| High (trial 4) | 26.2524 s | 40.4963 s | 3,723 | 5,743 |
| Low, DRHQ (trial 5) | 41.9221 s | 66.4282 s | 2,915 | 4,619 |

## Data check
Shipped demand files sum to 47,058 / 53,848 / 64,489 vehicles (Low / Medium / High; 14 h, 168 five-minute bins).
The paper's Table 1 gives 45,112 / 51,298 / 61,261. We could not reconcile this.
Simulated trips differ from the files by +30, +94 (DRHQ, Low), -161 and -94 (Medium, High trial 3) and +295 (High trial 4);
the paper (Sec. 6.1) spawns vehicles randomly.

## Scope
Actuated baseline: one episode for Low and Medium, two for High. DRHQ: one exploratory episode on Low demand.
No DQN, DRQ or DRSQ training. This is not a reproduction of the paper's results.

## Files in this folder
- Screenshots: `1_run_log_and_perf.png`, `2_recompute_check.png`, `3_three_demand_results.png`, `4_high_run2_and_perf.png`,
  `5_get_delay_source.png`, `6_recompute_from_gz.png`, `7_drhq_low_result.png`
- Logs: `actu_low_headless.log`, `actu_med_t2.log`, `actu_high_t3.log`, `actu_high_t4.log`, `drhq_low_t5.log`
- Results rows written by the authors' code (no header; columns: trial, episode, trips, missed, loss, steps, rush, dead,
  max delay, max queue): `actu_low_perf.csv`, `perf_all_three.csv`, `perf_all_runs.csv`, `drhq_low_perf.csv`
- `tripinfo/`: compressed raw trip data for runs 1-5
- `poly.fn`: polynomial file written by the DRHQ run
- `RESULTS_actuated_three_demand.md`: actuated results tables
