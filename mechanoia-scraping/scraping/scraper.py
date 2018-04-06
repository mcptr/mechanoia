import json
import time
import requests
import hashlib
import scraping
from urllib.parse import urlparse


class DocumentCache:
    def __init__(self, redis=None):
        self.redis = (redis or scraping.get_redis_connection())

    def _mk_key(self, doc):
        doc_id = hashlib.md5(doc["url"].encode("utf-8")).hexdigest()
        return "doc:%s" % doc_id

    def store(self, doc, ttl=(3600 * 24 * 7)):
        doc_id = self._mk_key(doc)
        self.redis.setex(doc_id, ttl, json.dumps(doc))
        print("DocumentCache:", doc_id)
        return doc_id

    def get(self, id):
        return self.redis.get(id)


class Scraper:
    def __init__(self, **kwargs):
        headers = {
            "User-Agent": scraping.config.scraper_ua,
        }
        headers.update(kwargs)

    def head(self, url, **kwargs):
        return requests.head(url, **kwargs)

    def get(self, url, **kwargs):
        return requests.get(url, **kwargs)


class _URLFetch(scraping.mq.TaskFilter):
    _throttle_prefix = "fetch.throttle:"
    _throttle_intval_sec = 5

    def __init__(self, *args, **kwargs):
        self.redis = kwargs.pop("redis", scraping.get_redis_connection())
        super().__init__(*args, **kwargs)
        self.scraper = Scraper()
        self.document_cache = DocumentCache(self.redis)

    def is_domain_throttled(self, fqdn):
        return self.redis.get(self._throttle_prefix + fqdn)

    def throttle_domain(self, fqdn, sec):
        self.redis.setex(self._throttle_prefix + fqdn, sec, 1)

    def process(self, ch, method, properties, body):
        body = json.loads(body)
        parsed = urlparse(body["url"])
        fqdn = parsed.netloc.split(":")[0]
        ok = True

        if self.is_domain_throttled(fqdn):
            # ok = False
            print("Throttled:", fqdn)

        if ok:
            self.throttle_domain(fqdn, self._throttle_intval_sec)
            r = self.fetch(parsed, body)
            if r.ok:
                self.publisher.publish(body, persistent=True)
        ch.basic_ack(delivery_tag = method.delivery_tag)


class URLFetchHEAD(_URLFetch):
    _throttle_prefix = "fqdn.throttled.head:"
    _throttle_intval_sec = 5
    _response_key = "headers"

    def fetch(self, parsed, body):
        url = parsed.geturl()
        r = self.scraper.head(url, allow_redirects=1)
        print("HEAD", r.status_code, url)
        if r.ok:
            body.update(
                headers=dict(r.headers),
                fetch_head_ts=int(time.time())
            )
        return r


class URLFetch(_URLFetch):
    _throttle_prefix = "fqdn.throttled:"
    _throttle_intval_sec = 5
    _response_key = "document"

    def fetch(self, parsed, body):
        url = parsed.geturl()
        r = self.scraper.get(url, allow_redirects=1)
        print("GET", r.status_code, url)
        if r.ok:
            body.update(
                fetch_ts=int(time.time())
            )

            doc = body.copy()
            doc.update(content=r.text)
            doc_id = self.document_cache.store(doc)
            body.update(cached_document_id=doc_id)
        return r

