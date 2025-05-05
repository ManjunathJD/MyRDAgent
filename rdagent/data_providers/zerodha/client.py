from kiteconnect import KiteConnect
from kiteconnect import exceptions as ex
import pandas as pd
from rdagent.log import rdagent_logger as logger
from rdagent.data_providers.zerodha.utils import format_date
from datetime import datetime

class ZerodhaClient:
    def __init__(self, api_key, api_secret, user_id, access_token_path):
        self.kite = KiteConnect(api_key=api_key)
        self.api_key = api_key
        self.api_secret = api_secret
        self.user_id = user_id
        self.access_token = None
        self.access_token_path = access_token_path
        self.load_access_token()

    def load_access_token(self):
        try:
            with open(self.access_token_path, "r") as f:
                self.access_token = f.read().strip()
                self.kite.set_access_token(self.access_token)

        except Exception:
            logger.warning("Token not found")

    def get_request_token(self, request_token):
        """
        Generates the access token.
        """
        try:
            data = self.kite.generate_session(request_token, api_secret=self.api_secret)
            self.access_token = data["access_token"]
            self.kite.set_access_token(self.access_token)
            self.save_access_token()
        except ex.TokenException as e:
            logger.error(f"Access token generate error {e}")
            raise Exception("Access token generate error")

    def save_access_token(self):
        with open(self.access_token_path, "w") as f:
            f.write(self.access_token)

    def get_historical_data(self, instrument_token, from_date, to_date, interval):
        try:
            data = self.kite.historical_data(
                instrument_token, from_date, to_date, interval
           )
            df = pd.DataFrame(data)
            return df
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            raise
    def get_instruments(self):
        try:
            instruments = self.kite.instruments()
            df = pd.DataFrame(instruments)
            return df
        except Exception as e:
            logger.error(f"Error getting instruments: {e}")
            raise