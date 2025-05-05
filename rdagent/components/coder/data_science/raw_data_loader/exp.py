from rdagent.components.coder.CoSTEER.task import CoSTEERTask, TaskType


# Because we use isinstance to distinguish between different types of tasks, we need to use sub classes to represent different types of tasks
class DataLoaderTask(CoSTEERTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task_type = TaskType.DATA_LOADER

