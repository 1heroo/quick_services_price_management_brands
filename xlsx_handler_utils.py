import aiohttp

import pandas as pd
from string import ascii_uppercase, ascii_lowercase


def find_vendor_code_column(df: pd.DataFrame) -> pd.DataFrame:
    columns = df.columns
    stock_names = ['Артикул', "артикул", "Артикул для заказа", "Артикул \nдля заказа", 'Артикул \r\nдля заказа']
    for index in df.index[:100]:
        for column in columns:
            if df[column][index] in stock_names or column in stock_names:
                return column


def find_price_column(df: pd.DataFrame) -> pd.DataFrame:
    stock_names = ['МРЦ ,  руб', 'РРЦ Wildberries, руб', 'ВБ, руб']
    columns = df.columns
    for index in df.index[:100]:
        for column in columns:
            if df[column][index] in stock_names or column in stock_names:
                return column


def handle_xlsx(df: pd.DataFrame, file_name) -> pd.DataFrame:
    index = search_table_begin(df=df)
    df = df.loc[index:]
    df.to_csv(file_name)

    delete_first_line(filename=file_name)
    df = pd.read_csv(file_name)
    for column in df:
        if 'Unnamed' in column:
            df = df.drop(column, axis=1)
    return df


def delete_first_line(filename):
    with open(filename, "r", encoding='utf-8') as fp:
        lines = fp.readlines()

    with open(filename, "w", encoding='utf-8') as fp:
        for line in range(1, len(lines)):
            fp.write(lines[line])


def search_table_begin(df: pd.DataFrame):
    columns = df.columns
    article_list = ['Артикул', "артикул", "Артикул для заказа", "Артикул для заказа", "Артикул \nдля заказа"]
    for index in df.index[:100]:
        for column in columns:
            if df[column][index] in article_list or column in article_list:
                return index
