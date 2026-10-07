"""
Sanity checks on numbers quoted in the paper.
Usage:  python checks/table1_and_arithmetic_checks.py [path/to/StateStreetSumo/utils]
If a path is given, also sums the 5-minute 'Vehicle Total' column of Low.txt / Med.txt / High.txt.
"""
import sys, os, re, json
out = {}
# ---- Table 1 (paper): total vehicles and average arrival rate (veh/s)
table1 = {"Low": (45112, 1.04), "Medium": (51298, 1.19), "High": (61261, 1.42)}
print("Table 1: implied observation window = Total / AvgRate")
for k, (tot, rate) in table1.items():
    secs = tot / rate
    out[k] = {"total": tot, "avg_rate": rate, "implied_seconds": secs, "implied_hours": secs / 3600,
              "rate_if_14h": tot / (14 * 3600), "rate_if_12h": tot / (12 * 3600)}
    print(f"  {k:6s} {tot:6d}/{rate} = {secs:8.0f} s = {secs/3600:5.2f} h | rate@14h={tot/(14*3600):.2f} rate@12h={tot/(12*3600):.2f}")

# ---- other arithmetic quoted in the paper
out["cmaes_600_episodes"] = 25 * 24            # "25 epochs (600 episodes)" with 24 episodes/epoch
out["params_352"] = 11 * (2 * 12 + 8)
out["params_256"] = 8 * (2 * 12 + 8)
out["episodes_4000_in_years_if_1_episode_is_1_day"] = 4000 / 365
print("25 epochs x 24 ep =", out["cmaes_600_episodes"], "| 11*(2*12+8) =", out["params_352"],
      "| 8*(2*12+8) =", out["params_256"], "| 4000 days =", round(4000 / 365, 1), "years")

# ---- optional: parse repo demand files
if len(sys.argv) > 1:
    d = sys.argv[1]
    for name in ("Low", "Med", "High"):
        path = os.path.join(d, f"{name}.txt")
        if not os.path.exists(path): print("missing", path); continue
        rows = []
        for line in open(path, encoding="utf-8", errors="ignore"):
            m = re.match(r"\s*(\d{1,2}:\d{2}\s*[AP]M)\b(.*)", line)
            if m:
                nums = re.findall(r"\d+", m.group(2).replace(m.group(1), ""))
                if nums: rows.append((m.group(1), int(nums[-1])))     # last column = Vehicle Total
        tot = sum(v for _, v in rows)
        out["file_" + name] = {"bins": len(rows), "first": rows[0][0] if rows else None,
                               "last": rows[-1][0] if rows else None, "sum": tot,
                               "hours_covered": len(rows) * 5 / 60}
        print(f"{name}.txt: {len(rows)} bins ({len(rows)*5/60:.1f} h) {rows[0][0]}..{rows[-1][0]}  SUM = {tot}")
json.dump(out, open(os.path.join(os.path.dirname(__file__), "..", "results", "table1_and_arithmetic_checks.json"), "w"), indent=2)
