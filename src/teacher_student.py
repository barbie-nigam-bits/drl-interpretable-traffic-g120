"""
Teacher-student sanity check of the three regulatable-Q variants (DRQ, DRSQ, DRHQ).  numpy + scikit-learn only.

What it is:  a *synthetic* stand-in for the Q-network ("teacher", a small MLP) and the interpretable polynomial G
("student", 11 actions x 16 inputs x (weight, exponent) = 352 parameters, structure as in drxq.py / networks.DQNPolyMax).
The student is trained to imitate the teacher with three different targets:
    DRQ  : squared error between G(s) and the teacher Q-values
    DRSQ : cross-entropy between softmax(G(s)) and softmax(Q(s))        (soft target)
    DRHQ : cross-entropy between softmax(G(s)) and one-hot argmax Q(s)  (hard target)
and we measure how often argmax G == argmax Q on held-out states, plus the Q-value lost when they disagree.

What it is NOT: it is not SUMO, not RL, and says nothing about the paper's 19.4%. The loss definitions follow the
paper's description; we did not read networks.py, so details of the authors' loss/scaling may differ.

G(s)_a = ( sum_{i<12} (w_ai s_ai)^p_ai ) * prod_{j>=12, s_aj>0} (w_aj s_aj)^p_aj      (cf. display() in drxq.py)
w = exp(a) > 0 ; exponents p clipped to [0.1, 4]; init w=1, p=1 (Alg. 1 line 4).
"""
import json, os, sys, time
import numpy as np
from sklearn.neural_network import MLPRegressor

A, F, NS = 11, 16, 12           # actions, inputs per action, state inputs per action (rest = clearance flags)
EPS = 1e-6

# ------------------------------------------------------------------ synthetic traffic-like data
def make_states(n, rng):
    s = np.zeros((n, A, F))
    s[:, :, :NS] = rng.random((n, A, NS)) * (rng.random((n, A, NS)) < 0.7)          # sparse, in [0,1]
    case = rng.integers(0, 4, (n, A))                                                # clearance case per action
    for j in range(4):
        s[:, :, NS + j] = (case == j)
    return s

def hidden_truth(s):
    """Non-polynomial 'true' value of each action (saturating terms + within-action interactions + clearance effect)."""
    q = s[:, :, 0] + s[:, :, 6]                       # stopped vehicles of the two phases
    ap = s[:, :, 1] + s[:, :, 7]                      # approaching
    wt = s[:, :, 2] + s[:, :, 8]                      # waiting time
    sp = s[:, :, 4] + s[:, :, 10]                     # queue length
    base = 1.2 * np.tanh(2.5 * q) + 0.8 * np.tanh(2.0 * wt) + 0.5 * np.sqrt(ap * (sp + 0.05)) + 0.6 * q * wt
    clear = np.array([1.0, 0.8, 0.45, 0.1])           # full / partial / permissive / none clearance (as printed in display())
    return base * (s[:, :, NS:] @ clear)

def fit_teacher(rng, n=30000):
    X = make_states(n, rng); Y = hidden_truth(X) + rng.normal(0, 0.03, (n, A))
    mlp = MLPRegressor((64, 64), activation="relu", max_iter=60, random_state=int(rng.integers(1e9)), early_stopping=False)
    mlp.fit(X.reshape(n, -1), Y)
    return mlp

# ------------------------------------------------------------------ the polynomial student (hand-written gradients)
class Poly:
    def __init__(self):
        self.a = np.zeros((A, F)); self.p = np.ones((A, F))
        self.m = {k: np.zeros((A, F)) for k in "ap"}; self.v = {k: np.zeros((A, F)) for k in "ap"}; self.t = 0
    def forward(self, s):
        pos = s > 0; ls = np.log(np.where(pos, s, 1.0))
        lt = self.p[None] * (self.a[None] + ls)
        term = np.where(pos, np.exp(np.clip(lt, -30, 30)), 0.0)
        S = term[:, :, :NS].sum(2)
        lC = np.where(pos[:, :, NS:], lt[:, :, NS:], 0.0).sum(2)
        C = np.exp(np.clip(lC, -30, 30))
        return S * C, (pos, ls, term, S, C)
    def grads(self, dg, cache):
        pos, ls, term, S, C = cache                          # dg : dLoss/dG  (n, A)
        n = dg.shape[0]
        gp = np.zeros((n, A, F)); ga = np.zeros((n, A, F))
        dterm = (dg * C)[:, :, None]
        ga[:, :, :NS] = dterm * self.p[None, :, :NS] * term[:, :, :NS]
        gp[:, :, :NS] = dterm * term[:, :, :NS] * (self.a[None, :, :NS] + ls[:, :, :NS])
        dC = (dg * S * C)[:, :, None]
        ga[:, :, NS:] = np.where(pos[:, :, NS:], dC * self.p[None, :, NS:], 0.0)
        gp[:, :, NS:] = np.where(pos[:, :, NS:], dC * (self.a[None, :, NS:] + ls[:, :, NS:]), 0.0)
        return ga.mean(0), gp.mean(0)
    def adam(self, ga, gp, lr):
        self.t += 1
        for k, g, x in (("a", ga, self.a), ("p", gp, self.p)):
            self.m[k] = 0.9 * self.m[k] + 0.1 * g; self.v[k] = 0.999 * self.v[k] + 0.001 * g * g
            mh = self.m[k] / (1 - 0.9 ** self.t); vh = self.v[k] / (1 - 0.999 ** self.t)
            x -= lr * mh / (np.sqrt(vh) + 1e-8)
        np.clip(self.p, 0.1, 4.0, out=self.p); np.clip(self.a, -6, 6, out=self.a)
    def n_params(self): return self.a.size + self.p.size

def softmax(z):
    z = z - z.max(1, keepdims=True); e = np.exp(z); return e / e.sum(1, keepdims=True)

def loss_grad(kind, g, q):
    n = g.shape[0]
    if kind == "DRQ":                                        # MSE to Q
        return ((g - q) ** 2).mean(), 2 * (g - q) / A
    if kind == "DRSQ":                                       # CE to softmax(Q)
        t = softmax(q); p = softmax(g)
    else:                                                    # DRHQ: CE to one-hot argmax Q
        t = np.eye(A)[q.argmax(1)]; p = softmax(g)
    return -(t * np.log(p + 1e-12)).sum(1).mean(), (p - t)

def agreement(poly, X, Q):
    g, _ = poly.forward(X); a = g.argmax(1); b = Q.argmax(1)
    ag = (a == b).mean()
    regret = (Q.max(1) - Q[np.arange(len(a)), a]).mean()
    return ag, regret

def train(kind, Xtr, Qtr, Xte, Qte, rng, steps=2500, bs=256, lr=0.03, log_every=100):
    poly = Poly(); curve = []
    for it in range(steps + 1):
        if it % log_every == 0:
            curve.append((it,) + agreement(poly, Xte, Qte))
        idx = rng.integers(0, len(Xtr), bs)
        g, cache = poly.forward(Xtr[idx])
        _, dg = loss_grad(kind, g, Qtr[idx])
        ga, gp = poly.grads(dg, cache); poly.adam(ga, gp, lr)
    return poly, np.array(curve)

if __name__ == "__main__":
    seeds = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results") if os.path.isdir(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")) else "."
    res = {k: [] for k in ("DRQ", "DRSQ", "DRHQ")}; curves = {k: [] for k in res}; rand_base, heur_base = [], []
    t0 = time.time()
    for sd in range(seeds):
        rng = np.random.default_rng(sd)
        teacher = fit_teacher(rng)
        Xtr = make_states(20000, rng); Xte = make_states(5000, rng)
        Qtr = teacher.predict(Xtr.reshape(len(Xtr), -1)); Qte = teacher.predict(Xte.reshape(len(Xte), -1))
        shift = Qtr.min(); Qtr = Qtr - shift; Qte = Qte - shift                      # G >= 0, so shift Q to >= 0 (argmax unchanged)
        # reference points: random action, and "most stopped vehicles" heuristic
        rand_base.append(float(np.mean(rng.integers(0, A, len(Xte)) == Qte.argmax(1))))
        heur = (Xte[:, :, 0] + Xte[:, :, 6]).argmax(1); heur_base.append(float((heur == Qte.argmax(1)).mean()))
        for kind in res:
            poly, cv = train(kind, Xtr, Qtr, Xte, Qte, np.random.default_rng(100 + sd))
            ag, rg = agreement(poly, Xte, Qte); res[kind].append((float(ag), float(rg), poly.n_params())); curves[kind].append(cv)
        print("seed", sd, {k: round(v[-1][0], 3) for k, v in res.items()}, "| %.0fs" % (time.time() - t0), flush=True)
    summary = {k: {"agreement_mean": float(np.mean([r[0] for r in v])), "agreement_std": float(np.std([r[0] for r in v])),
                   "q_regret_mean": float(np.mean([r[1] for r in v])), "n_params": v[0][2], "seeds": seeds} for k, v in res.items()}
    summary["baselines"] = {"random_action_agreement": float(np.mean(rand_base)), "max_stopped_heuristic_agreement": float(np.mean(heur_base))}
    summary["teacher_params"] = 176 * 64 + 64 + 64 * 64 + 64 + 64 * 11 + 11
    print(json.dumps(summary, indent=2))
    json.dump({"summary": summary, "per_seed": res}, open(os.path.join(out_dir, "teacher_student_results.json"), "w"), indent=2)
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    for k, c in zip(curves, ("tab:blue", "tab:orange", "tab:green")):
        cv = np.array(curves[k]); ax[0].plot(cv[0, :, 0], cv[:, :, 1].mean(0), c, label=k)
        ax[0].fill_between(cv[0, :, 0], cv[:, :, 1].mean(0) - cv[:, :, 1].std(0), cv[:, :, 1].mean(0) + cv[:, :, 1].std(0), color=c, alpha=.2)
    ax[0].axhline(summary["baselines"]["random_action_agreement"], ls=":", c="gray", label="random action")
    ax[0].axhline(summary["baselines"]["max_stopped_heuristic_agreement"], ls="--", c="gray", label="max-stopped heuristic")
    ax[0].set_xlabel("training step"); ax[0].set_ylabel("argmax agreement with teacher (held-out)"); ax[0].legend(); ax[0].set_title("Policy agreement, mean ± sd over %d seeds" % seeds)
    names = list(res); ax[1].bar(names, [summary[k]["agreement_mean"] for k in names], yerr=[summary[k]["agreement_std"] for k in names], color=("tab:blue", "tab:orange", "tab:green"))
    ax[1].set_ylabel("final agreement"); ax[1].set_title("Final agreement (352-parameter polynomial)")
    plt.tight_layout(); plt.savefig(os.path.join(out_dir, "teacher_student_agreement.png"), dpi=130)
