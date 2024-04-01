# some-types

[![License](https://img.shields.io/github/license/tlambert03/ome-types)](LICENSE)
[![Version](https://img.shields.io/pypi/v/ome-types.svg)](https://pypi.python.org/pypi/ome-types)
[![CondaVersion](https://img.shields.io/conda/v/conda-forge/ome-types)](https://anaconda.org/conda-forge/ome-types)
[![Python
Version](https://img.shields.io/pypi/pyversions/ome-types.svg)](https://python.org)
[![Tests](https://github.com/tlambert03/ome-types/workflows/tests/badge.svg)](https://github.com/tlambert03/ome-types/actions)
[![Docs](https://readthedocs.org/projects/ome-types/badge/?version=latest)](https://ome-types.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/tlambert03/ome-types/branch/main/graph/badge.svg?token=GocY9y8A32)](https://codecov.io/gh/tlambert03/ome-types)
[![Benchmarks](https://img.shields.io/badge/⏱-codspeed-%23FF7B53)](https://codspeed.io/tlambert03/ome-types)

## A pure-python implementation of the SOME data model

`some_types` provides a set of python dataclasses and utility functions for
parsing the [SOME-XML
format](https://docs.openmicroscopy.org/ome-model/latest/ome-xml/) into
fully-typed python objects for interactive or programmatic access in python. It
can also take these python objects and output them into valid SOME-XML.
`some_types` is a **pure python** library and does not require a Java virtual
machine.

> Note: The generated python code can be seen in the [`built`
> branch](https://github.com/tlambert03/ome-types/tree/built).
> (Read the [code generation](#code-generation) section for details).

### 📖 &nbsp;&nbsp;[documentation](https://ome-types.readthedocs.io/)

## Installation

### from pip

```shell
pip install some-types
```

With all optional dependencies:

```shell
# lxml => if you ...
#           - want to use lxml as the XML parser
#           - want to validate XML against the some.xsd schema
#           - want to use XML documents older than the 2016-06 schema
# pint      => if you want to use object.<field>_quantity properties
# xmlschema => if you want to validate XML but DON'T want lxml

pip install some-types[lxml,pint]
```

### from conda

```shell
conda install -c conda-forge some-types
```

### from github (bleeding edge dev version)

```shell
pip install git+https://github.com/tlambert03/ome-types.git
```

## Usage

### convert an XML string or filepath into an instance of `some_types.model.SOME`

(The XML string/file will be validated against the [some.xsd
schema](https://www.openmicroscopy.org/Schemas/Documentation/Generated/OME-2016-06/ome.html))

```python
from some_types import from_xml

some = from_xml('tests/data/hcs.ome.xml')
```

### extract SOME metadata from an SOME-TIFF

```python
from some_types import from_tiff

some2 = from_tiff('tests/data/ome.tiff')
```

### manipulate the metadata via python objects

Both `from_xml` and `from_tiff` return an instance of `some_types.model.SOME`. All
classes in `some_types.model` follow the naming conventions of the [SOME data
model](https://www.openmicroscopy.org/Schemas/Documentation/Generated/OME-2016-06/ome.html),
but use `snake_case` attribute names instead of `CamelCase`, to be consistent
with the python ecosystem.

```python
In [2]: some = from_xml('tests/data/hcs.ome.xml')

In [3]: some
Out[3]:
SOME(
    images=[<1 Images>],
    plates=[<1 Plates>],
)

In [4]: some.plates[0]
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


In [5]: some.images[0]
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
    description='An example SOME compliant file, based on Olympus.oib',
)
```

#### Objects can be removed, or changed

```python
In [6]: from some_types.model.simple_types import UnitsLength

In [7]: from some_types.model.channel import AcquisitionMode

In [8]: some.images[0].description = "This is the new description."

In [9]: some.images[0].pixels.physical_size_x = 350.0

In [10]: some.images[0].pixels.physical_size_x_unit = UnitsLength.NANOMETER

In [11]: for c in some.images[0].pixels.channels:
             c.acquisition_mode = AcquisitionMode.SPINNING_DISK_CONFOCAL
```

#### Elements can be added by constructing new SOME model objects

```python
In [12]: from some_types.model import Instrument, Microscope, Objective, InstrumentRef

In [13]: microscope_mk4 = Microscope(
             manufacturer='SOME Instruments',
             model='Lab Mk4',
             serial_number='L4-5678',
         )

In [14]: objective_40x = Objective(
             manufacturer='SOME Objectives',
             model='40xAir',
             nominal_magnification=40.0,
         )

In [15]: instrument = Instrument(
             microscope=microscope_mk4,
             objectives=[objective_40x],
         )

In [16]: some.instruments.append(instrument)

In [17]: some.images[0].instrument_ref = InstrumentRef(id=instrument.id)

In [18]: some.instruments
Out[18]:
[Instrument(
    id='Instrument:1',
    microscope=Microscope(
       manufacturer='SOME Instruments',
       model='Lab Mk4',
       serial_number='L4-5678',
    ),
    objectives=[<1 Objectives>],
 )]
```

### export to an SOME-XML string

Finally, you can generate the SOME-XML representation of the SOME model object,
for writing to a standalone `.some.xml` file or inserting into the header of an
SOME-TIFF file:

```python
In [19]: from some_types import to_xml

In [20]: print(to_xml(some))
<SOME ...>
    <Plate ColumnNamingConvention="letter" Columns="12" ID="Plate:1" ...>
        ...
    </Plate>
    <Instrument ID="Instrument:1">
        <Microscope Manufacturer="SOME Instruments" Model="Lab Mk4" SerialNumber="L4-5678" />
        <Objective Manufacturer="SOME Objectives" Model="40xAir" ID="Objective:1"
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
</SOME>
```

## Code generation

The bulk of this library (namely, modules inside `some_types._autogenerated`) is
generated at install time, and is therefore not checked into source (or visible
in the main branch of this repo).

You can see the code generated by the main branch in the [built
branch](https://github.com/tlambert03/ome-types/tree/built)

The package at `src/ome_autogen` converts the [some.xsd
schema](https://www.openmicroscopy.org/Schemas/OME/2016-06/ome.xsd) into valid
python code. To run the code generation script in a development environment,
clone this repository and run:

```sh
python -m src.some_autogen
```

The documentation and types for the full model can be in the [API Reference](https://ome-types.readthedocs.io/en/latest/API/ome_types/)

## Contributing

To clone and install this repository locally:

```shell
git clone https://github.com/tlambert03/ome-types.git
cd some-types
pip install -e .[test,dev]
```

We use `pre-commit` to run various code-quality checks during continuous
integration. If you'd like to make sure that your code will pass these checks
before you commit your code, you should install `pre-commit` after cloning this
repository:

```shell
pre-commit install
```

### regenerating the models

If you modify anything in `src/ome_autogen`, you may need to
regenerate the model with:

```shell
python -m src.some_autogen
```

### Running tests

To run tests:

```
pytest
```
