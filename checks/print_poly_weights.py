"""
Print the learned polynomial (weights and exponents) saved by the authors' DRXQ agent (drxq.py: self.simple.save -> poly.fn).

Usage (needs h5py + numpy; both are already in the authors' Python 3.6 environment):
    python print_poly_weights.py Data5-0/poly.fn
    python print_poly_weights.py Data5-0/poly.fn --csv poly_drhq_low_trial5.csv

The file is HDF5 with two (11, 16) float32 datasets:
    model_weights/designed_layer_1/designed_layer_1/weights:0
    model_weights/designed_layer_1/designed_layer_1/exponents:0
Row i = action i, column j = input j. Labels below are copied from display() in drxq.py:
    rows    : E/W, E/EL, W/WL, EL/WL, NPL/SPL, NPL/S, N/NL, N/SPL, N/S, S/SL, NL/SL
    columns : 6 state variables of the first phase, 6 of the second phase, then 4 clearance flags
              (Queue, Approach, Wait, Speed, QLength, AvgWait | same six | FULL, PART, NO, PERM)
The score of action i is (sum over the 12 state terms (w*s)^p) times the product of the active flag terms, as in display().
We did not read networks.py: whether the weights start at 1.0 is taken from Algorithm 1 line 4 of the paper, not checked in code.
"""
import sys, argparse
import numpy as np

ROWS = ['E/W', 'E/EL', 'W/WL', 'EL/WL', 'NPL/SPL', 'NPL/S', 'N/NL', 'N/SPL', 'N/S', 'S/SL', 'NL/SL']
VARS = ['Queue', 'Approach', 'Wait', 'Speed', 'QLength', 'AvgWait']
COLS = ['A.' + v for v in VARS] + ['B.' + v for v in VARS] + ['FULL', 'PART', 'NO', 'PERM']


def load(path):
    import h5py
    found = {}
    with h5py.File(path, 'r') as f:
        def visit(name, obj):
            if isinstance(obj, h5py.Dataset) and 'designed_layer' in name:
                if name.endswith('weights:0'):
                    found['w'] = np.array(obj)
                elif name.endswith('exponents:0'):
                    found['p'] = np.array(obj)
        f.visititems(visit)
    if 'w' not in found or 'p' not in found:
        sys.exit("Could not find designed_layer weights/exponents in %s" % path)
    return found['w'], found['p']


def table(title, m):
    out = [title, "%-8s" % "" + "".join("%9s" % c for c in COLS)]
    for i, r in enumerate(ROWS):
        out.append("%-8s" % r + "".join("%9.3f" % v for v in m[i]))
    return "\n".join(out)


def summary(w, p):
    lines = []
    lines.append("shape weights %s, exponents %s -> %d parameters" % (w.shape, p.shape, w.size + p.size))
    for name, m in (("weights", w), ("exponents", p)):
        lines.append("%-9s min %.3f  max %.3f  mean %.3f  | entries differing from 1.0 by > 1e-3: %d of %d"
                     % (name, m.min(), m.max(), m.mean(), int((np.abs(m - 1.0) > 1e-3).sum()), m.size))
    lines.append("negative weights: %d | exponents <= 0: %d | non-finite values: %d"
                 % (int((w < 0).sum()), int((p <= 0).sum()), int((~np.isfinite(w)).sum() + (~np.isfinite(p)).sum())))
    return "\n".join(lines)


def to_csv(path, w, p):
    with open(path, 'w') as fh:
        fh.write("kind,action," + ",".join(COLS) + "\n")
        for kind, m in (("weight", w), ("exponent", p)):
            for i, r in enumerate(ROWS):
                fh.write("%s,%s," % (kind, r) + ",".join("%.6f" % v for v in m[i]) + "\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("poly")
    ap.add_argument("--csv", default=None)
    a = ap.parse_args()
    w, p = load(a.poly)
    assert w.shape == (11, 16) and p.shape == (11, 16), "unexpected shapes"
    print(summary(w, p)); print()
    print(table("WEIGHTS w (rows = actions, columns = inputs)", w)); print()
    print(table("EXPONENTS p", p))
    if a.csv:
        to_csv(a.csv, w, p); print("\nwrote", a.csv)
