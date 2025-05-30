from pathlib import Path

import pickle  

from rdagent.log import rdagent_logger as logger


class KnowledgeBase:
    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path else None
        self.load()

    def load(self) -> None:
        if self.path is not None and self.path.exists():
            with self.path.open("rb") as f:
                loaded = pickle.load(f)
                if isinstance(loaded, dict):                    
                    loaded_data = {k: v for k, v in loaded.items() if k != "path"}
                else:                   
                    loaded_data = {k: v for k, v in loaded.__dict__.items() if k != "path"}
                self.__dict__.update(loaded_data)

    def dump(self) -> None:
        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            pickle.dump(self.__dict__, self.path.open("wb"))
        else:
            logger.warning("KnowledgeBase path is not set, dump failed.")
