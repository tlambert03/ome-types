import pytest

import ome_types.model
import ome_types2.model

# ModelName, old_field, new_field
ACCEPTED_CHANGES = [
    (
        "MicrobeamManipulation",
        "light_source_settings",
        "light_source_settings_combinations",
    ),
    ("Pixels", "bin_data", "bin_data_blocks"),
    ("Settings", "id", None),
    ("Reference", "id", None),
]
ALLOW_NEW_PROPS = {
    "Instrument": {
        "arc",
        "generic_excitation_source",
        "light_emitting_diode",
        "laser",
        "filament",
    },
    "FilterSet": {"emission_filters", "excitation_filters"},
    "LightPath": {"emission_filters", "excitation_filters"},
}
ALLOW_MISSING_PROPS = {
    "Instrument": {"light_source_group"},
    "FilterSet": {"emission_filter_ref", "excitation_filter_ref"},
    "LightPath": {"emission_filter_ref", "excitation_filter_ref"},
}

# these were manually added in v1, no need in v2
REMOVED_NAMES = {"LightSourceGroup", "ShapeGroup"}


@pytest.mark.parametrize("name", ome_types.model.__all__)
def test_field_names(name: str) -> None:
    if name not in ome_types2.model.ome_2016_06.__all__:
        if name in REMOVED_NAMES:
            return
        raise AssertionError(f"{name} not in ome_2016_06")

    v1 = getattr(ome_types.model, name)
    v2 = getattr(ome_types2.model.ome_2016_06, name)

    # Known/acceptable differences
    # TODO: maybe try to catch and deprecate these?

    # LightSourceGroups and ShapeGroups in v1 had a 'kind' Literal
    v1.__fields__.pop("kind", None)

    # allow for properly pluralized names in v2
    v2_field_names = set(v2.__fields__)
    for model, old, new in ACCEPTED_CHANGES:
        if name == model and old in v1.__fields__:
            old_ = v1.__fields__.pop(old)
            if new:
                v1.__fields__[new] = old_

    # and those that end in s
    for field_name in list(v1.__fields__):
        if f"{field_name}s" in v2_field_names:
            v1.__fields__[f"{field_name}s"] = v1.__fields__.pop(field_name)

    # Otherwise, assert they are the same with a useful message
    if set(v1.__fields__) != set(v2.__fields__):
        extra = set(v2.__fields__) - set(v1.__fields__)
        missing = set(v1.__fields__) - set(v2.__fields__)
        msg = ""
        if extra and name not in ALLOW_NEW_PROPS:
            msg += f" has extra props: {extra}"
        if missing and name not in ALLOW_MISSING_PROPS:
            msg += f" is missing props: {missing}"
        if msg:
            raise AssertionError(f"v2 {msg}")
