#!/usr/bin/env python


import scraping


pg = scraping.get_pg_connection()

sql = (
    "INSERT INTO blacklisted_domains(fqdn) VALUES(%s)"
    "  ON CONFLICT(fqdn) DO NOTHING"
)


with open("data/top-1m.csv") as fh:
    domains = []
    with pg.cursor() as cur:
        for record in fh.readlines():
            (id, fqdn) = record.split(",")
            fqdn = fqdn.strip()
            print(id, fqdn)
            cur.execute(sql, (fqdn,))
        cur.connection.commit()
