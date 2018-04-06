#!/usr/bin/env python

import sys
import scraping.scraper

redis = scraping.get_redis_connection()

scraper = scraping.scraper.URLFetch(
    [
        scraping.config.rabbit_url,
        scraping.mq.ScrapingExchange,
        scraping.mq.ScrapingExchange.queues.document_head,
    ],
    [
        scraping.config.rabbit_url,
        scraping.mq.ScrapingExchange,
        scraping.mq.ScrapingExchange.queues.document,
    ],
    redis=redis
)


scraper.start()
