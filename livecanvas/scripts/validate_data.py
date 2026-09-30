#!/usr/bin/env python3
"""Structural checks only: this does not fact-check the source websites."""
import argparse
import datetime as dt
import json
import math
import re
import sys
from zoneinfo import ZoneInfo


def validate(data, allow_demo=False):
    errors, warnings, summaries = [], [], []

    def require(ok, message):
        if not ok:
            errors.append(message)

    def date(value):
        if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            raise ValueError(f"Invalid ISO date: {value!r}")
        return dt.date.fromisoformat(value)

    def number(value):
        return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)

    require(data.get("schemaVersion") == 1, "schemaVersion must be 1")
    require(isinstance(data.get("demo"), bool), "demo must be boolean")
    demo = data.get("demo", False)
    require(not demo or allow_demo, "Synthetic demo blocked; use --allow-demo only for testing")
    for key in ("title", "subtitle", "footnote"):
        require(isinstance(data.get(key), str) and bool(data[key].strip()), f"Missing {key}")
    provenance = data["provenance"]
    require(provenance in ("observed", "reconstructed", "reanalysis", "forecast", "synthetic"), "Unknown provenance")
    require((provenance == "synthetic") == demo, "Synthetic provenance and demo flag must agree")
    period, metric = data["period"], data["metric"]
    start, end, asof = date(period["start"]), date(period["end"]), date(data["asOf"])
    require(start < end, "Period must have positive duration")
    require(provenance == "forecast" or end <= asof, "Historical period ends after asOf")
    ZoneInfo(period["timezone"])
    require(bool(period.get("definition")), "Missing period definition")
    granularity = period["granularity"]
    require(granularity in ("daily", "monthly", "yearly"), "Unsupported granularity")
    require(metric.get("kind") in ("market_cap", "temperature", "other"), "Unknown metric kind")
    require(bool(metric.get("unit")) and bool(metric.get("label")), "Missing metric unit/label")
    if metric.get("kind") == "market_cap":
        require(bool(re.fullmatch(r"[A-Z]{3}", metric.get("currency", ""))), "Market cap requires currency")
    lo, hi = data["display"]["yDomain"]
    require(number(lo) and number(hi) and lo < hi, "Invalid yDomain")
    decimals = data["display"]["decimals"]
    require(type(decimals) is int and 0 <= decimals <= 6, "Invalid decimals")
    sources = data["sources"]
    ids = [s["id"] for s in sources]
    require(bool(ids) and len(ids) == len(set(ids)), "Source IDs missing/duplicated")
    for source in sources:
        for key in ("id", "title", "url", "accessedAt", "method"):
            require(isinstance(source.get(key), str) and bool(source[key].strip()), f"Source missing {key}")
        accessed = date(source["accessedAt"])
        require(accessed <= asof, "Source accessedAt later than asOf")
        require(demo or bool(re.match(r"https?://[^/\s]+", source["url"])), "Real data requires HTTP(S) source")
    series_ids = [s["id"] for s in data["series"]]
    require(bool(series_ids) and len(set(series_ids)) == len(series_ids), "Series IDs missing/duplicated")
    for series in data["series"]:
        require(bool(series.get("name")), "Missing series name")
        require(bool(re.fullmatch(r"#[0-9a-fA-F]{6}", series.get("color", ""))), "Invalid series color")
        points, valid, dates = series["points"], [], []
        for point in points:
            day = date(point["date"])
            require(start <= day <= end, f"Point outside period: {day}")
            require(not dates or day > dates[-1], f"Dates not strictly increasing: {day}")
            dates.append(day)
            require(point.get("sourceId") in ids, f"Unknown source at {day}")
            value = point["value"]
            if value is not None:
                require(number(value), f"Nonfinite/non-numeric value at {day}")
                if number(value):
                    require(lo <= value <= hi, f"Value clipped by yDomain at {day}")
                    require(metric["kind"] != "market_cap" or value >= 0, "Negative market cap")
                    valid.append(point)
        require(len(valid) >= 2, f"{series['id']}: need at least two valid observations")
        if granularity == "monthly":
            buckets = [(d.year, d.month) for d in dates]
            expected = []
            y, m = start.year, start.month
            while (y, m) <= (end.year, end.month):
                expected.append((y, m))
                y, m = (y + 1, 1) if m == 12 else (y, m + 1)
            require(len(buckets) == len(set(buckets)), "Monthly series has multiple observations per month")
            require(set(buckets) == set(expected), "Missing monthly buckets; insert explicit null observations")
        elif granularity == "yearly":
            years = [d.year for d in dates]
            require(len(years) == len(set(years)), "Yearly series has duplicate years")
            require(set(years) == set(range(start.year, end.year + 1)), "Missing yearly buckets; insert nulls")
        if any(p["value"] is None for p in points):
            warnings.append(f"{series['id']}: missing observations; show gaps")
        if granularity == "daily" and any((b-a).days > 7 for a,b in zip(dates, dates[1:])):
            warnings.append(f"{series['id']}: long daily gaps; inspect expected trading/calendar cadence")
        if valid:
            a, b = valid[0], valid[-1]
            summary = dict(series=series["id"], first=a, last=b, delta=b["value"]-a["value"], count=len(valid))
            if metric["kind"] != "temperature" and a["value"] != 0:
                summary["changePercent"] = (b["value"]/a["value"]-1)*100
            summaries.append(summary)
    return dict(ok=not errors, errors=errors, warnings=warnings, summaries=summaries, factCheck="not_performed_by_validator")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data")
    parser.add_argument("--allow-demo", action="store_true")
    args = parser.parse_args()
    try:
        with open(args.data, encoding="utf-8") as f:
            result = validate(json.load(f), args.allow_demo)
    except (ValueError, KeyError, TypeError, OSError) as exc:
        result = dict(ok=False, errors=[str(exc)], factCheck="not_performed_by_validator")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["ok"] else 1)
