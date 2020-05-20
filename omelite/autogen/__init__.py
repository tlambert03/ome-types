from .schema import SchemaConverter


def convert_schema(schema_path, target_dir):
    SchemaConverter(schema_path).write(target_dir)
