import pandas as pd
from rdagent.data_providers.zerodha.client import ZerodhaClient


class ZerodhaDataLoader:
    def __init__(self, zerodha_client: ZerodhaClient):
        self.client = zerodha_client

    def load_data(self, instrument_token, start_date, end_date, interval):
        raw_data = self.client.get_historical_data(
            instrument_token, start_date, end_date, interval
        )
        # Format data
        df = self._format_data(raw_data)

        return df

    def get_instruments(self):
        raw_data = self.client.get_instruments()
        # Format data
        df = self._format_instruments(raw_data)

        return df

    def _format_data(self, df):
        df.rename(
            columns={
                "date": "datetime",
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
                "instrument_token": "instrument_token",
                "tradingsymbol": "tradingsymbol",
                "name":"name",
                "last_price": "last_price",
            },
            inplace=True,
        )

        return df