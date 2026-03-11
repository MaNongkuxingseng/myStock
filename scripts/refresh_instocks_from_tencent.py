#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Backfill instockdb.cn_stock_selection for a given trading date using Tencent realtime API.

Steps:
1) Read all codes from instockdb.cn_stock_selection (distinct code).
2) Fetch realtime quote in batches via qt.gtimg.cn.
3) Upsert rows into cn_stock_selection for target date.

Note: Tencent API provides realtime fields; we store snapshot as daily row.
"""

from __future__ import annotations

import math
import time
from datetime import date, datetime
from typing import Dict, List, Tuple

import pymysql
import requests

DB = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "785091",
    "database": "instockdb",
    "charset": "utf8mb4",
}


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def market_code(code6: str) -> str:
    return ("sh" if code6.startswith("6") else "sz") + code6


def fetch_batch(codes6: List[str]) -> Dict[str, Dict]:
    q = ",".join(market_code(c) for c in codes6)
    url = f"http://qt.gtimg.cn/q={q}"
    r = requests.get(url, timeout=8)
    r.raise_for_status()
    out: Dict[str, Dict] = {}
    for line in r.text.split("\n"):
        line = line.strip()
        if not line or "=" not in line:
            continue
        try:
            body = line.split("=", 1)[1].strip().strip('";')
            parts = body.split("~")
            if len(parts) < 35:
                continue
            name = parts[1]
            code = parts[2]
            price = float(parts[3] or 0)
            preclose = float(parts[4] or 0)
            openp = float(parts[5] or 0)
            vol = int(float(parts[6] or 0))
            amount = float(parts[37] or 0) if len(parts) > 37 else 0
            high = float(parts[33] or 0)
            low = float(parts[34] or 0)
            chg = price - preclose
            pct = (chg / preclose * 100) if preclose else 0
            out[code] = {
                "name": name,
                "new_price": price,
                "change_rate": pct,
                "volume": vol,
                "deal_amount": amount,
                "high_price": high,
                "low_price": low,
                "pre_close_price": preclose,
                "open_price": openp,
                "fetched_time": parts[30] if len(parts) > 30 else "",
            }
        except Exception:
            continue
    return out


def main():
    target_date = date.today().isoformat()
    print("target_date", target_date)

    conn = pymysql.connect(**DB)
    cur = conn.cursor()

    cur.execute("SELECT DISTINCT code FROM cn_stock_selection")
    codes = [row[0] for row in cur.fetchall() if row and row[0]]
    codes = [str(c).zfill(6) for c in codes]
    print("codes", len(codes))

    fetched = {}
    ok = 0
    total = len(codes)

    for i, batch in enumerate(chunks(codes, 200), 1):
        try:
            data = fetch_batch(batch)
            fetched.update(data)
            ok += len(data)
        except Exception as e:
            # continue
            pass
        if i % 5 == 0:
            print("progress", min(i * 200, total), "/", total, "ok", ok)
        time.sleep(0.12)

    print("fetched", len(fetched))

    # minimal upsert: only a handful of columns guaranteed exist
    sql = (
        "INSERT INTO cn_stock_selection (date, code, name, new_price, change_rate, volume, deal_amount, high_price, low_price, pre_close_price) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
        "ON DUPLICATE KEY UPDATE name=VALUES(name), new_price=VALUES(new_price), change_rate=VALUES(change_rate), volume=VALUES(volume), deal_amount=VALUES(deal_amount), high_price=VALUES(high_price), low_price=VALUES(low_price), pre_close_price=VALUES(pre_close_price)"
    )

    rows = []
    for code, d in fetched.items():
        rows.append(
            (
                target_date,
                code,
                d.get("name"),
                d.get("new_price"),
                d.get("change_rate"),
                d.get("volume"),
                d.get("deal_amount"),
                d.get("high_price"),
                d.get("low_price"),
                d.get("pre_close_price"),
            )
        )

    if rows:
        cur.executemany(sql, rows)
        conn.commit()

    # verify max(date)
    cur.execute("SELECT COUNT(*), MIN(date), MAX(date) FROM cn_stock_selection")
    print("cn_stock_selection", cur.fetchone())

    conn.close()


if __name__ == "__main__":
    main()
