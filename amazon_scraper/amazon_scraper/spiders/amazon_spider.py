import scrapy

class AmazonProductSpider(scrapy.Spider):
    name = "amazon_products"
    start_urls = [
        'https://www.amazon.fr/b?node=2805688031&ref=lp_210965031_nr_n_2',
        'https://www.amazon.fr/gp/browse.html?rw_useCurrentProtocol=1&node=2953222031&ref_=beauty_leftnav_produitsbronzantssolaires',
        'https://www.amazon.fr/b?node=211031031&ref=lp_211020031_nr_n_0'
    ]

    def parse(self, response):
        for product in response.css('div.s-result-item'):
            product_name = product.css('span.a-size-base-plus.a-color-base.a-text-normal::text').get()
            price = product.css('span.a-price span.a-offscreen::text').get()
            product_url = product.css('a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal::attr(href)').get()

            yield {
                'product_name': product_name,
                'price': price,
                'product_url': response.urljoin(product_url)
            }
