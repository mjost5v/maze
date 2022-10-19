import scrapy

class MazeScrapy(scrapy.Spider):
    name = 'maze'

    def start_requests(self):
        urls = ['http://www.cs.loyola.edu/~isaacman/403/maze/']
        for url in urls:
            if 'maze' in url:
                yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        title = response.css('title::text').get()
        items = response.css('ul li::text').getall() + response.css('span::text').getall()
        yield {
            'title': title,
            'items': items
        }
        next_pages = response.css('a::attr(href)').getall()
        for next_page in next_pages:
            url = response.urljoin(next_page)
            if 'maze' not in url:
                continue
            yield scrapy.Request(url, callback=self.parse)


