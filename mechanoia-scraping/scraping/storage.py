
def store_domain(cur, fqdn):
    sql = (
        "INSERT INTO domains AS d(fqdn, hits)"
        "  VALUES(%s, 1)"
        "  ON CONFLICT(fqdn) DO UPDATE SET hits = d.hits + 1"
        "  RETURNING id"
    )

    cur.execute(sql, (fqdn,))
    r = cur.fetchone()
    return r.id if r else None


def store_url(cur, domain_id, url):
    sql = (
        "INSERT INTO urls as u(domain_id, url, hits)"
        "  VALUES(%s, %s, 1)"
        "  ON CONFLICT(url) DO UPDATE SET hits = u.hits + 1"
        "  RETURNING id"
    )

    cur.execute(sql, (domain_id, url,))
    r = cur.fetchone()
    return r.id if r else None


def store_url_ref(cur, ref):
    sql = (
        "INSERT INTO url_refs as ur(from_id, to_id, is_external, hits, text)"
        "  VALUES(%s, %s, %s, 1, %s)"
        "  ON CONFLICT (from_id, to_id, text) DO UPDATE SET hits = ur.hits + 1"
        "  RETURNING id"
    )

    cur.execute(
        sql,
        (
            ref["parent_url_id"],
            ref["url_id"],
            ref["is_external"],
            ref["text"][:512]
        )
    )
    r = cur.fetchone()
    return r.id if r else None


