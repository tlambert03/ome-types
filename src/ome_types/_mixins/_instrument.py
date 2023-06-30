from typing import TYPE_CHECKING, TypeAlias, Union, cast

if TYPE_CHECKING:
    from ome_types.model import (
        Arc,
        Filament,
        GenericExcitationSource,
        Instrument,
        Laser,
        LightEmittingDiode,
    )

    LightSource: TypeAlias = Union[
        GenericExcitationSource, LightEmittingDiode, Filament, Arc, Laser
    ]


class InstrumentMixin:
    @property
    def light_source_group(self) -> "list[LightSource]":
        slf = cast("Instrument", self)
        return [
            *slf.arcs,
            *slf.filaments,
            *slf.generic_excitation_sources,
            *slf.lasers,
            *slf.light_emitting_diodes,
        ]
