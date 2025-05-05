import pandas as pd
from rdagent.data_providers.icici_breeze.client import ICICIBreezeClient


class ICICIBreezeDataLoader:
    def __init__(self, breeze_client: ICICIBreezeClient):
        self.client = breeze_client

    def load_data(self, stock_code, exchange_code, start_date, end_date, interval):
        raw_data = self.client.get_historical_data(
            stock_code, exchange_code, start_date, end_date, interval
        )
        # Format data
        df = self._format_data(raw_data)

        return df

    def get_stock_list(self):
        raw_data = self.client.get_stock_list()
        # Format data
        df = self._format_instruments(raw_data)

        return df

    def _format_data(self, df):
        df.rename(
            columns={
                "datetime": "datetime",
                "open": "Open",
                "high": "High",
                "low": "Low",
                "close": "Close",
                "volume": "Volume",
            },
            inplace=True,
        )
        df["datetime"] = pd.to_datetime(df["datetime"])
        df.set_index("datetime", inplace=True)
        return df
    def _format_instruments(self, df):
        df.rename(
            columns={
                "StockCode": "instrument_token",
                "StockName": "tradingsymbol",
                "ExchangeCode":"ExchangeCode",

            },
            inplace=True,
        )

        return df