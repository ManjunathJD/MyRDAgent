# rdagent/app/CI/run.py
import os
import subprocess
import sys

from rdagent.log.logger import logger
from rdagent.utils.env import get_env_info
from rdagent.utils.repo.diff import get_file_diff


def run_command(cmd: str, shell: bool = True):
    """
    Run a command in the shell.
    """
    proc = subprocess.Popen(
        cmd,
        shell=shell,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    stdout, stderr = proc.communicate()

    logger.info(f"stdout: {stdout}")
    logger.error(f"stderr: {stderr}")

    if proc.returncode != 0:
        raise Exception(f"Error running command: {cmd}\n{stderr}")

    return stdout


def run_pytest(path: str = None):
    """
    Run pytest on the given path.
    """
    if path is None:
        cmd = "pytest -s test"
    else:
        cmd = f"pytest -s {path}"
    logger.info(f"Running command: {cmd}")
    return run_command(cmd)


def run_tox():
    """
    Run tox.
    """
    cmd = "tox -vv"
    logger.info(f"Running command: {cmd}")
    return run_command(cmd)


def run_check_format():
    """
    Check if the code is formatted correctly.
    """
    cmd = "pre-commit run --all-files"
    logger.info(f"Running command: {cmd}")
    return run_command(cmd)


def run_check_type():
    """
    Check if the code is typed correctly.
    """
    cmd = "mypy rdagent"
    logger.info(f"Running command: {cmd}")
    return run_command(cmd)


def run_coverage():
    """
    Run coverage.
    """
    cmd = "coverage run -m pytest test"
    logger.info(f"Running command: {cmd}")
    run_command(cmd)

    cmd = "coverage report -m"
    logger.info(f"Running command: {cmd}")
    return run_command(cmd)


def main(stage: str):
    """
    Main function to run the CI.
    """
    logger.info("--- CI start ---")

    logger.info(get_env_info())

    # check python version
    logger.info(f"Python version: {sys.version}")
    if sys.version_info < (3, 9):
        raise Exception("Python version must be 3.9 or higher.")
    logger.info("Python version check success.")

    logger.info(f"stage = {stage}")
    if stage == "test":
        # pytest
        try:
            run_pytest()
            logger.info("pytest test success.")
        except Exception as e:
            logger.error(f"pytest test failed: {e}")
            sys.exit(1)

        # coverage
        try:
            run_coverage()
            logger.info("coverage test success.")
        except Exception as e:
            logger.error(f"coverage test failed: {e}")
            sys.exit(1)
    elif stage == "check":
        # check_format
        try:
            run_check_format()
            logger.info("check_format success.")
        except Exception as e:
            logger.error(f"check_format failed: {e}")
            sys.exit(1)

        # check_type
        try:
            run_check_type()
            logger.info("check_type success.")
        except Exception as e:
            logger.error(f"check_type failed: {e}")
            sys.exit(1)
    elif stage == "tox":
        # tox
        try:
            run_tox()
            logger.info("tox success.")
        except Exception as e:
            logger.error(f"tox failed: {e}")
            sys.exit(1)

    elif stage == "diff":
        logger.info("diff test start.")
        try:
            logger.info(get_file_diff())
            logger.info("diff test success.")
        except Exception as e:
            logger.error(f"diff test failed: {e}")
            sys.exit(1)

    logger.info("--- CI end ---")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", type=str, default="test")
    args = parser.parse_args()

    main(args.stage)