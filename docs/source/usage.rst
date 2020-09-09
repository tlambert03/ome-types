Usage
=====

``ome_types`` is useful for parsing the `OME XML format
<https://docs.openmicroscopy.org/ome-model/5.6.3/ome-xml/>`_ into python
classes for interactive or programmatic access in python.

For example, you can parse an ome.xml, and then explore it with pythonic,
``camel_case`` syntax and nice object representations:


.. code-block:: python

    In [1]: from ome_types import from_xml

    In [2]: ome = from_xml('path/to/metadata.ome.xml')

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


You can also construct OME model objects (output to XML coming)

.. code-block:: python

    In [1]: from ome_types.model import Channel

    In [4]: channel = Channel( 
       ...:     excitation_wavelength=475, 
       ...:     excitation_wavelength_unit="nm", 
       ...:     emission_wavelength=530000, 
       ...:     emission_wavelength_unit="pm", 
       ...: )

    In [5]: channel
    Out[5]:
    Channel(
        id='Channel:3',
        emission_wavelength=530000.0,
        emission_wavelength_unit='pm',
        excitation_wavelength=475.0,
    )
