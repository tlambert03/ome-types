import ome_types
import ome_types2.model


def test_names():
    new_model = ome_types2.model.OME.__pydantic_model__.schema()
    old_model = ome_types.model.OME.schema()
    assert set(old_model["properties"]) == set(new_model["properties"])

    for key, value in old_model["definitions"].items():
        new_props = new_model["definitions"][key]["properties"]
        assert set(value["properties"]) == set(new_props)
