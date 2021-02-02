from pathlib import Path

from quilt3 import Package


def download_test_resources() -> None:
    root = Path(__file__).parent.parent.parent
    resources = (root / "aicsimageio" / "aicsimageio" / "tests" / "resources").resolve()
    resources.mkdir(exist_ok=True)
    package = Package.browse(
        "aicsimageio/test_resources", "s3://aics-modeling-packages-test-resources"
    )
    package["resources"].fetch(resources)


if __name__ == "__main__":
    download_test_resources()
