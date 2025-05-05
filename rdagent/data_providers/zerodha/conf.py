import os
from rdagent.core.conf import ConfigBaseSetting

class ZerodhaDataSetting(ConfigBaseSetting):
    """Setting for data folder"""

    access_token_path: str = os.path.join(os.getcwd(), ".zerodha_token")