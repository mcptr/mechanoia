#!/usr/bin/env python

import sys
import scraping.scraper

redis = scraping.get_redis_connection()

scraper = scraping.scraper.URLFetchHEAD(
    [
        scraping.config.rabbit_url,
        scraping.mq.ScrapingExchange,
        scraping.mq.ScrapingExchange.queues.url_filtered,
    ],
    [
        scraping.config.rabbit_url,
        scraping.mq.ScrapingExchange,
        scraping.mq.ScrapingExchange.queues.document_head,
    ],
    redis=redis
)


scraper.start()
