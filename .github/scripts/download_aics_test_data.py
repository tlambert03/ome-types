from pathlib import Path

from quilt3 import Package


def download_test_resources() -> None:
    root = Path(__file__).parent.parent.parent
    resources = (root / "aicsimageio" / "aicsimageio" / "tests" / "resources").resolve()

    # Get the specific hash for test resources
    with open(root / "aicsimageio" / "scripts" / "TEST_RESOURCES_HASH.txt", "r") as f:
        top_hash = f.readline().strip()

    # Download test resources
    resources.mkdir(exist_ok=True)
    package = Package.browse(
        "aicsimageio/test_resources",
        "s3://aics-modeling-packages-test-resources",
        top_hash=top_hash,
    )
    package["resources"].fetch(resources)


if __name__ == "__main__":
    download_test_resources()
