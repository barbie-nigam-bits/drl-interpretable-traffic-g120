"""
Eq. (1) of Ault, Hanna & Sharon (AAMAS 2020), "Learning an Interpretable Traffic Signal Control Policy".

    g(s, Phi; theta') = [ sum_{phi in Phi} sum_{i=1..6} (w_{phi,i} * s_phi[i]) ^ p_{phi,i} ]
                        * [ sum_{j=1..4} (w'_j * f_j) ^ p'_j ]

 * s_phi[1..6]: stopped vehicles, approaching vehicles, cumulative stopped time,
                average stopped time, average queue length, average approach speed (Sec. 4)
 * f_1..f_4   : clearance flags (full / partial / permissive / none); one-hot, lowest index wins
 * 12 tunable parameters per phase (6 weights + 6 exponents) and 8 per phase-combination
   (4 weights + 4 exponents) -> n_combos * (phases_per_combo * 12 + 8)

NOTE (our reading): the typeset equation is a product of the two sums above.
"""
import numpy as np

N_STATE_VARS = 6
N_CLEARANCE = 4


def n_parameters(n_combos: int, phases_per_combo: int = 2) -> int:
    """Total tunable parameters of G over all phase combinations."""
    per_combo = phases_per_combo * 2 * N_STATE_VARS + 2 * N_CLEARANCE
    return n_combos * per_combo


def clearance_flags(case: int) -> np.ndarray:
    """case in {1,2,3,4} -> one-hot flag vector. Lowest index wins if several apply."""
    f = np.zeros(N_CLEARANCE)
    f[case - 1] = 1.0
    return f


def precedence(s, f, w, p, w_c, p_c):
    """
    s   : (n_phases, 6) non-negative state variables for the phases in this combination
    f   : (4,) one-hot clearance flags
    w,p : (n_phases, 6) weights / exponents
    w_c, p_c : (4,) clearance weights / exponents
    """
    s = np.asarray(s, float)
    with np.errstate(invalid="ignore", divide="ignore"):
        state_term = np.sum((w * s) ** p)
        clear_term = np.sum(np.where(f > 0, (w_c * f) ** p_c, 0.0))   # 0^p' = 0 for inactive flags
    return state_term * clear_term


def policy(states, flags, params):
    """argmax over phase-combinations. states/flags/params are lists, one entry per combination."""
    scores = [precedence(s, f, *pr) for s, f, pr in zip(states, flags, params)]
    return int(np.argmax(scores)), scores


def init_params(n_phases=2, rng=None):
    """Paper initialises weights to 1 (Alg. 1 line 4); optional noise for tests."""
    w = np.ones((n_phases, N_STATE_VARS)); p = np.ones((n_phases, N_STATE_VARS))
    w_c = np.ones(N_CLEARANCE); p_c = np.ones(N_CLEARANCE)
    if rng is not None:
        w = w * rng.uniform(0.2, 3.0, w.shape); p = rng.uniform(0.3, 2.5, p.shape)
        w_c = rng.uniform(0.2, 3.0, 4); p_c = rng.uniform(0.3, 2.5, 4)
    return w, p, w_c, p_c
