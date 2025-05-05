from pathlib import Path
from typing import Dict, Optional




# Because we use isinstance to distinguish between different types of tasks, we need to use sub classes to represent different types of tasks
class WorkflowTask:
    def __init__(self, name: str = "Workflow", *args, **kwargs) -> None:
        self.name = name
