import pytest
from pydantic import ValidationError
from pint import DimensionalityError
from ome_types.model import Channel, Laser, Plane
from ome_types.dataclasses import ureg


def test_quantity_math():
    """Validate math on quantities with different but compatible units."""
    channel = Channel(
        excitation_wavelength=475,
        excitation_wavelength_unit="nm",
        emission_wavelength=530000,
        emission_wavelength_unit="pm",
    )
    shift = (
        channel.emission_wavelength_quantity - channel.excitation_wavelength_quantity
    )
    # Compare to a tolerance due to Pint internal factor representation.
    assert abs(shift.to("nm").m - 55) < 1e-12


def test_invalid_unit():
    """Ensure incompatible units in constructor raises ValidationError."""
    with pytest.raises(ValidationError):
        Channel(
            excitation_wavelength=475, excitation_wavelength_unit="kg",
        )


def test_dimensionality_error():
    """Ensure math on incompatible units raises DimensionalityError."""
    laser = Laser(
        id="LightSource:1",
        repetition_rate=10,
        repetition_rate_unit="MHz",
        wavelength=640,
    )
    with pytest.raises(DimensionalityError):
        laser.repetition_rate_quantity + laser.wavelength_quantity


def test_reference_frame():
    """Validate reference_frame behavior."""
    plane = Plane(
        the_c=0,
        the_t=0,
        the_z=0,
        position_x=1,
        position_x_unit="reference frame",
        position_y=2,
        position_y_unit="mm",
    )
    # Verify two different ways that reference_frame and length are incompatible.
    with pytest.raises(DimensionalityError):
        plane.position_x_quantity + plane.position_y_quantity
    product = plane.position_x_quantity * plane.position_y_quantity
    assert not product.check("[area]")
    # Verify that we can obtain a usable length if we know the conversion factor.
    conversion_factor = ureg.Quantity(1, "micron/reference_frame")
    position_x = plane.position_x_quantity * conversion_factor
    assert position_x.check("[length]")
