from typing import TYPE_CHECKING, Protocol, TypeAlias, TypeVar, Union

if TYPE_CHECKING:
    from ome_types.model import (
        Arc,
        Filament,
        GenericExcitationSource,
        Laser,
        LightEmittingDiode,
    )

    LightSource: TypeAlias = Union[
        GenericExcitationSource, LightEmittingDiode, Filament, Arc, Laser
    ]

    class HasLightSources(Protocol):
        generic_excitation_source: list[GenericExcitationSource]
        light_emitting_diode: list[LightEmittingDiode]
        filament: list[Filament]
        arc: list[Arc]
        laser: list[Laser]

    T = TypeVar("T", bound=HasLightSources)


class InstrumentMixin:
    @property
    def light_source_group(self: "T") -> "list[LightSource]":
        return [
            *self.arc,
            *self.filament,
            *self.generic_excitation_source,
            *self.laser,
            *self.light_emitting_diode,
        ]
