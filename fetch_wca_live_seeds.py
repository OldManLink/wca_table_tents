import csv
import html
import os
import re
import sys
import time
from urllib.parse import quote

import requests


WCA_LIVE_API = "https://live.worldcubeassociation.org/api"
WCA_PERSON_API = "https://www.worldcubeassociation.org/api/v0/persons/{wca_id}"


ROUND_QUERY = """
query Round($id: ID!) {
  round(id: $id) {
    id
    name
    number
    competitionEvent {
      event {
        id
        name
      }
    }
    results {
      ranking
      advancing
      person {
        name
        wcaId
      }
    }
  }
}
"""


EVENT_NAME_OVERRIDES = {
    "222": "2x2",
    "333": "3x3",
    "444": "4x4",
    "555": "5x5",
    "666": "6x6",
    "777": "7x7",
    "333bf": "3BLD",
    "333fm": "FMC",
    "333oh": "OH",
    "333ft": "Feet",
    "clock": "Clock",
    "minx": "Megaminx",
    "pyram": "Pyraminx",
    "skewb": "Skewb",
    "sq1": "Square-1",
    "444bf": "4BLD",
    "555bf": "5BLD",
    "333mbf": "MBLD",
}


def fetch_round(round_id):
    payload = {
        "operationName": "Round",
        "variables": {"id": str(round_id)},
        "query": ROUND_QUERY,
    }

    response = requests.post(WCA_LIVE_API, json=payload, timeout=30)
    response.raise_for_status()

    data = response.json()

    if "errors" in data:
        raise RuntimeError(data["errors"])

    return data["data"]["round"]


def event_name_from_round(round_data):
    event = round_data["competitionEvent"]["event"]
    event_id = event["id"]
    return EVENT_NAME_OVERRIDES.get(event_id, event["name"])


def safe_filename(s):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", s).strip("_")


def get_country_code_from_wca_api(session, wca_id):
    url = WCA_PERSON_API.format(wca_id=quote(wca_id))
    response = session.get(url, timeout=30)
    response.raise_for_status()

    data = response.json()

    # WCA API commonly returns either:
    # { "person": { "country_iso2": "SE", ... } }
    # or directly { "country_iso2": "SE", ... }
    person = data.get("person", data)

    country_iso2 = person.get("country_iso2")
    if country_iso2:
        return country_iso2.upper()

    country = person.get("country")
    if isinstance(country, dict):
        for key in ("iso2", "iso2Code", "iso2_code", "id"):
            if country.get(key):
                return str(country[key]).upper()

    if isinstance(country, str) and len(country) == 2:
        return country.upper()

    return None


def get_country_code(session, wca_id):
    if not wca_id:
        return "??"

    try:
        code = get_country_code_from_wca_api(session, wca_id)
        if code:
            return code
    except Exception as e:
        print(f"Warning: could not fetch country for {wca_id}: {e}, file=sys.stderr")

    return "??"


def write_seed_csv(round_id, include_all=False, limit=None):
    round_data = fetch_round(round_id)
    event_name = event_name_from_round(round_data)

    results = round_data["results"]

    if include_all:
        selected = results
    else:
        selected = [r for r in results if r.get("advancing")]

    selected = sorted(selected, key=lambda r: r["ranking"])

    if limit is not None:
        selected = selected[:limit]

    output_name = f"{safe_filename(event_name)}_seeds.csv"

    session = requests.Session()
    session.headers.update({
        "User-Agent": "table-tents-helper/0.1"
    })

    rows = []

    for seed, result in enumerate(selected, start=1):
        person = result["person"]
        name = person["name"]
        wca_id = person.get("wcaId")

        country_code = get_country_code(session, wca_id)

        print(f"{seed:2d}. {country_code:2s}  {name}  ({wca_id or 'no WCA ID'})", file=sys.stderr)

        rows.append({
            "country_code": country_code,
            "competitor_name": name,
        })

        time.sleep(0.1)  # polite tiny pause

    with open(output_name, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["country_code", "competitor_name"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Event: {event_name}", file=sys.stderr)
    print(f"Saved: {output_name}", file=sys.stderr)

    print(output_name)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:", file=sys.stderr)
        print("  python3 fetch_wca_live_seeds.py ROUND_ID", file=sys.stderr)
        print("  python3 fetch_wca_live_seeds.py ROUND_ID --all, file=sys.stderr")
        print("  python3 fetch_wca_live_seeds.py ROUND_ID --limit 16", file=sys.stderr)
        sys.exit(1)

    round_id = sys.argv[1]
    include_all = "--all" in sys.argv

    limit = None
    if "--limit" in sys.argv:
        i = sys.argv.index("--limit")
        limit = int(sys.argv[i + 1])

    write_seed_csv(round_id, include_all=include_all, limit=limit)

