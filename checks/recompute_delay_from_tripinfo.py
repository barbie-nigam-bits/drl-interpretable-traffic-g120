"""
Recompute the authors' delay metrics from SUMO's tripinfo.xml (independent check of traci_env.get_delay).

Usage (from ~/StateStreetSumo, after a run):
    python <path>/recompute_delay_from_tripinfo.py Data0-0/tripinfo.xml --file 0
    # or give the windows explicitly:  --rush 33900 --dead 0

Reproduces the authors' printed numbers AND the corrected dead-hour average.
Authors' get_delay() returns  dh_loss / rh_trips  (rush-hour trip count) on its last line;
the dead-hour total should be divided by the dead-hour trip count (dh_trips).
Works on Python 3.6+.
"""
import sys, argparse
import xml.etree.ElementTree as ET

ap = argparse.ArgumentParser()
ap.add_argument("tripinfo")
ap.add_argument("--file", type=int, default=0, help="demand index 0=Low 1=Med 2=High (reads shared.py)")
ap.add_argument("--rush", type=float, default=None)
ap.add_argument("--dead", type=float, default=None)
a = ap.parse_args()

rush, dead = a.rush, a.dead
if rush is None or dead is None:
    try:
        sys.path.insert(0, ".")
        import shared                      # authors' settings file (run from the repo folder)
        rush = shared.rush[a.file] if rush is None else rush
        dead = shared.dead[a.file] if dead is None else dead
        print("rush/dead start (from shared.py): %s / %s" % (rush, dead))
    except Exception as e:
        sys.exit("Could not read shared.py (%s). Pass --rush and --dead explicitly." % e)

trips = 0; loss = 0.0; max_delay = 0.0
rh_trips = rh_loss = dh_trips = dh_loss = 0
for _, el in ET.iterparse(a.tripinfo):
    if el.tag != "tripinfo":
        continue
    tl = float(el.get("timeLoss")); dep = float(el.get("depart"))
    trips += 1; loss += tl; max_delay = max(max_delay, tl)
    if rush <= dep <= rush + 3600: rh_loss += tl; rh_trips += 1
    if dead <= dep <= dead + 3600: dh_loss += tl; dh_trips += 1
    el.clear()

print("trips                         :", trips)
print("loss  (mean timeLoss, s)      : %.6f" % (loss / trips))
print("max delay (s)                 : %.1f" % max_delay)
print("rush-hour trips / mean loss   : %d / %.6f" % (rh_trips, rh_loss / rh_trips))
print("dead-hour trips               : %d" % dh_trips)
print("dead-hour mean, authors' formula (dh_loss / rh_trips) : %.6f" % (dh_loss / rh_trips))
print("dead-hour mean, corrected (dh_loss / dh_trips)        : %.6f" % (dh_loss / dh_trips))
