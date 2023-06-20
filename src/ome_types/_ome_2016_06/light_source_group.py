from typing import Union

from .arc import Arc
from .filament import Filament
from .generic_excitation_source import GenericExcitationSource
from .laser import Laser
from .light_emitting_diode import LightEmittingDiode
from .light_source import LightSource

LightSourceGroup = LightSource

LightSourceGroupType = Union[
    Laser, Arc, Filament, LightEmittingDiode, GenericExcitationSource
]
