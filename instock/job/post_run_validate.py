#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import os
import pymysql

DB_HOST = os.environ.get('db_host', '127.0.0.1')
DB_USER = os.environ.get('db_user', 'root')
DB_PASSWORD = os.environ.get('db_password', 'root')
DB_NAME = os.environ.get('db_database', 'instockdb')
DB_PORT = int(os.environ.get('db_port', '3306'))

CRITICAL_TABLES = [
    'cn_stock_selection',
    'cn_stock_indicators',
    'cn_stock_indicators_buy',
    'cn_stock_indicators_sell',
    'cn_stock_pattern',
]


def table_exists(cur, table):
    cur.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=%s AND table_name=%s", (DB_NAME, table))
    return cur.fetchone()[0] == 1


def row_count_by_date(cur, table, dt):
    cur.execute(f"SELECT COUNT(*) FROM `{table}` WHERE `date`=%s", (dt,))
    return int(cur.fetchone()[0])


def main():
    today = datetime.date.today().strftime('%Y-%m-%d')
    failed = []
    details = []

    conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME, port=DB_PORT, charset='utf8mb4')
    try:
        cur = conn.cursor()
        for tb in CRITICAL_TABLES:
            if not table_exists(cur, tb):
                failed.append(tb)
                details.append(f"[MISS] table not exists: {tb}")
                continue
            cnt = row_count_by_date(cur, tb, today)
            details.append(f"[OK] {tb} rows(date={today})={cnt}")
            if tb in ('cn_stock_selection', 'cn_stock_indicators') and cnt == 0:
                failed.append(tb)
                details.append(f"[FAIL] {tb} has 0 rows on {today}")
    finally:
        conn.close()

    print('\n'.join(details))
    if failed:
        print(f"VALIDATION_FAILED: {sorted(set(failed))}")
        raise SystemExit(2)
    print('VALIDATION_OK')


if __name__ == '__main__':
    main()
