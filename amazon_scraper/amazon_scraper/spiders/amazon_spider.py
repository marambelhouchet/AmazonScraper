import scrapy

class AmazonProductSpider(scrapy.Spider):
    name = "amazon_products"
    
    start_urls = [
        'https://www.amazon.fr/b?node=2805688031&ref=lp_210965031_nr_n_2',
        'https://www.amazon.fr/gp/browse.html?rw_useCurrentProtocol=1&node=2953222031&ref_=beauty_leftnav_produitsbronzantssolaires',
        'https://www.amazon.fr/b?node=211031031&ref=lp_211020031_nr_n_0'
    ]

    def parse(self, response):
        category = response.meta.get('category')

        # Extract product data from the current page
        for product in response.css('div.s-result-item'):
            product_name = product.css('span.a-size-base-plus.a-color-base.a-text-normal::text').get()
            price = product.css('span.a-price span.a-offscreen::text').get()
            product_url = response.urljoin(product.css('a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal::attr(href)').get())

            yield {
                'category': category,
                'product_name': product_name,
                'price': price,
                'product_url': product_url
            }

    def start_requests(self):
        urls = {
            'parfum': 'https://www.amazon.fr/b?node=2805688031&ref=lp_210965031_nr_n_2',
            'solaire': 'https://www.amazon.fr/gp/browse.html?rw_useCurrentProtocol=1&node=2953222031&ref_=beauty_leftnav_produitsbronzantssolaires',
            'coffres': 'https://www.amazon.fr/b?node=211031031&ref=lp_211020031_nr_n_0'
        }
        
        for category, url in urls.items():
            if category == 'coffres':
                for page in range(1, 10):
                    page_url = f"{url}&page={page}"
                    yield scrapy.Request(url=page_url, callback=self.parse, meta={'category': category})
            elif category == 'solaire':
                for page in range(1, 14):
                    page_url = f"{url}&page={page}"
                    yield scrapy.Request(url=page_url, callback=self.parse, meta={'category': category})
            else:
                for page in range(1, 101):
                    page_url = f"{url}&page={page}"
                    yield scrapy.Request(url=page_url, callback=self.parse, meta={'category': category})
