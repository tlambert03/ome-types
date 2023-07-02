from __future__ import annotations

from xsdata.codegen.writer import CodeWriter
from xsdata.models import config as cfg
from xsdata.utils import text

from ome_autogen._generator import OmeGenerator
from ome_autogen._util import camel_to_snake

MIXIN_MODULE = "ome_types._mixins"
MIXINS: list[tuple[str, str, bool]] = [
    (".*", f"{MIXIN_MODULE}._base_type.OMEType", False),  # base type on every class
    ("OME", f"{MIXIN_MODULE}._ome.OMEMixin", True),
    ("Instrument", f"{MIXIN_MODULE}._instrument.InstrumentMixin", False),
    ("Reference", f"{MIXIN_MODULE}._reference.ReferenceMixin", True),
    ("BinData", f"{MIXIN_MODULE}._bin_data.BinDataMixin", True),
    (
        "StructuredAnnotations",
        f"{MIXIN_MODULE}._structured_annotations.StructuredAnnotationsMixin",
        True,
    ),
]

ALLOW_RESERVED_NAMES = {"type", "Type", "Union"}
OME_FORMAT = "OME"


def get_config(
    package: str, kw_only: bool = True, compound_fields: bool = False
) -> cfg.GeneratorConfig:
    # ALLOW "type" to be used as a field name
    text.stop_words.difference_update(ALLOW_RESERVED_NAMES)

    # use our own camel_to_snake
    # Our's interprets adjacent capital letters as two words
    # NameCase.SNAKE: 'PositionXUnit' -> 'position_xunit'
    # camel_to_snake: 'PositionXUnit' -> 'position_x_unit'
    cfg.__name_case_func__["snakeCase"] = camel_to_snake

    #  critical to be able to use the format="OME"
    CodeWriter.register_generator(OME_FORMAT, OmeGenerator)

    mixins = []
    for class_name, import_string, prepend in MIXINS:
        mixins.append(
            cfg.GeneratorExtension(
                type=cfg.ExtensionType.CLASS,
                class_name=class_name,
                import_string=import_string,
                prepend=prepend,
            )
        )

    keep_case = cfg.NameConvention(cfg.NameCase.ORIGINAL, "type")
    return cfg.GeneratorConfig(
        output=cfg.GeneratorOutput(
            package=package,
            # format.value lets us use our own generator
            # kw_only is important, it makes required fields actually be required
            format=cfg.OutputFormat(value=OME_FORMAT, kw_only=kw_only),
            structure_style=cfg.StructureStyle.CLUSTERS,
            docstring_style=cfg.DocstringStyle.NUMPY,
            compound_fields=cfg.CompoundFields(enabled=compound_fields),
        ),
        # Add our mixins
        extensions=cfg.GeneratorExtensions(mixins),
        # Don't convert things like XMLAnnotation to XmlAnnotation
        conventions=cfg.GeneratorConventions(class_name=keep_case),
    )
