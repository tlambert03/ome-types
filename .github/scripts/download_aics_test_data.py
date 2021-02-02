from pathlib import Path

from quilt3 import Package


def download_test_resources() -> None:
    root = Path(__file__).parent.parent.parent
    print("root is", root)
    resources = (root / "aicsimageio" / "tests" / "resources").resolve()
    print("resources is", resources)
    resources.mkdir(exist_ok=True)
    package = Package.browse(
        "aicsimageio/test_resources", "s3://aics-modeling-packages-test-resources"
    )
    package["resources"].fetch(resources)


if __name__ == "__main__":
    download_test_resources()