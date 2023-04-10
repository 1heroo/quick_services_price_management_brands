import math

import pandas as pd

from settings import settings
from utils import BaseUtils


class BaseServices:

    def __init__(self):
        self.utils = BaseUtils()

    async def price_management(self, df, vendorCode_column, price_column):
        prices_to_be_updated: list = []
        discounts_to_be_updated: list = []

        auth = self.utils.auth(token=settings.WB_API_TOKEN)
        products = await self.utils.get_products_from_api(token_auth=auth)
        products_df = pd.DataFrame(products)
        vendorCodes_no_bland = products_df.vendorCode.apply(lambda item: item.split('bland')[-1])
        products_df['vendorCodes_no_bland'] = vendorCodes_no_bland

        new_df = pd.DataFrame({
            vendorCode_column: df[vendorCode_column],
            price_column: df[price_column]
        })

        df = pd.merge(
            new_df, products_df, how='inner', left_on=vendorCode_column, right_on='vendorCodes_no_bland'
        )

        for index in df.index:

            basicSale = 31
            price = math.ceil(float(df[price_column][index])) - 15
            price = price / (100 - basicSale) * 100
            price = math.ceil(price)

            prices_to_be_updated.append({
                'nmId': int(df['nmID'][index]),
                'price': price
            })
            discounts_to_be_updated.append({
                'nm': int(df['nmID'][index]),
                'discount': basicSale
            })

        prices_to_be_updated = self.utils.remove_duplicates(products=prices_to_be_updated, nm_name='nmId')
        discounts_to_be_updated = self.utils.remove_duplicates(products=discounts_to_be_updated, nm_name='nm')

        await self.utils.update_prices(prices=prices_to_be_updated, token_auth=auth)
        await self.utils.update_discounts(discounts=discounts_to_be_updated, token_auth=auth)
