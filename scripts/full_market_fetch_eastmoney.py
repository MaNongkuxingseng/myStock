#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fetch FULL A-share snapshot from Eastmoney push2 (no key).
Outputs a CSV/JSON with latest quotes and basic fields.

This is the Phase-A (fastest) market data source used to backfill instockdb.cn_stock_selection daily rows.
"""

from __future__ import annotations

import csv
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

import requests

BASE_URL = "https://push2.eastmoney.com/api/qt/clist/get"
UT = "bd1d9ddb04089700cf9c27f6f7426281"  # public ut used by Eastmoney web
FS = "m:0+t:6,m:0+t:13,m:1+t:2,m:1+t:23"  # A-share main boards + ChiNext/STAR
FIELDS = "f12,f14,f2,f3,f4,f5,f6,f15,f16,f17,f18,f10,f8,f9,f23,f20,f21,f13"


_S = requests.Session()
_S.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123 Safari/537.36",
    "Accept": "application/json,text/plain,*/*",
    "Connection": "keep-alive",
})


def fetch_page(pn: int, pz: int = 200, retries: int = 5) -> Dict[str, Any]:
    params = {
        "pn": pn,
        "pz": pz,
        "po": 1,
        "np": 1,
        "ut": UT,
        "fltt": 2,
        "invt": 2,
        "fid": "f3",
        "fs": FS,
        "fields": FIELDS,
    }
    last = None
    for i in range(retries):
        try:
            r = _S.get(BASE_URL, params=params, timeout=15)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            last = e
            time.sleep(0.6 * (i + 1))
    raise last


def main():
    out_dir = Path(__file__).resolve().parent.parent / "data" / "eastmoney"
    out_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    all_rows: List[Dict[str, Any]] = []
    page = 1
    total = None

    while True:
        j = fetch_page(page, 200)
        data = j.get("data") or {}
        if total is None:
            total = int(data.get("total") or 0)
        diff = data.get("diff") or []
        if not diff:
            break
        all_rows.extend(diff)
        if len(all_rows) >= total:
            break
        page += 1
        time.sleep(0.15)

    meta = {
        "fetched_at": datetime.now().isoformat(timespec="seconds"),
        "total": total,
        "rows": len(all_rows),
        "source": "eastmoney_push2_clist",
    }

    json_path = out_dir / f"a_share_snapshot_{ts}.json"
    csv_path = out_dir / f"a_share_snapshot_{ts}.csv"

    with json_path.open("w", encoding="utf-8") as f:
        json.dump({"meta": meta, "data": all_rows}, f, ensure_ascii=False)

    # CSV
    cols = [
        "code",
        "name",
        "price",
        "pct",
        "chg",
        "vol",
        "amt",
        "high",
        "low",
        "open",
        "preclose",
        "turnover",
        "pe_ttm",
        "amp",
        "mktcap",
        "float_mktcap",
        "market",
    ]

    def map_row(r: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "code": r.get("f12"),
            "name": r.get("f14"),
            "price": r.get("f2"),
            "pct": r.get("f3"),
            "chg": r.get("f4"),
            "vol": r.get("f5"),
            "amt": r.get("f6"),
            "high": r.get("f15"),
            "low": r.get("f16"),
            "open": r.get("f17"),
            "preclose": r.get("f18"),
            "turnover": r.get("f8"),
            "pe_ttm": r.get("f9"),
            "amp": r.get("f10"),
            "mktcap": r.get("f20"),
            "float_mktcap": r.get("f21"),
            "market": r.get("f13"),
        }

    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in all_rows:
            w.writerow(map_row(r))

    print(f"OK fetched rows={len(all_rows)} total={total}")
    print(f"JSON: {json_path}")
    print(f"CSV : {csv_path}")


if __name__ == "__main__":
    main()
