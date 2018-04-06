#!/usr/bin/env python

import sys
import time
import scraping


publisher = scraping.mq.TaskPublisher(
    scraping.config.rabbit_url,
    scraping.mq.ScrapingExchange,
    scraping.mq.ScrapingExchange.queues.url_unfiltered
)

for url in sys.argv[1:]:
    msg = dict(
        url=url,
        upload_ts=int(time.time()),
    )
    publisher.publish(msg, persistent=True)
