"""
    Test conversions in core.py
"""

# Standard library
import tempfile

# Third-party
import astropy.coordinates as coord
import astropy.units as u
from astropy.utils.data import get_pkg_data_filename
from astropy.tests.helper import quantity_allclose
import numpy as np

# This package
from ..velocity_frame_transforms import (vgal_to_hel, vhel_to_gal,
                                         vgsr_to_vhel, vhel_to_vgsr)


def test_vgsr_to_vhel():
    filename = get_pkg_data_filename('idl_vgsr_vhel.txt')
    data = np.genfromtxt(filename, names=True, skip_header=2)

    # one row
    row = data[0]
    l = coord.Angle(row["lon"] * u.degree)
    b = coord.Angle(row["lat"] * u.degree)
    c = coord.Galactic(l, b)
    vgsr = row["vgsr"] * u.km/u.s
    vlsr = [row["vx"],row["vy"],row["vz"]]*u.km/u.s # this is right
    vcirc = row["vcirc"]*u.km/u.s

    vsun = vlsr + [0,1,0]*vcirc
    vhel = vgsr_to_vhel(c, vgsr, vsun=vsun)
    return
    np.testing.assert_almost_equal(vhel.value, row['vhelio'], decimal=4)

    # now check still get right answer passing in ICRS coordinates
    vhel = vgsr_to_vhel(c.transform_to(coord.ICRS), vgsr, vsun=vsun)
    np.testing.assert_almost_equal(vhel.value, row['vhelio'], decimal=4)

    # all together now
    l = coord.Angle(data["lon"] * u.degree)
    b = coord.Angle(data["lat"] * u.degree)
    c = coord.Galactic(l, b)
    vgsr = data["vgsr"] * u.km/u.s
    vhel = vgsr_to_vhel(c, vgsr, vsun=vsun)
    np.testing.assert_almost_equal(vhel.value, data['vhelio'], decimal=4)

    # now check still get right answer passing in ICRS coordinates
    vhel = vgsr_to_vhel(c.transform_to(coord.ICRS), vgsr, vsun=vsun)
    np.testing.assert_almost_equal(vhel.value, data['vhelio'], decimal=4)


def test_vgsr_to_vhel_misc():
    # make sure it works with longitude in 0-360 or -180-180
    l1 = coord.Angle(190.*u.deg)
    l2 = coord.Angle(-170.*u.deg)
    b = coord.Angle(30.*u.deg)

    c1 = coord.Galactic(l1, b)
    c2 = coord.Galactic(l2, b)

    vgsr = -110.*u.km/u.s
    vhel1 = vgsr_to_vhel(c1, vgsr)
    vhel2 = vgsr_to_vhel(c2, vgsr)

    np.testing.assert_almost_equal(vhel1.value, vhel2.value, decimal=9)


def test_vhel_to_vgsr():
    filename = get_pkg_data_filename('idl_vgsr_vhel.txt')
    data = np.genfromtxt(filename, names=True, skip_header=2)

    # one row
    row = data[0]
    l = coord.Angle(row["lon"] * u.degree)
    b = coord.Angle(row["lat"] * u.degree)
    c = coord.Galactic(l, b)
    vhel = row["vhelio"] * u.km/u.s
    vlsr = [row["vx"],row["vy"],row["vz"]]*u.km/u.s # this is right
    vcirc = row["vcirc"]*u.km/u.s

    vsun = vlsr + [0,1,0]*vcirc
    vgsr = vhel_to_vgsr(c, vhel, vsun=vsun)
    np.testing.assert_almost_equal(vgsr.value, row['vgsr'], decimal=4)

    # now check still get right answer passing in ICRS coordinates
    vgsr = vhel_to_vgsr(c.transform_to(coord.ICRS), vhel, vsun=vsun)
    np.testing.assert_almost_equal(vgsr.value, row['vgsr'], decimal=4)

    # all together now
    l = coord.Angle(data["lon"] * u.degree)
    b = coord.Angle(data["lat"] * u.degree)
    c = coord.Galactic(l, b)
    vhel = data["vhelio"] * u.km/u.s
    vgsr = vhel_to_vgsr(c, vhel, vsun=vsun)
    np.testing.assert_almost_equal(vgsr.value, data['vgsr'], decimal=4)

    # now check still get right answer passing in ICRS coordinates
    vgsr = vhel_to_vgsr(c.transform_to(coord.ICRS), vhel, vsun=vsun)
    np.testing.assert_almost_equal(vgsr.value, data['vgsr'], decimal=4)
