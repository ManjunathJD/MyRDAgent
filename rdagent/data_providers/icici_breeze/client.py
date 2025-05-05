from breeze_connect import BreezeConnect
import pandas as pd
from rdagent.log import rdagent_logger as logger
from rdagent.data_providers.icici_breeze.utils import format_date
from datetime import datetime


class ICICIBreezeClient:
    def __init__(self, api_key, secret_key, session_token_path):
        self.api_key = api_key
        self.secret_key = secret_key
        self.breeze = BreezeConnect(api_key=self.api_key)
        self.session_token_path = session_token_path
        self.session_token = None
        self.user_id = None
        self.load_session()

    def login(self, user_id, session):
        self.user_id = user_id
        self.session_token = session
        self.breeze.set_session(
            user_id=self.user_id, api_session=self.session_token
        )
        self.save_session()

    def save_session(self):
        with open(self.session_token_path, "w") as f:
            f.write(self.session_token)

    def load_session(self):
        try:
            with open(self.session_token_path, "r") as f:
                self.session_token = f.read().strip()

        except Exception:
            logger.warning("Token not found")

    def logout(self):
        try:
            self.breeze.logout()
        except Exception as e:
            logger.error(f"Error on logout {e}")

    def get_historical_data(self, stock_code, exchange_code, from_date, to_date, interval):
        try:
            self.breeze.set_session(
                user_id=self.user_id, api_session=self.session_token
            )
            data = self.breeze.get_historical_data(
                interval=interval,
                from_date=format_date(from_date),
                to_date=format_date(to_date),
                stock_code=stock_code,
                exchange_code=exchange_code,
            )
            df = pd.DataFrame(data["Success"])
            return df
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            raise
    def get_stock_list(self):
        try:
            self.breeze.set_session(
                user_id=self.user_id, api_session=self.session_token
            )
            instruments = self.breeze.get_stock_list()
            df = pd.DataFrame(instruments["Success"])
            return df
        except Exception as e:
            logger.error(f"Error getting instruments: {e}")
            raise

    def get_quotes(self, stock_code, exchange_code):
        try:
            self.breeze.set_session(
                user_id=self.user_id, api_session=self.session_token
            )
            data = self.breeze.get_quotes(
                stock_code=stock_code,
                exchange_code=exchange_code
            )
            df = pd.DataFrame(data["Success"])
            return df
        except Exception as e:
            logger.error(f"Error getting quotes: {e}")
            raise