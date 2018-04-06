#!/usr/bin/env python

import sys
import json
import bs4
import scraping
from scraping import storage
from scraping.scraper import DocumentCache
from urllib.parse import urlparse, urljoin

redis = scraping.get_redis_connection()
pg = scraping.get_pg_connection()


def extract_links(document):
    links = []
    soup = bs4.BeautifulSoup(document["content"], "lxml")
    elements = soup.find_all("a")
    for el in elements:
        href = el.get("href", None)
        if not href: continue

        if href.startswith("#"):
            print("Anchor")
            continue

        text = el.text.strip()
        # if text:
        #     text = text.encode()

        parsed = urlparse(href)
        result = dict(
            url=urljoin(document["url"], href),
            text=text,
            attrs=dict(el.attrs),
            # FIXME: check against supported schemes
            is_external=(not not parsed.scheme),
            parent_url=document["url"],
            parent_url_id=document["url_id"],
        )

        links.append(result)

    return links


class URLExtractor(scraping.mq.TaskFilter):
    def __init__(self, *args, **kwargs):
        self.redis = kwargs.pop("redis", scraping.get_redis_connection())
        super().__init__(*args, **kwargs)
        self.document_cache = DocumentCache(self.redis)

    def process(self, ch, method, properties, body):
        body = json.loads(body)
        doc_id = body["cached_document_id"]
        cached = self.document_cache.get(doc_id)
        doc = json.loads(cached.decode("utf-8"))
        links = extract_links(doc)
        for ref in links:
            # TODO: split hits into ext and self refs, domain as well.
            # Currently we're ranking self-references
            parsed_ref = urlparse(ref["url"])
            with pg.cursor() as cur:
                domain_id = storage.store_domain(cur, parsed_ref.hostname)
                ref["url_id"] = storage.store_url(
                    cur,
                    domain_id,
                    parsed_ref.geturl()
                )
                storage.store_url_ref(cur, ref)
                cur.connection.commit()
            print(doc["url"], "->", ref)
        ch.basic_ack(delivery_tag=method.delivery_tag)


extractor = URLExtractor(
    [
        scraping.config.rabbit_url,
        scraping.mq.ScrapingExchange,
        scraping.mq.ScrapingExchange.queues.document,
    ],
    [
        scraping.config.rabbit_url,
        scraping.mq.ScrapingExchange,
        scraping.mq.ScrapingExchange.queues.url_unfiltered,
    ],
    redis=redis
)

extractor.start()
