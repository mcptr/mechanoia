#!/usr/bin/env python


import json
import time
import scraping
from urllib.parse import urlparse


redis = scraping.get_redis_connection()
pg = scraping.get_pg_connection()


def is_scheme_supported(parsed):
    supported = (parsed.scheme in ["http", "https"])
    if not supported:
        print("Unsupported scheme", parsed.scheme)
    return supported


def is_domain_blacklisted(fqdn):
    sql = (
        "SELECT id FROM blacklisted_domains"
        "  WHERE fqdn=%s"
    )

    with pg.cursor() as cur:
        cur.execute(sql, (fqdn,))
        r = cur.fetchone()
        if r:
            print("Blacklisted", fqdn)
        return r


class URLFilter(scraping.mq.TaskFilter):
    def process(self, ch, method, properties, body):
        body = json.loads(body)
        parsed = urlparse(body["url"])
        fqdn = parsed.netloc.split(":")[0]
        filtered_out = False
        if (not is_scheme_supported(parsed) or
            is_domain_blacklisted(fqdn)):
            filtered_out = True

        if not filtered_out:
            print("OK:", parsed.geturl())
            body.update(filter_ts=int(time.time()))
            self.publisher.publish(body, persistent=True)
        ch.basic_ack(delivery_tag=method.delivery_tag)


flt = URLFilter(
    [
        scraping.config.rabbit_url,
        scraping.mq.ScrapingExchange,
        scraping.mq.ScrapingExchange.queues.url_unfiltered,
    ],
    [
        scraping.config.rabbit_url,
        scraping.mq.ScrapingExchange,
        scraping.mq.ScrapingExchange.queues.url_filtered,
    ],
)

flt.start()
