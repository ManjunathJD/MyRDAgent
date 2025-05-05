class WorkflowError(Exception):
    """
    Exception indicating an error that the current loop cannot handle, preventing further progress.
    """


class FormatError(WorkflowError):  # noqa: D101
    """
    After multiple attempts, we are unable to obtain the answer in the correct format to proceed.
    """


class CoderError(WorkflowError):
    """
    Exceptions raised when Implementing and running code.
    - start: FactorTask => FactorGenerator
    - end: Get dataframe after execution

    The more detailed evaluation in dataframe values are managed by the evaluator.
    """

    # NOTE: it corresponds to the error of **component**


class CodeFormatError(CoderError):  # noqa: D101
    """
    The generated code is not found due format error.
    """


class CustomRuntimeError(CoderError):  # noqa: D101
    """
    The generated code fail to execute the script.
    """


class NoOutputError(CoderError):  # noqa: D101
    """
    The code fail to generate output file.
    """


class RunnerError(Exception):
    """
    Exceptions raised when running the code output.
    """

    # NOTE: it corresponds to the error of whole **project**


FactorEmptyError = CoderError  # noqa: D101 Exceptions raised when no factor is generated correctly

ModelEmptyError = CoderError  # noqa: D101 Exceptions raised when no model is generated correctly


class KaggleError(Exception):  # noqa: D101
    """
    Exceptions raised when calling Kaggle API
    """
