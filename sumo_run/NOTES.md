# Run of the authors' code (jault/StateStreetSumo)

**Environment:** WSL2 Ubuntu 22.04, SUMO 1.12.0 (the authors used 1.0.1), Python 3.6.15 (conda),
tensorflow 1.12.0, Keras 2.2.4, gym 0.12.1, cma 2.7.0, numpy 1.19.5. No code patches.

**Command:** `python -c "import main; main.run_trial('actu', 0, 1, 0, render=False)"`
(actuated agent, Low demand, 1 trial, 1 episode, headless)

**Run:** wall time 20m 7s. Simulation ended at 55,001 s. Vehicles inserted: 47,088. No missed trips.

## Results (perf.csv)
| Metric | Value |
|---|---|
| Trips | 47,088 |
| Mean timeLoss (loss) | 42.1386 s |
| Max delay | 265.3 s |
| Rush-hour mean | 64.3097 s |
| "dead" as printed by the code | 19.4636 s |

## Independent check
`checks/recompute_delay_from_tripinfo.py` recomputes the metrics from `Data0-0/tripinfo.xml`.
It reproduces trips, loss, max delay and the rush-hour mean exactly.

## Observation about the released code
`traci_env.get_delay()` divides the dead-hour total by `rh_trips` (4,639) instead of `dh_trips` (2,927).
The printed dead-hour value (19.46 s) therefore understates the true average, which is 30.85 s.

## Data check
The shipped `Low.txt` sums to 47,058 vehicles (14 h, 168 five-minute bins). The paper's Table 1 gives 45,112.
We could not reconcile this. The run inserted 47,088 vehicles (30 more than the file; unexplained).

## Scope
One actuated-baseline episode only. This is not a reproduction of the paper's results.

## Files
- `1_run_log_and_perf.png` - run log summary and perf.csv
- `2_recompute_check.png` - independent recompute
- `actu_low_headless.log` - full terminal log
- `actu_low_perf.csv` - results row written by the authors' code (no header; columns: trial, episode, trips, missed, loss, steps, rush, dead, max delay, max queue)
