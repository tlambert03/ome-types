from pydantic import root_validator

from ome_types._mixins._base_type import OMEType


class PixelsMixin(OMEType):
    @root_validator(pre=True)
    def _validate_root(cls, values: dict) -> dict:
        if "metadata_only" in values:
            if isinstance(values["metadata_only"], bool):
                if not values["metadata_only"]:
                    values.pop("metadata_only")
                else:
                    # type ignore in case the autogeneration hasn't been built
                    from ome_types.model import MetadataOnly  # type: ignore

                    values["metadata_only"] = MetadataOnly()

        return values
