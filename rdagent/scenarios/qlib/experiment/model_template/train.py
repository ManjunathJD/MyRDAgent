# rdagent/app/CI/run.py
import os
import subprocess
import sys

from rdagent.log.base import logger


def run_command(cmd, cwd=None):
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise Exception(f"Command failed: {cmd}\n{stderr.decode()}")
    return stdout.decode()


def run_coverage(cwd=None):
    logger.info("Running coverage...")
    run_command("coverage run --source rdagent -m pytest", cwd=cwd)
    return run_command("coverage report -m", cwd=cwd)


def upload_coverage(cwd=None):
    logger.info("Uploading coverage...")
    return run_command("coverage xml -o coverage.xml", cwd=cwd)


def upload_code_qlib(cwd=None):
    logger.info("Uploading qlib...")
    return run_command(f"python {os.path.join(os.path.dirname(__file__),'upload_code_qlib.py')}", cwd=cwd)

def upload_code_kaggle(cwd=None):
    logger.info("Uploading kaggle...")
    return run_command(f"python {os.path.join(os.path.dirname(__file__),'upload_code_kaggle.py')}", cwd=cwd)

def upload_code_data_science(cwd=None):
    logger.info("Uploading data science...")
    return run_command(f"python {os.path.join(os.path.dirname(__file__),'upload_code_data_science.py')}", cwd=cwd)

def run_pylint(cwd=None):
    logger.info("Running pylint...")
    return run_command("pylint rdagent", cwd=cwd)


def run_bandit(cwd=None):
    logger.info("Running bandit...")
    return run_command("bandit -r rdagent", cwd=cwd)


def run_mypy(cwd=None):
    logger.info("Running mypy...")
    return run_command("mypy rdagent", cwd=cwd)


def run_pytest(cwd=None):
    logger.info("Running pytest...")
    return run_command("pytest", cwd=cwd)


def run_pre_commit(cwd=None):
    logger.info("Running pre-commit...")
    return run_command("pre-commit run --all-files", cwd=cwd)


def run_all_tools(cwd=None):
    run_pre_commit(cwd=cwd)
    run_pylint(cwd=cwd)
    run_bandit(cwd=cwd)
    run_mypy(cwd=cwd)
    return run_coverage(cwd=cwd)


def run_all_test(cwd=None):
    run_pre_commit(cwd=cwd)
    return run_coverage(cwd=cwd)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        cwd = sys.argv[2] if len(sys.argv) > 2 else None
        if cmd == "all_tools":
            run_all_tools(cwd=cwd)
        elif cmd == "all_test":
            run_all_test(cwd=cwd)
        elif cmd == "upload_coverage":
            upload_coverage(cwd=cwd)
        elif cmd == "upload_code_qlib":
            upload_code_qlib(cwd=cwd)
        elif cmd == "upload_code_kaggle":
            upload_code_kaggle(cwd=cwd)
        elif cmd == "upload_code_data_science":
            upload_code_data_science(cwd=cwd)
        elif cmd == "pylint":
            run_pylint(cwd=cwd)
        elif cmd == "bandit":
            run_bandit(cwd=cwd)
        elif cmd == "mypy":
            run_mypy(cwd=cwd)
        elif cmd == "pytest":
            run_pytest(cwd=cwd)
        elif cmd == "pre_commit":
            run_pre_commit(cwd=cwd)
        elif cmd == "coverage":
            run_coverage(cwd=cwd)
        else:
            logger.error(f"Unknown command: {cmd}")
    else:
        logger.error("No command specified.")