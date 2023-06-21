import pytest

import ome_types
import ome_types2.model

V1_PLURAL_ERRORS = {
    "leader",
    "annotation_ref",
    "image_ref",
    "experimenter_ref",
    "plate_ref",
    "folder_ref",
    "roi_ref",
    "well_sample_ref",
    "light_source_settings",
    "kind",
    "dataset_ref",
    "m",
}

NEW_MODEL = ome_types2.model.OME.__pydantic_model__.schema()
OLD_MODEL = ome_types.model.OME.schema()


def test_top_props():
    assert set(OLD_MODEL["properties"]) == set(NEW_MODEL["properties"])


@pytest.mark.parametrize("key", OLD_MODEL["definitions"])
def test_names(key):
    value = OLD_MODEL["definitions"][key]
    if key not in NEW_MODEL["definitions"]:
        if "__" in key:
            return
        raise AssertionError(f"{key} not in v2")
    new_props = set(NEW_MODEL["definitions"][key].get("properties", []))
    old_props = set(value.get("properties", []))
    if old_props != new_props:
        for accepted_error in V1_PLURAL_ERRORS:
            old_props.discard(accepted_error)
            for x in list(new_props):
                if x.startswith(accepted_error):
                    new_props.discard(x)
    if old_props != new_props:
        extra = new_props - old_props
        missing = old_props - new_props
        msg = f"{key} v2"
        if extra:
            msg += f" has extra prop: {extra}"
        if missing:
            msg += f" is missing prop: {missing}"
        raise AssertionError(msg)
