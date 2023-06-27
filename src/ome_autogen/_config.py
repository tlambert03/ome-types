from xsdata.codegen.writer import CodeWriter
from xsdata.models import config as cfg
from xsdata.utils import text

from ome_autogen._util import camel_to_snake

from ._generator import OmeGenerator

OME_BASE_TYPE = "ome_types2.model._mixins.OMEType"

OUTPUT_PACKAGE = "ome_types2.model.ome_2016_06"
OME_FORMAT = "OME"


def get_config(
    package: str = OUTPUT_PACKAGE, kw_only: bool = True, compound_fields: bool = False
) -> cfg.GeneratorConfig:
    # ALLOW "type" to be used as a field name
    text.stop_words.discard("type")

    # use our own camel_to_snake
    # Our's interprets adjacent capital letters as two words
    # NameCase.SNAKE: 'PositionXUnit' -> 'position_xunit'
    # camel_to_snake: 'PositionXUnit' -> 'position_x_unit'
    cfg.__name_case_func__["snakeCase"] = camel_to_snake

    #  critical to be able to use the format="OME"
    CodeWriter.register_generator(OME_FORMAT, OmeGenerator)

    # add our own base type to every class
    ome_extension = cfg.GeneratorExtension(
        type=cfg.ExtensionType.CLASS,
        class_name=".*",
        import_string=OME_BASE_TYPE,
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
        extensions=cfg.GeneratorExtensions([ome_extension]),
        # Don't convert things like XMLAnnotation to XmlAnnotation
        conventions=cfg.GeneratorConventions(class_name=keep_case),
    )


# # These are the fields with compound "chices"
# OME ['Projects', 'Datasets', 'Folders', 'Experiments', 'Plates', 'Screens',
#      'Experimenters', 'ExperimenterGroups', 'Instruments', 'Images',
#      'StructuredAnnotations', 'ROIs', 'BinaryOnly']
# Pixels ['BinDataBlocks', 'TiffDataBlocks', 'MetadataOnly']
# Instrument ['GenericExcitationSource', 'LightEmittingDiode', 'Filament', 'Arc', 'Laser']
# BinaryFile ['External', 'BinData']
# StructuredAnnotations ['XMLAnnotation', 'FileAnnotation', 'ListAnnotation', 
#                        'LongAnnotation', 'DoubleAnnotation', 'CommentAnnotation',
#                        'BooleanAnnotation', 'TimestampAnnotation', 'TagAnnotation',
#                        'TermAnnotation', 'MapAnnotation']
# Union ['Label', 'Polygon', 'Polyline', 'Line', 'Ellipse', 'Point', 'Mask', 'Rectangle']