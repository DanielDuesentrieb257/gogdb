import aiohttp, asyncio
from fake_useragent import UserAgent
import logging


class APIRequester:

    def __init__(self, retries=5, concurrency=10):
        self.__retries = retries
        self.__concurrency = concurrency
        self.__logger = logging.getLogger('GOGDB.DISCORDBOT.REQUESTER')


    async def __aenter__(self):
        self.__ua = UserAgent().random
        self.__session = aiohttp.ClientSession(headers={'User-Agent':self.__ua})
        return self


    async def __aexit__(self, *err):
        await self.__session.close()
        self.__session = None

    async def getjson(self, url, params=None):
        if isinstance(url, str) and (isinstance(params, dict) or params == None):
            return await self.__getjson(url, params)
        elif isinstance(url, list) and (isinstance(params, dict) or params == None):
            return await self.__getjson_multi_urls(url, params)
        elif isinstance(url, str) and isinstance(params, list):
            return await self.__getjson_multi_params(url, params)


    async def __getjson(self, url, params):
        retries = 0
        logstr = 'request %s with params %s' % (url, params)
        self.__logger.debug('Now %s' % logstr)
        while True:
            async with self.__session.get(url, params=params) as resp:
                try:
                    resp.raise_for_status()
                except Exception as e:
                    retries += 1
                    if retries <= self.__retries:
                        continue
                    else:
                        self.__logger.error('Fatal error occured when %s: %s' % (logstr, e))
                        return {'error':True, 'errorType':type(e).__name__, 'errorMessage':resp.reason, 'responseStatus':resp.status}
                try:
                    return await resp.json()
                except Exception as e:
                    self.__logger.error('Fatal error occured when %s: %s' % (logstr, e))
                    return {'error':True, 'errorType':type(e).__name__, 'errorMessage':str(e), 'responseStatus':resp.status}


    async def __getjson_multi_urls(self, urls, params):
        if len(urls) <= self.__concurrency:
            return await asyncio.gather(*[self.__getjson(url, params) for url in urls], return_exceptions=True)
        else:
            result = list()
            start = 0
            end = self.__concurrency
            while True:
                result.extend(await asyncio.gather(*[self.__getjson(url, params) for url in urls[start:end]], return_exceptions=True))
                if end > len(urls):
                    return result
                else:
                    start = end
                    end += self.__concurrency


    async def __getjson_multi_params(self, url, params):
        if len(params) <= self.__concurrency:
            return await asyncio.gather(*[self.__getjson(url, param) for param in params], return_exceptions=True)
        else:
            result = list()
            start = 0
            end = self.__concurrency
            while True:
                result.extend(await asyncio.gather(*[self.__getjson(url, param) for param in params[start:end]], return_exceptions=True))
                if end > len(params):
                    return result
                else:
                    start = end
                    end += self.__concurrency


class APIUtility():

    def __init__(self):
        self.__logger = logging.getLogger('GOGDB.DISCORDBOT.UTILITY')

    def errorchk(self, jsondata):
        error = jsondata.get('error', False)
        if error:
            self.__logger.warning('Error occured on request, may lost data')
        return error

    def product_notfoundchk(self, productid, productdata):
        if "message" in productdata:
            msg = productdata['message']
            if t:
                self.__logger.error('Product %s not found' % productid)
                return True
            else:
                self.__logger.error('Product id may error, product data here %s' % productdata)
                return False
        else:
            return False


class API():

    def __init__(self, hosts, retries=5):
        self.__hosts = dict()
        self.__hosts['root'] = hosts
        self.__hosts['detail'] = f"{self.__hosts['root']}/products"
        self.__hosts['price'] = f"{self.__hosts['root']}/price"
        self.__hosts['discount'] = f"{self.__hosts['root']}/discount"
        self.__hosts['changes'] = f"{self.__hosts['root']}/changes"

        self.__retries = retries
        self.__logger = logging.getLogger('GOGDB.DISCORDBOT')

        self.__utl = APIUtility()

    @property
    def retries(self):
        return self.__retries

    @retries.setter
    def retries(self, value):
        self.__retries = value

    @property
    def logger(self):
        return self.__logger

    @property
    def hosts(self):
        return self.__hosts['root']

    @hosts.setter
    def hosts(self, value):
        self.__hosts['root'] = value


    async def query_products(self, string='', limit=20, page=1):
        if string == '':
            params = {'limit':limit, 'page':page}
        else:
            params = {'query':string, 'limit':limit, 'page':page}

        async with APIRequester(self.__retries) as request:

            products = await request.getjson(self.__hosts['detail'], params)

            if self.__utl.errorchk(products):
                return dict()
            else:
                return products


    async def product_detail(self, prod_id):
        async with APIRequester(self.__retries) as request:

            detail = await request.getjson(f"{self.__hosts['detail']}/{prod_id}")

            if self.__utl.errorchk(detail):
                return dict()
            else:
                return detail


    async def product_price(self, prod_id, country=''):
        params = {'countryCode':country} if country != '' else {'limit':0}

        async with APIRequester(self.__retries) as request:

            urls = [f"{self.__hosts['detail']}/{prod_id}",
                    f"{self.__hosts['price']}/{prod_id}"]
            detail, price = await request.getjson(urls, params)

            if self.__utl.errorchk(price):
                return dict()
            else:
                if country == '':
                    price['title'] = detail['title']
                    price['id'] = prod_id
                else:
                    price = {'count':1, 'limit':0, 'page':1, 'pages':1, 'baseprice':[price], 'title':detail['title'], 'id':prod_id}
                return price


    async def product_discount(self, prod_id):
        params = {'limit':0}

        async with APIRequester(self.__retries) as request:
            discount = await request.getjson(f"{self.__hosts['discount']}/{prod_id}", params)

            if self.__utl.errorchk(discount):
                return dict()
            else:
                return discount


    async def product_changes(self, prod_id, limit, page):
        params = {'limit': limit, 'page': page}

        async with APIRequester(self.__retries) as request:
            changes = await request.getjson(f"{self.__hosts['changes']}/{prod_id}", params)

            if self.__utl.errorchk(changes):
                return dict()
            else:
                return changes

    async def list_changes(self, limit, page):
        params = {'limit': limit, 'page': page}

        async with APIRequester(self.__retries) as request:
            changes = await request.getjson(f"{self.__hosts['changes']}", params)

            if self.__utl.errorchk(changes):
                return dict()
            else:
                return changes

