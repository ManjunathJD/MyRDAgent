import os
from rdagent.core.conf import ConfigBaseSetting


class ICICIBreezeDataSetting(ConfigBaseSetting):
    """Setting for data folder"""

    api_key: str
    secret_key: str
    session_token_path: str = os.path.join(os.getcwd(), ".icici_token")