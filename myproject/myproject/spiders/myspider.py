import scrapy
from scrapy_splash import SplashRequest

class MySpider(scrapy.Spider):
    name = "products"
    start_urls = [
        'http://www.petlebi.com',
    ]

    def handle_error(self, failure):
        self.logger.error(repr(failure))

        # In case you want to analyze which request failed, you can extract it from the failure object:
        failed_request = failure.request
        self.logger.error("Failed request: %s", failed_request.url)

    def parse(self, response):
        # Lua script to interact with each navbar button
        script = """
        function main(splash, args)
            splash:go(args.url)
            splash:wait(1.5)
            local category_urls = {}
            
            -- Interact with each button on the navbar to choose animal type
            for _, btn in ipairs(splash:select_all('.menu-tabing a')) do
                btn:mouse_hover()  -- Simulate hover
                splash:wait(1.5)   -- Wait for potential dropdowns to appear

                -- to access to tüm kategoriler
                for _, link in ipairs(splash:select_all('li.wsshoplink-active a')) do

                    -- to collect category URLs that appear in tüm kategoriler 
                    for _, each in ipairs(splash:select_all('ul.wstliststy01 li a')) do
                        if each then
                            table.insert(category_urls, each:attr('href'))
                        else 
                            splash:log('Nil element found in innermost loop for selector: ul.wstliststy01 li a')
                        end
                    end
                end
                if not link then
                    splash:log('Nil element found in middle loop for selector: li.wsshoplink-active a')
                end
            end
            if not btn then
                splash:log('Nil element found in outermost loop for selector: .menu-tabing a')
            end
            
            return {urls=category_urls}
        end
        """

        yield SplashRequest(response.url, self.parse_category_urls,
                            endpoint='execute',
                            args={'lua_source': script},
                            errback=self.handle_error)


                
    def parse_category_urls(self, response):

        try:
            category_urls = response.data['urls']
            for url in category_urls:
                yield SplashRequest(url, self.parse_category, args={'wait': 2})

        except Exception as e:
            self.logger.error("Error occurred in parse_category_url: %s", e)



    def parse_category(self, response):

        try:
            product_urls = response.css('div.card-body a::attr(href)').extract()
            for url in product_urls:
                yield SplashRequest(url, self.parse_product, args={'wait': 2})

        except Exception as e:
            self.logger.error("Error occurred in parse_category: %s", e)



    def parse_product(self, response):

        try:
            item = {
                #'product_URL': ,  # öğren
                'product_name': response.css('h1.product-h1::text').get(),
                #'product_barcode': , # öğren
                #'product_price': response.css('new-price::text').get(),
                #'product_stock': response.css('description::text').get(), #nerde
                #'product_images': , # öğren
                #'description': response.css('span#productDescription p::text').getall(),
                #'sku': response.css('new-price::text').get(),   #nerde
                #'category': response.css('li a::text').getall(), 
                #'product_ID': response.css('col-10 pd-d-v::text').get(),    #bu barkod dimi
                #'brand': response.css('col-10 pd-d-v::text').get(),  
            }
            yield item

        except Exception as e:
            self.logger.error("Error occurred in parse_product: %s", e)
