import platform
import sys

from packaging.version import parse as parse_version, Version


def print_runtime_info():
    print(f"Python {sys.version} on {platform.system()} {platform.release()}")


def get_installed_packages():
    import importlib.metadata
    installed_packages = {}
    for package_name in importlib.metadata.packages_distributions().keys():
        try:
            installed_packages[package_name.lower()] = importlib.metadata.version(package_name)
        except importlib.metadata.PackageNotFoundError:
            pass
    return installed_packages


def print_filtered_packages(installed_packages, filtered_packages):
    for package_name in filtered_packages:
        version = installed_packages.get(package_name.lower())
        if version:
            print(f"{package_name}=={version}")


if __name__ == "__main__":
    print_runtime_info()
    filtered_packages = [
        "transformers",
        "accelerate",
        "torch",
        "tensorflow",
        "pandas",
        "numpy",
        "scikit-learn",
        "scipy",
        "lightgbm",
        "vtk",
        "opencv-python",
        "keras",
        "matplotlib",
        "pydicom",
    ]
    installed_packages = get_installed_packages()
    print_filtered_packages(installed_packages, filtered_packages)

