Usage
=====

``ome_types`` is useful for parsing the `OME-XML format
<https://docs.openmicroscopy.org/ome-model/latest/ome-xml/>`_ into Python
objects for interactive or programmatic access in python. It can also take
these Python objects and turn them back into OME-XML.

For example, you can parse an ome.xml, and then explore it with pythonic
``camel_case`` syntax and readable object representations:


.. code-block:: python

    In [1]: from ome_types import from_xml

    In [2]: ome = from_xml('testing/data/hcs.ome.xml')

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

    In [5]: ome.plates[0].wells[0]
    Out[5]: 
    Well(
        id='Well:1',
        column=0,
        row=0,
        well_samples=[<1 Well_Samples>],
    )

    In [6]: ome.images[0]
    Out[6]: 
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

    In [7]: ome.images[0].pixels.channels[0]
    Out[7]: 
    Channel(
        id='Channel:0:0',
        name='CH1',
        acquisition_mode='LaserScanningConfocalMicroscopy',
        emission_wavelength=523.0,
        excitation_wavelength=488.0,
        illumination_type='Epifluorescence',
        pinhole_size=103.5,
        samples_per_pixel=1,
    )

    In [8]: ome.images[0].pixels.channels[0].emission_wavelength                                                                               
    Out[8]: 523.0

Then you might want to make some changes:

.. code-block:: python

   In [9]: from ome_types.model.simple_types import UnitsLength

   In [10]: from ome_types.model.channel import AcquisitionMode

   In [11]: ome.images[0].description = "This is the new description."

   In [12]: ome.images[0].pixels.physical_size_x = 350.0

   In [13]: ome.images[0].pixels.physical_size_x_unit = UnitsLength.NANOMETER

   In [14]: for c in ome.images[0].pixels.channels:
                c.acquisition_mode = AcquisitionMode.SPINNING_DISK_CONFOCAL

And add elements by constructing new OME model objects:

.. code-block:: python

   In [15]: from ome_types.model import Instrument, Microscope, Objective, InstrumentRef

   In [16]: microscope_mk4 = Microscope(
                manufacturer='OME Instruments',
                model='Lab Mk4',
                serial_number='L4-5678',
            )

   In [17]: objective_40x = Objective(
                manufacturer='OME Objectives',
                model='40xAir',
                nominal_magnification=40.0,
            )

   In [18]: instrument = Instrument(
                microscope=microscope_mk4,
                objectives=[objective_40x],
            )

   In [19]: ome.instruments.append(instrument)

   In [20]: ome.images[0].instrument_ref = InstrumentRef(instrument.id)

   In [21]: ome.instruments
   Out[21]:
   [Instrument(
       id='Instrument:1',
       microscope=Microscope(
          manufacturer='OME Instruments',
          model='Lab Mk4',
          serial_number='L4-5678',
       ),
       objectives=[<1 Objectives>],
    )]

Finally, you can generate the OME-XML representation of the OME model object,
for writing to a standalone .ome.xml file or inserting into the header of an
OME-TIFF file:

.. code-block:: python

    In [22]: from ome_types import to_xml

    In [23]: print(to_xml(ome))
    <OME ...>
        <Plate ColumnNamingConvention="letter" Columns="12" ID="Plate:1" ...>
            ...
        </Plate>
        <Instrument ID="Instrument:1">
            <Microscope Manufacturer="OME Instruments" Model="Lab Mk4" SerialNumber="L4-5678" />
            <Objective Manufacturer="OME Objectives" Model="40xAir" ID="Objective:1" NominalMagnification="40.0" />
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

