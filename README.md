# ome-types

[![License](https://img.shields.io/github/license/tlambert03/ome-types)](LICENSE)
[![Version](https://img.shields.io/pypi/v/ome-types.svg)](https://pypi.python.org/pypi/ome-types)
[![CondaVersion](https://img.shields.io/conda/v/conda-forge/ome-types)](https://anaconda.org/conda-forge/ome-types)
[![Python
Version](https://img.shields.io/pypi/pyversions/ome-types.svg)](https://python.org)
[![Tests](https://github.com/tlambert03/ome-types/workflows/tests/badge.svg)](https://github.com/tlambert03/ome-types/actions)
[![Docs](https://readthedocs.org/projects/ome-types/badge/?version=latest)](https://ome-types.readthedocs.io/en/latest/?badge=latest)
<!-- [![conda-forge](https://img.shields.io/conda/vn/conda-forge/ome-types)](https://anaconda.org/conda-forge/ome-types) -->

## A pure-python implementation of the OME data model

`ome_types` provides a set of python dataclasses and utility functions for
parsing the [OME-XML
format](https://docs.openmicroscopy.org/ome-model/latest/ome-xml/) into
fully-typed python objects for interactive or programmatic access in python. It
can also take these python objects and output them into valid OME-XML.
`ome_types` is a **pure python** library and does not require a Java virtual
machine.

> Note: The generated python code can be seen in the [`built`
branch](https://github.com/tlambert03/ome-types/tree/built).
(Read the [code generation](#code-generation) section for details).

### 📖  &nbsp;&nbsp;[documentation](https://ome-types.readthedocs.io/)

## Installation

### from pip

```shell
pip install ome-types
```

### from source

```shell
git clone https://github.com/tlambert03/ome-types.git
cd ome-types
pip install -e .
```

## Usage

### convert an XML string or filepath into an instance of `ome_types.model.OME`

(The XML string/file will be validated against the [ome.xsd
schema](https://www.openmicroscopy.org/Schemas/Documentation/Generated/OME-2016-06/ome.html))

```python
from ome_types import from_xml

ome = from_xml('tests/data/hcs.ome.xml')
```

### extract OME metadata from an OME-TIFF

```python
from ome_types import from_tiff

ome2 = from_tiff('tests/data/ome.tiff')
```

### manipulate the metadata via python objects

Both `from_xml` and `from_tiff` return an instance of `ome_types.model.OME`. All
classes in `ome_types.model` follow the naming conventions of the [OME data
model](https://www.openmicroscopy.org/Schemas/Documentation/Generated/OME-2016-06/ome.html),
but use `snake_case` attribute names instead of `CamelCase`, to be consistent
with the python ecosystem.

```python
In [2]: ome = from_xml('tests/data/hcs.ome.xml')

In [3]: ome
Out[3]:
OME(
    images=[<1 Images>],
    plates=[<1 Plates>],
)

In [4]: ome.plates[0]
Out[4]:
Plate(
    id='Plate:1',
    name='Control Plate',
    column_naming_convention='letter',
    columns=12,
    row_naming_convention='number',
    rows=8,
    wells=[<1 Wells>],
)


In [5]: ome.images[0]
Out[5]:
Image(
    id='Image:0',
    name='Series 1',
    pixels=Pixels(
        id='Pixels:0',
        dimension_order='XYCZT',
        size_c=3,
        size_t=16,
        size_x=1024,
        size_y=1024,
        size_z=1,
        type='uint16',
        bin_data=[<1 Bin_Data>],
        channels=[<3 Channels>],
        physical_size_x=0.207,
        physical_size_y=0.207,
        time_increment=120.1302,
    ),
    acquisition_date=datetime.fromisoformat('2008-02-06T13:43:19'),
    description='An example OME compliant file, based on Olympus.oib',
)
```

#### Objects can be removed, or changed

```python
In [6]: from ome_types.model.simple_types import UnitsLength

In [7]: from ome_types.model.channel import AcquisitionMode

In [8]: ome.images[0].description = "This is the new description."

In [9]: ome.images[0].pixels.physical_size_x = 350.0

In [10]: ome.images[0].pixels.physical_size_x_unit = UnitsLength.NANOMETER

In [11]: for c in ome.images[0].pixels.channels:
             c.acquisition_mode = AcquisitionMode.SPINNING_DISK_CONFOCAL
```

#### Elements can be added by constructing new OME model objects

```python
In [12]: from ome_types.model import Instrument, Microscope, Objective, InstrumentRef

In [13]: microscope_mk4 = Microscope(
             manufacturer='OME Instruments',
             model='Lab Mk4',
             serial_number='L4-5678',
         )

In [14]: objective_40x = Objective(
             manufacturer='OME Objectives',
             model='40xAir',
             nominal_magnification=40.0,
         )

In [15]: instrument = Instrument(
             microscope=microscope_mk4,
             objectives=[objective_40x],
         )

In [16]: ome.instruments.append(instrument)

In [17]: ome.images[0].instrument_ref = InstrumentRef(id=instrument.id)

In [18]: ome.instruments
Out[18]:
[Instrument(
    id='Instrument:1',
    microscope=Microscope(
       manufacturer='OME Instruments',
       model='Lab Mk4',
       serial_number='L4-5678',
    ),
    objectives=[<1 Objectives>],
 )]
 ```

### export to an OME-XML string

Finally, you can generate the OME-XML representation of the OME model object,
for writing to a standalone `.ome.xml` file or inserting into the header of an
OME-TIFF file:

```python
In [19]: from ome_types import to_xml

In [20]: print(to_xml(ome))
<OME ...>
    <Plate ColumnNamingConvention="letter" Columns="12" ID="Plate:1" ...>
        ...
    </Plate>
    <Instrument ID="Instrument:1">
        <Microscope Manufacturer="OME Instruments" Model="Lab Mk4" SerialNumber="L4-5678" />
        <Objective Manufacturer="OME Objectives" Model="40xAir" ID="Objective:1"
        NominalMagnification="40.0" />
    </Instrument>
    <Image ID="Image:0" Name="Series 1">
        <AcquisitionDate>2008-02-06T13:43:19</AcquisitionDate>
        <Description>This is the new description.</Description>
        <InstrumentRef ID="Instrument:1" />
        <Pixels ... PhysicalSizeX="350.0" PhysicalSizeXUnit="nm" ...>
            <Channel AcquisitionMode="SpinningDiskConfocal" ...>
             ...
        </Pixels>
    </Image>
</OME>
```

## Code generation

The bulk of this library (namely, the `ome_types.model` module) is generated
at install time, and is therefore not checked into source (or visible in the main
branch of this repo).

You can see the code generated by the main branch in the [built
branch](https://github.com/tlambert03/ome-types/tree/built)


The script at `src/ome_autogen.py` converts the [ome.xsd
schema](https://www.openmicroscopy.org/Schemas/OME/2016-06/ome.xsd) into valid
python code. To run the code generation script in a development environment,
clone this repository and run:

```sh
python src/ome_autogen.py
```

As an example, the
[`OME/Image`](https://www.openmicroscopy.org/Schemas/Documentation/Generated/OME-2016-06/ome_xsd.html#Image)
model will be rendered as the following dataclass in `ome_types/model/image.py`

```python
from datetime import datetime
from typing import List, Optional

from pydantic import Field

from ome_types._base_type import OMEType

from .annotation_ref import AnnotationRef
from .experiment_ref import ExperimentRef
from .experimenter_group_ref import ExperimenterGroupRef
from .experimenter_ref import ExperimenterRef
from .imaging_environment import ImagingEnvironment
from .instrument_ref import InstrumentRef
from .microbeam_manipulation_ref import MicrobeamManipulationRef
from .objective_settings import ObjectiveSettings
from .pixels import Pixels
from .roi_ref import ROIRef
from .simple_types import ImageID
from .stage_label import StageLabel


class Image(OMEType):
    id: ImageID
    pixels: Pixels
    acquisition_date: Optional[datetime] = None
    annotation_ref: List[AnnotationRef] = Field(default_factory=list)
    description: Optional[str] = None
    experiment_ref: Optional[ExperimentRef] = None
    experimenter_group_ref: Optional[ExperimenterGroupRef] = None
    experimenter_ref: Optional[ExperimenterRef] = None
    imaging_environment: Optional[ImagingEnvironment] = None
    instrument_ref: Optional[InstrumentRef] = None
    microbeam_manipulation_ref: List[MicrobeamManipulationRef] = Field(
        default_factory=list
    )
    name: Optional[str] = None
    objective_settings: Optional[ObjectiveSettings] = None
    roi_ref: List[ROIRef] = Field(default_factory=list)
    stage_label: Optional[StageLabel] = None
```

The documentation and types for the full model can be in the [API Reference](https://ome-types.readthedocs.io/en/latest/ome_types.model.html)

## Contributing

To clone and install this repository locally (this will also build the model at
`src/ome_types/model`)

```shell
git clone https://github.com/tlambert03/ome-types.git
cd ome-types
pip install -e .[autogen]
```

We use `pre-commit` to run various code-quality checks (isort, black, mypy,
flake8) during continuous integration.  If you'd like to make sure that your
code will pass these checks before you commit your code, you should install
`pre-commit` after cloning this repository:

```shell
pip install pre-commit
pre-commit install
```

If you modify `src/ome_autogen.py`, you may need to regenerate the model with:

```shell
python src/ome_autogen.py
```

### Running tests

To run tests quickly, just install and run `pytest`.  Note, however, that this
requires that the `ome_types.model` module has already been built with `python
src/ome_autogen.py`.

Alternatively, you can install and run `tox` which will run tests and
code-quality checks in an isolated environment.
