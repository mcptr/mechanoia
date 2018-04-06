import json
import time
import requests
import scraping
from urllib.parse import urlparse


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

    def is_domain_throttled(self, fqdn):
        return False
        return self.redis.get(self._throttle_prefix + fqdn)

    def throttle_domain(self, fqdn, sec):
        self.redis.setex(self._throttle_prefix + fqdn, sec, 1)

    def process(self, ch, method, properties, body):
        body = json.loads(body)
        parsed = urlparse(body["url"])
        fqdn = parsed.netloc.split(":")[0]
        ok = True

        if self.is_domain_throttled(fqdn):
            ok = False
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
            print(r.content)
            body.update(
                document=dict(),
                fetch_ts=int(time.time())
            )
        return r

