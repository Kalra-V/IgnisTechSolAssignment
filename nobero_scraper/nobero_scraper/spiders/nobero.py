import scrapy


class NoberoSpider(scrapy.Spider):
    name = "nobero"
    allowed_domains = ["nobero.com"]
    start_urls = ["https://nobero.com/pages/men"]

    def parse(self, response):
        # Extracting categories from the Men section
        categories = response.css('div.collection-grid-item a::attr(href)').getall()
        for category in categories:
            category_url = response.urljoin(category)
            yield scrapy.Request(category_url, callback=self.parse_category)

    def parse_category(self, response):
        # Extracting product URLs from category pages
        product_urls = response.css('a.product-grid-item__image-wrapper::attr(href)').getall()
        for product_url in product_urls:
            full_url = response.urljoin(product_url)
            yield scrapy.Request(full_url, callback=self.parse_product)

    def parse_product(self, response):
        # Parsing product details
        product_data = {
            "category": response.css('span.collection::text').get().strip(),
            "url": response.url,
            "title": response.css('h1.product-single__title::text').get().strip(),
            "price": int(response.css('span.price__current::text').get().replace('Rs. ', '').replace(',', '').strip()),
            "MRP": int(response.css('span.price__original::text').get().replace('Rs. ', '').replace(',', '').strip()),
            "last_7_day_sale": int(response.css('span.price__reduced::text').get().replace('Rs. ', '').replace(',', '').strip()),
            "available_skus": [],
            "fit": response.css('span.fit::text').get().strip(),
            "fabric": response.css('span.fabric::text').get().strip(),
            "neck": response.css('span.neck::text').get().strip(),
            "sleeve": response.css('span.sleeve::text').get().strip(),
            "pattern": response.css('span.pattern::text').get().strip(),
            "length": response.css('span.length::text').get().strip(),
            "description": response.css('div.product-description p::text').getall()
        }

        # Extracting SKUs
        colors = response.css('div.color-swatch span::text').getall()
        sizes = response.css('select.single-option-selector option::text').getall()
        for color in colors:
            sku_data = {
                "color": color.strip(),
                "size": sizes
            }
            product_data["available_skus"].append(sku_data)

        yield product_data
