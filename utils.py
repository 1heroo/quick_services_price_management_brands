import asyncio
import json

import aiohttp


class BaseUtils:

    @staticmethod
    def auth(token):
        return {
            'Authorization': token
        }

    @staticmethod
    async def make_get_request(url, headers, no_json=False):
        async with aiohttp.ClientSession(trust_env=True, headers=headers) as session:
            async with session.get(url=url) as response:
                print(response.status)
                # print(await response.text())
                if response.status == 200:
                    return True if no_json else json.loads(await response.text())
                return

    @staticmethod
    async def make_post_request(url, headers, payload, no_json=False):
        async with aiohttp.ClientSession(trust_env=True, headers=headers) as session:
            async with session.post(url=url, json=payload) as response:
                print(response.status)
                # print(await response.text())
                if response.status == 200:
                    return True if no_json else json.loads(await response.text())
                return

    @staticmethod
    def remove_duplicates(products, nm_name):
        articles = []
        output_data = []

        for product in products:
            article = product.get(nm_name)
            if article not in articles:
                articles.append(article)
                output_data.append(product)
        return output_data

    async def update_prices(self, prices, token_auth):
        url = 'https://suppliers-api.wildberries.ru/public/api/v1/prices'

        len_prices = len(prices)
        times = len_prices // 1000
        start = 0

        for i in range(times + 1):
            chunk_prices = prices[start: start + 1000] if i != times else prices[start: len_prices]
            start += 1000
            data = await self.make_post_request(url=url, headers=token_auth, payload=chunk_prices)
            print(data)

    async def update_discounts(self, discounts, token_auth):
        url = 'https://suppliers-api.wildberries.ru/public/api/v1/updateDiscounts'

        len_discounts = len(discounts)
        times = len_discounts // 1000
        start = 0

        for i in range(times + 1):
            chunk_discounts = discounts[start: start + 1000] if i != times else discounts[start: len_discounts]
            start += 1000

            data = await self.make_post_request(url=url, headers=token_auth, payload=chunk_discounts)
            print(data)

    async def get_products_from_api(self, token_auth):
        data = []
        url = 'https://suppliers-api.wildberries.ru/content/v1/cards/cursor/list'
        payload = {
            "sort": {
                "cursor": {
                    "limit": 1000
                },
                "filter": {
                    "withPhoto": -1
                }
            }
        }
        total = 1
        while total != 0:
            partial_data = await self.make_post_request(url=url, payload=payload, headers=token_auth)
            data += partial_data['data']['cards']
            cursor = partial_data['data']['cursor']
            payload['sort']['cursor'].update(cursor)
            total = cursor['total']
        return data

    async def get_detail_by_nms(self, nms):
        output_data = []
        tasks = []
        count = 1

        for nm in nms:
            task = asyncio.create_task(self.get_product_data(article=nm))
            tasks.append(task)
            count += 1

            if count % 50 == 0:
                print(count, 'product data')
                output_data += await asyncio.gather(*tasks, return_exceptions=True)
                tasks = []

    async def get_product_data(self, article):
        detail_url = f'https://card.wb.ru/cards/detail?spp=0&regions=80,64,38,4,115,83,33,68,70,69,30,86,75,40,1,66,31,48,110,22,71,111&pricemarginCoeff=1.0&reg=0&appType=1&emp=0&locale=ru&lang=ru&curr=rub&couponsGeo=12,3,18,15,21&dest=-1257786&nm={article}'
        detail = await self.make_get_request(detail_url, headers={})

        if detail:
            detail = detail['data']['products']
        else:
            detail = {}

        return detail


def make_head(article: int):
    head = 'https://basket-{i}.wb.ru'

    if article < 14400000:
        number = '01'
    elif article < 28800000:
        number = '02'
    elif article < 43500000:
        number = '03'
    elif article < 72000000:
        number = '04'
    elif article < 100800000:
        number = '05'
    elif article < 106300000:
        number = '06'
    elif article < 111600000:
        number = '07'
    elif article < 117000000:
        number = '08'
    elif article < 131400000:
        number = '09'
    else:
        number = '10'
    return head.format(i=number)


def make_tail(article: str, item: str):
    length = len(str(article))
    if length <= 3:
        return f'/vol{0}/part{0}/{article}/info/' + item
    elif length == 4:
        return f'/vol{0}/part{article[0]}/{article}/info/' + item
    elif length == 5:
        return f'/vol{0}/part{article[:2]}/{article}/info/' + item
    elif length == 6:
        return f'/vol{article[0]}/part{article[:3]}/{article}/info/' + item
    elif length == 7:
        return f'/vol{article[:2]}/part{article[:4]}/{article}/info/' + item
    elif length == 8:
        return f'/vol{article[:3]}/part{article[:5]}/{article}/info/' + item
    else:
        return f'/vol{article[:4]}/part{article[:6]}/{article}/info/' + item
