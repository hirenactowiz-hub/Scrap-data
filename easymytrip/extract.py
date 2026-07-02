import json

SRC = r"C:\Users\hiren.chauhan\Desktop\HirenGit\easymytrip\easemytrip.json"          # input  — place in the same folder
OUT = r"C:\Users\hiren.chauhan\Desktop\HirenGit\easymytrip\easemytrip_output.json"   # output — written to the same folder

# ── helpers ──────────────────────────────────────────────────────────────────

def fmt_duration(dur):
    """'00h 55m' → '0:55:00'"""
    h, m = 0, 0
    if dur:
        parts = dur.replace("h", "").replace("m", "").split()
        h = int(parts[0]) if len(parts) >= 1 else 0
        m = int(parts[1]) if len(parts) >= 2 else 0
    return f"{h}:{m:02d}:00"


def fmt_date_day(dt_str):
    """'Mon-01Jun2026' → ('01Jun2026', 'Monday')"""
    day_map = {
        "Mon": "Monday",  "Tue": "Tuesday",  "Wed": "Wednesday",
        "Thu": "Thursday","Fri": "Friday",   "Sat": "Saturday","Sun": "Sunday",
    }
    if not dt_str or "-" not in dt_str:
        return dt_str, ""
    abbr, date_part = dt_str.split("-", 1)
    return date_part, day_map.get(abbr, abbr)


def fmt_terminal(t):
    """'1' → 'Terminal - 1', None/'' → 'No Terminal Data Given'"""
    return f"Terminal - {t}" if t else "No Terminal Data Given"


# ── main ─────────────────────────────────────────────────────────────────────

with open(SRC, encoding="utf-8") as f:
    data = json.load(f)

# LegKey → leg-detail lookup
leg_map = {v["LegKey"]: v for v in data["dctFltDtl"].values()}

# Airport code → city name  (e.g. "DEL" → "New Delhi")
airport_city = data.get("A", {})

results = []

for itinerary in data["j"][0]["s"]:
    leg_keys = itinerary.get("segKeyArr") or []

    # "1-Stop|6525|44|DEL-JAI-NMI||" → "1-Stop"
    sd = itinerary.get("SD", "")
    stops = sd.split("|")[0] if sd else ""

    flight_details = []
    for lk in leg_keys:
        leg = leg_map.get(lk)
        if not leg:
            continue
        
        date_str, day_str = fmt_date_day(leg.get("DDT"))
        dep_code = leg.get("OG", "")
        arr_code = leg.get("DT", "")

        flight_details.append({
            "flightId":   f'{leg.get("AC", "")}{leg.get("FN", "")}',
            "airline":    leg.get("FlightName", ""),
            "date":       date_str,
            "day":        day_str,
            "cabinClass": leg.get("CB", ""),
            "duration":   fmt_duration(leg.get("DUR")),
            "departure": {
                "city":     airport_city.get(dep_code, dep_code),
                "time":     leg.get("DTM", ""),
                "terminal": fmt_terminal(leg.get("DTER")),
            },
            "arrival": {
                "city":     airport_city.get(arr_code, arr_code),
                "time":     leg.get("ATM", ""),
                "terminal": fmt_terminal(leg.get("ATER")),
            },
        })

    results.append({
        "stops":   stops,
        "flight_details":    flight_details,
        "pricing": {
            "baseFare":   itinerary.get("AP",  0),
            "taxAndFees": itinerary.get("APT", 0),
            "totalFare":  itinerary.get("TF",  0),
        },
    })

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"Done — {len(results)} itineraries written to '{OUT}'")