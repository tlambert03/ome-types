import pytest

import ome_types.model
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

NEW_MODEL = ome_types2.model.OME.schema()
OLD_MODEL = ome_types.model.OME.schema()


def test_top_props():
    assert set(OLD_MODEL["properties"]) == set(NEW_MODEL["properties"])


# @pytest.mark.parametrize("key", OLD_MODEL["definitions"])
# def test_names(key):
#     value = OLD_MODEL["definitions"][key]
#     if key not in NEW_MODEL["definitions"]:
#         if "__" in key:
#             return
#         raise AssertionError(f"{key} not in v2")
#     new_props = set(NEW_MODEL["definitions"][key].get("properties", []))
#     old_props = set(value.get("properties", []))
#     if old_props != new_props:
#         for accepted_error in V1_PLURAL_ERRORS:
#             old_props.discard(accepted_error)
#             for x in list(new_props):
#                 if x.startswith(accepted_error):
#                     new_props.discard(x)
#     if old_props != new_props:
#         extra = new_props - old_props
#         missing = old_props - new_props
#         msg = f"{key} v2"
#         if extra:
#             msg += f" has extra prop: {extra}"
#         if missing:
#             msg += f" is missing prop: {missing}"
#         raise AssertionError(msg)

ACCEPTED_CHANGES = [
    (
        "MicrobeamManipulation",
        "light_source_settings",
        "light_source_settings_combinations",
    ),
    ("Pixels", "bin_data", "bin_data_blocks"),
    ("ExperimenterGroup", "leader", "leaders"),
]


@pytest.mark.parametrize("name", ome_types.model.__all__)
def test_field_names(name):
    if name not in ome_types2.model.ome_2016_06.__all__:
        raise AssertionError(f"{name} not in ome_2016_06")
    v1 = getattr(ome_types.model, name)
    v2 = getattr(ome_types2.model.ome_2016_06, name)

    # Known/acceptable differences
    v1.__fields__.pop("kind", None)
    v1.__fields__.pop("m", None)
    v2.__fields__.pop("ms", None)

    for model, old, new in ACCEPTED_CHANGES:
        if name == model and old in v1.__fields__:
            v1.__fields__[new] = v1.__fields__.pop(old)

    if set(v1.__fields__) != set(v2.__fields__):
        extra = set(v2.__fields__) - set(v1.__fields__)
        missing = set(v1.__fields__) - set(v2.__fields__)
        msg = "v2"
        if extra:
            msg += f" has extra props: {extra}"
        if missing:
            msg += f" is missing props: {missing}"
        raise AssertionError(msg)
