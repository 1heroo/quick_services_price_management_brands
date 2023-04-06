import os
import time

import pandas as pd
import uvicorn
from fastapi import FastAPI, File

from services import BaseServices
from settings import settings
from utils import BaseUtils
from xlsx_handler_utils import handle_xlsx, find_vendor_code_column, find_price_column

app = FastAPI()
utils = BaseUtils()
services = BaseServices()


@app.post("/")
async def root():
    for file in os.listdir('file_db/'):
        if 'Штурм' in file:
            list_name = 'ПРАЙС'
        if 'PIT' in file:
            print(file)
            list_name = 'Инструменты'
        file_name = str(int(time.time())) + '.csv'

        df = pd.read_excel('file_db/' + file, list_name, header=None)
        df = handle_xlsx(df=df, file_name=file_name)

        vendorCode_column = find_vendor_code_column(df=df)
        price_column = find_price_column(df=df)
        print(vendorCode_column, price_column)
        await services.price_management(df=df, price_column=price_column, vendorCode_column=vendorCode_column)
        os.remove(file_name)


if __name__ == '__main__':
    uvicorn.run(
        app='main:app',
        host='0.0.0.0',
        port=8000,
        reload=True
    )
