from ome_types.model import OME, modulo

m = modulo.ModuloAnnotation()
m.value.modulos.modulo_along_c = modulo.Modulo(
    type=modulo.ModuloType.ANGLE, start=0, end=360
)

ome = OME()
ome.structured_annotations.append(m)

print(ome.to_xml())
