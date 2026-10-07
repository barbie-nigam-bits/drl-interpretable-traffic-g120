"""Proof-of-work checks for Sec. 4 of the paper: parameter counts (352 / 256) and Definition 1 / Lemma 1."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from precedence import *

out = {}
rng = np.random.default_rng(0)

# ---- 1. parameter counts ---------------------------------------------------
out["params_figure1_8phases_8combos"] = n_parameters(8)    # paper: 8*(2*12+8) = 256
out["params_murray_10phases_11combos"] = n_parameters(11)  # paper: 352
assert out["params_figure1_8phases_8combos"] == 256
assert out["params_murray_10phases_11combos"] == 352
print("Parameter counts OK:", out["params_figure1_8phases_8combos"], out["params_murray_10phases_11combos"])

# ---- 2. Definition 1: monotonicity in each state variable --------------------
def sweep_is_monotone(i, phi, theta, grid=200):
    """Definition 1: sweep ONE variable s[phi,i] over [0,100] (others fixed, random).
    Returns True if the slope never changes sign."""
    w, p, w_c, p_c = theta
    f = clearance_flags(int(rng.integers(1, 5)))
    s = rng.uniform(0, 50, (2, N_STATE_VARS))
    ys = []
    for x in np.linspace(0.01, 100, grid):
        s2 = s.copy(); s2[phi, i] = x
        ys.append(precedence(s2, f, w, p, w_c, p_c))
    d = np.diff(ys)
    return len(set(np.sign(d[np.abs(d) > 1e-12]).astype(int).tolist())) <= 1

violations = 0; checked = 0
for k in range(40):                       # 40 random parameter settings; exponents p may be + or -
    theta = init_params(rng=rng)
    theta = (theta[0], theta[1] * rng.choice([1, -1], theta[1].shape, p=[.8, .2]), theta[2], theta[3])
    for phi in range(2):
        for i in range(N_STATE_VARS):
            for _ in range(5):            # 5 random base states per (phi, i)
                checked += 1
                if not sweep_is_monotone(i, phi, theta): violations += 1
out["monotonicity_variable_sweeps_checked"] = checked
out["monotonicity_violations"] = violations
print(f"Monotonicity: {checked} sweeps, {violations} sign changes")

# ---- 3. negative control: a non-regulatable (non-monotone) function fails the same test -----
def nonmono(x): return 3 * x - 0.05 * x ** 2        # rises then falls on [0,100]
d = np.diff(nonmono(np.linspace(0.01, 100, 200)))
out["negative_control_sign_set"] = sorted(set(np.sign(d).astype(int).tolist()))
print("Negative control (quadratic) slope signs:", out["negative_control_sign_set"], "-> NOT regulatable")

# ---- 4. analytic derivative of (w s)^p : p*w*(w s)^(p-1)  == p * w^p * s^(p-1) ------------------
w0, p0, s0 = 1.7, 1.6, 3.3
fd = ((w0 * (s0 + 1e-6)) ** p0 - (w0 * (s0 - 1e-6)) ** p0) / 2e-6
a1 = p0 * w0 * (w0 * s0) ** (p0 - 1); a2 = p0 * w0 ** p0 * s0 ** (p0 - 1); a3 = w0 * p0 * s0 ** (p0 - 1)
out["deriv_finite_diff"] = fd; out["deriv_p_w_(ws)^(p-1)"] = a1; out["deriv_p_w^p_s^(p-1)"] = a2
out["deriv_as_typeset_w_p_s^(p-1)"] = a3
print(f"d/ds (ws)^p  finite-diff={fd:.6f}  p*w*(ws)^(p-1)={a1:.6f}  p*w^p*s^(p-1)={a2:.6f}  w*p*s^(p-1)={a3:.6f}")

# ---- 5. figure: g vs each state variable (monotone curves) -------------------------------
fig, axs = plt.subplots(1, 2, figsize=(10, 3.8))
xs = np.linspace(0, 40, 200); f = clearance_flags(4)
for pv in (0.5, 1.0, 1.5, 2.0):
    w, p, w_c, p_c = init_params(); p = p * pv
    axs[0].plot(xs, [precedence(np.where(np.eye(2, N_STATE_VARS) > 0, x, 5.0), f, w, p, w_c, p_c) for x in xs], label=f"p={pv}")
axs[0].set_title("Precedence g vs. stopped vehicles (w=1)"); axs[0].set_xlabel("s[1]"); axs[0].legend()
axs[1].plot(xs, nonmono(xs), "r"); axs[1].set_title("Negative control: non-monotone function"); axs[1].set_xlabel("s")
plt.tight_layout(); plt.savefig(os.path.join(os.path.dirname(__file__), "..", "results", "monotonicity.png"), dpi=130)

json.dump(out, open(os.path.join(os.path.dirname(__file__), "..", "results", "check_parameters_and_monotonicity.json"), "w"), indent=2)
