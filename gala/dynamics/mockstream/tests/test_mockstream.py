import os

# Third-party
import astropy.units as u
import numpy as np
import pytest

# Custom
from ....potential import (Hamiltonian, NFWPotential, HernquistPotential,
                           ConstantRotatingFrame)
from ....dynamics import PhaseSpacePosition, Orbit
from ....integrate import DOPRI853Integrator
from ....units import galactic

# Project
from ...nbody import DirectNBody
from ..mockstream_generator import MockStreamGenerator
from ..df import FardalStreamDF


def test_init():
    w0 = PhaseSpacePosition(pos=[15., 0., 0]*u.kpc,
                            vel=[0, 0, 0.13]*u.kpc/u.Myr)
    potential = NFWPotential.from_circular_velocity(v_c=0.2, r_s=20.,
                                                    units=galactic)
    H = Hamiltonian(potential)
    df = FardalStreamDF()

    with pytest.raises(TypeError):
        MockStreamGenerator(df="some df", hamiltonian=H)

    with pytest.raises(TypeError):
        MockStreamGenerator(df=df, hamiltonian=H, progenitor_potential="stuff")

    # Test validating the input nbody
    nbody_w0 = PhaseSpacePosition(pos=[25., 0., 0]*u.kpc,
                                  vel=[0, 0, 0.13]*u.kpc/u.Myr)
    potential2 = NFWPotential.from_circular_velocity(v_c=0.2, r_s=25.,
                                                     units=galactic)
    nbody = DirectNBody(w0=nbody_w0, external_potential=potential2,
                        particle_potentials=[None])
    gen = MockStreamGenerator(df=df, hamiltonian=H)
    with pytest.raises(ValueError):
        gen._get_nbody(w0, nbody)

    frame2 = ConstantRotatingFrame([0,0,25.]*u.km/u.s/u.kpc, galactic)
    nbody = DirectNBody(w0=nbody_w0, external_potential=potential, frame=frame2,
                        particle_potentials=[None])
    with pytest.raises(ValueError):
        gen._get_nbody(w0, nbody)

    # we expect success!
    nbody = DirectNBody(w0=nbody_w0, external_potential=potential,
                        particle_potentials=[None])
    new_nbody = gen._get_nbody(w0, nbody)


def test_run():
    potential = NFWPotential.from_circular_velocity(v_c=0.2, r_s=20.,
                                                    units=galactic)
    H = Hamiltonian(potential)
    w0 = PhaseSpacePosition(pos=[15., 0., 0]*u.kpc,
                            vel=[0, 0, 0.13]*u.kpc/u.Myr)
    mass = 2.5e4 * u.Msun
    prog_pot = HernquistPotential(mass, 4*u.pc, galactic)

    # The basic run:
    df = FardalStreamDF()
    gen = MockStreamGenerator(df=df, hamiltonian=H)
    stream1, _ = gen.run(w0, mass, dt=-1., n_steps=100)

    # Expected errors:
    with pytest.raises(TypeError):
        gen.run(w0, mass.value, dt=-1., n_steps=100)

    # With self-gravity
    gen = MockStreamGenerator(df=df, hamiltonian=H,
                              progenitor_potential=prog_pot)
    stream2, _ = gen.run(w0, mass, dt=-1., n_steps=100)
    assert not u.allclose(stream1.xyz, stream2.xyz)

    # Skipping release steps:
    gen = MockStreamGenerator(df=df, hamiltonian=H)
    stream3, _ = gen.run(w0, mass, dt=-1., n_steps=100,
                         release_every=4, n_particles=4)
    assert stream3.shape == ((100//4 + 1) * 4 * 2, )

    # Custom n_particles:
    gen = MockStreamGenerator(df=df, hamiltonian=H)
    n_particles = np.random.randint(0, 4, size=101)
    stream3, _ = gen.run(w0, mass, dt=-1., n_steps=100,
                         release_every=1, n_particles=n_particles)
    assert stream3.shape[0] == 2 * n_particles.sum()

    # TODO: add nbody test


# @pytest.mark.skipif('CI' in os.environ,
#                     reason="For some reason, doesn't work on Travis/CI")
# def test_animate(tmpdir):
#     import h5py
#
#     potential = NFWPotential.from_circular_velocity(v_c=0.2, r_s=20.,
#                                                     units=galactic)
#     H = Hamiltonian(potential)
#     w0 = PhaseSpacePosition(pos=[15., 0., 0]*u.kpc,
#                             vel=[0, 0, 0.13]*u.kpc/u.Myr)
#     mass = 2.5e4 * u.Msun
#
#     # The basic run:
#     df = FardalStreamDF(trail=False)
#     gen = MockStreamGenerator(df=df, hamiltonian=H)
#
#     filename = os.path.join(str(tmpdir), "test.hdf5")
#     stream, _ = gen.run(w0, mass, dt=-1., n_steps=3,
#                         output_every=1, output_filename=filename)
#
#     with h5py.File(filename) as f:
#         stream_orbits = Orbit.from_hdf5(f['stream'])
#         nbody_orbits = Orbit.from_hdf5(f['nbody'])
#
#     print(stream_orbits.x.shape)
#     print(stream_orbits.x)
#
#     # assert np.allclose(t, orbit.t.value)
#     #
#     # for idx in range(pos.shape[2]):
#     #     assert np.allclose(pos[:, -1, idx], stream.xyz.value[:, idx], rtol=1E-4)
#     #     assert np.allclose(vel[:, -1, idx], stream.v_xyz.value[:, idx], rtol=1E-4)
