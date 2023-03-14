from decouple import config


class Settings:

    WB_API_TOKEN = config('WB_API_TOKEN')


settings = Settings()
