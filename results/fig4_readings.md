# Values read off the paper's Fig. 4 (final episode, read by eye, about +/-1 s)

Fig. 4 of Ault, Hanna & Sharon (2020): average delay (s) vs training episode, mean of 30 trials.
These are our readings of a zoomed screenshot of the figure. They are approximate and not taken from any table.

| Demand | Actuated | DQN | DRSQ | DRHQ | CMA-ES |
|---|---|---|---|---|---|
| Low | 42.1 | 32.7 | 34.9 | 34.3 | 33.2 |
| Medium | 46.4 | 36.8 | 40.5 | 40.5 | 35.7 |
| High | about 67 | about 52-55 (noisy) | about 57-58 | about 57-58 | about 47 |

Reduction vs actuated (approximate):
- DRHQ, Low: about 18.5 %  -> consistent with "up to 19.4 %" (abstract).
- CMA-ES, High: about 29 %  -> consistent with "up to 30 %" (introduction).

Our actuated runs: Low 42.14 s, Medium 47.32 s, High 54.71 s and 58.37 s (see sumo_run/).
