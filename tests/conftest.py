from pathlib import Path

import pytest

# SHOULD_FAIL_VALIDATION = {"invalid_xml_annotation", "bad"}
# SHOULD_FAIL_ROUNDTRIP = {
#     # Order of elements in StructuredAnnotations and Union are jumbled.
#     "timestampannotation-posix-only",
#     "transformations-downgrade",
#     "invalid_xml_annotation",
# }
# SHOULD_FAIL_ROUNDTRIP_LXML = {
#     "folders-simple-taxonomy",
#     "folders-larger-taxonomy",
# }
# SKIP_ROUNDTRIP = {
#     # These have XMLAnnotations with extra namespaces and mixed content, which
#     # the automated round-trip test code doesn't properly verify yet. So even
#     # though these files do appear to round-trip correctly when checked by eye,
#     # we'll play it safe and skip them until the test is fixed.
#     "spim",
#     "xmlannotation-body-space",
#     "xmlannotation-multi-value",
#     "xmlannotation-svg",
# }

DATA = Path(__file__).parent / "data"
ALL_XML = set(DATA.glob("*.ome.xml"))
INVALID = {DATA / "invalid_xml_annotation.ome.xml", DATA / "bad.ome.xml"}


def _true_stem(p: Path) -> str:
    return p.name.partition(".")[0]


@pytest.fixture(params=sorted(ALL_XML), ids=_true_stem)
def any_xml(request: pytest.FixtureRequest) -> Path:
    return request.param


@pytest.fixture(params=sorted(ALL_XML - INVALID), ids=_true_stem)
def valid_xml(request: pytest.FixtureRequest) -> Path:
    return request.param


@pytest.fixture(params=INVALID, ids=_true_stem)
def invalid_xml(request: pytest.FixtureRequest) -> Path:
    return request.param
