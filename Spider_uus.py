import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from bs4 import BeautifulSoup


class HTTPMethodSpider(CrawlSpider):
    name = 'rik-spider'
    allowed_domains = ['rik.ee']
    start_urls = ['https://www.rik.ee']
    output_file = 'output.txt'
    url_methods_map = {}

    rules = (
        Rule(LinkExtractor(), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        if not response.url.startswith(self.start_urls[0]):
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        links = [a.get('href') for a in soup.find_all('a', href=True)]
        for link in links:
            if not link.startswith(self.start_urls[0]):
                continue
            yield scrapy.Request(link, method='HEAD', callback=self.parse_head)
            yield scrapy.Request(link, method='GET', callback=self.parse_get)
            yield scrapy.Request(link, method='POST', callback=self.parse_post)
            yield scrapy.Request(link, method='CONNECT', callback=self.parse_connect)
            yield scrapy.Request(link, method='OPTIONS', callback=self.parse_options)
            yield scrapy.Request(link, method='TRACE', callback=self.parse_trace)
            yield scrapy.Request(link, method='PATCH', callback=self.parse_patch)

    def parse_head(self, response):
        self.update_url_methods_map(response, 'HEAD')

    def parse_get(self, response):
        self.update_url_methods_map(response, 'GET')

    def parse_post(self, response):
        self.update_url_methods_map(response, 'POST')

    def parse_connect(self, response):
        self.update_url_methods_map(response, 'CONNECT')

    def parse_options(self, response):
        self.update_url_methods_map(response, 'OPTIONS')

    def parse_trace(self, response):
        self.update_url_methods_map(response, 'TRACE')

    def parse_patch(self, response):
        self.update_url_methods_map(response, 'PATCH')

    def update_url_methods_map(self, response, method):
        url = response.url
        status_code = response.status
        content_length = len(response.body)

        if url in self.url_methods_map:
            self.url_methods_map[url].add(method)
        else:
            self.url_methods_map[url] = {method}

        with open(self.output_file, 'a') as f:
            methods_str = ';'.join(self.url_methods_map[url])
            if status_code in [200, 301, 302, 303, 307, 400, 401, 403, 404, 405]:
                row = f'{methods_str}, {url}, {status_code}, {content_length}\n'
                f.write(row)
