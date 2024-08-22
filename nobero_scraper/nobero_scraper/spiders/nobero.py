import scrapy
import json

class NoberoSpider(scrapy.Spider):
    name = 'nobero'
    allowed_domains = ['nobero.com']
    start_urls = ['https://nobero.com/pages/men']

    def parse(self, response):
        # Extract all subcategory URLs under the Men's section
        category_links = response.css('a#image-container::attr(href)').getall()
        for link in category_links:
            yield response.follow(link, self.parse_category)

    def parse_category(self, response):
        # Extract product URLs in each category
        product_links = response.css('a.product_link::attr(href)').getall()
        for link in product_links:
            yield response.follow(link, self.parse_product)

        # Handle pagination
        next_page = response.css('a[rel="next"]::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse_category)

    def parse_product(self, response):
        # Extract product details
        title = response.css('h1.product-title::text').get().strip()
        price = response.css('h2#variant-price spanclass::text').get()
        mrp = response.css('span#variant-compare-at-price spanclass::text').get()

        #USING XPATH WAS UNAVOIDABLE
        data_attr = response.xpath('//div[@class="product_bought_count"]/@data-ga-view-payload-custom').get()
        last_7_day_sale = 0
        if data_attr:
            try:
                payload = json.loads(data_attr.replace("'", '"'))
                last_7_day_sale = int(payload.get('product_count', 0))
            except (json.JSONDecodeError, ValueError):
                last_7_day_sale = 0
        
        #USING XPATH WAS UNAVOIDABLE
        fit = response.xpath('//p[contains(@class, "text-[#000000]") and contains(@class, "pb-[8px]") and contains(@class, "font-normal")]/text()').getall()[0]
        fabric = response.xpath('//p[contains(@class, "text-[#000000]") and contains(@class, "pb-[8px]") and contains(@class, "font-normal")]/text()').getall()[1]
        neck = response.xpath('//p[contains(@class, "text-[#000000]") and contains(@class, "pb-[8px]") and contains(@class, "font-normal")]/text()').getall()[2]
        sleeve = response.xpath('//p[contains(@class, "text-[#000000]") and contains(@class, "pb-[8px]") and contains(@class, "font-normal")]/text()').getall()[3]
        pattern = response.xpath('//p[contains(@class, "text-[#000000]") and contains(@class, "pb-[8px]") and contains(@class, "font-normal")]/text()').getall()[4]
        length =response.xpath('//p[contains(@class, "text-[#000000]") and contains(@class, "pb-[8px]") and contains(@class, "font-normal")]/text()').getall()[5]
        
        #FOR DESCRIPTION
        description_parts = response.css('#description_content p::text, #description_content span::text, #description_content strong::text, #description_content br').getall()

        # Process the parts to build the final description string
        description = ""
        for part in description_parts:
            if part == '<br data-mce-fragment="1">':
                description += '\n'  # Add a newline for <br> tags
            else:
                description += part.strip()  # Add the text part and strip extra spaces

        # Extract SKU details
        available_skus = []

        # Extract the color labels
        color_labels = response.css('div.flex.overflow-x-scroll.hide-scrollbar fieldset label')

        # Iterate through each color label
        for color_label in color_labels:
            color = color_label.css('input.variant-color-input::attr(value)').get()
            
            # Extract the sizes for this color
            size_labels = response.css('div.size-section fieldset label')
            sizes = []
            for size_label in size_labels:
                size = size_label.css('input.size-select-input::attr(value)').get()
                sizes.append(size)

            # Add the color and its sizes to the available_skus list
            available_skus.append({
                'color': color,
                'size': sizes
            })


        # Create product data dictionary
        product_data = {
            'category': response.css('nav.breadcrumb a::text').getall()[-1].strip(),
            'url': response.url,
            'title': title,
            'price': price,
            'MRP': mrp,
            'last_7_day_sale' : last_7_day_sale,
            'available_skus': available_skus,
            #product_urls
            'fit' : fit,
            'fabric' : fabric,
            'neck' : neck,
            'sleeve' : sleeve,
            'pattern' : pattern,
            'length' : length,
            'description' : description
        }

        yield product_data
