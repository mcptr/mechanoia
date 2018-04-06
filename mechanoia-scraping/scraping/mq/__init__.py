from .mq import Queue, TaskPublisher, TaskConsumer, TaskFilter



class URLQueues:
    url_unfiltered = mq.Queue("url_unfiltered", durable=True, auto_delete=False)
    url_filtered = mq.Queue("url_filtered", durable=True, auto_delete=False)
    document_head = mq.Queue("document_head", durable=True, auto_delete=False)
    document = mq.Queue("document", durable=True, auto_delete=False)


class ScrapingExchange:
    exchange = "scraping"
    exchange_type = "direct"
    queues = URLQueues()

