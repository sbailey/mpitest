#!/usr/bin/env python

"""
Testing MPI + redrock

srun -N 2 -n 2 -c 24 $SCRATCH/mpitest.py
"""

from __future__ import absolute_import, division, print_function

from mpi4py import MPI
comm = MPI.COMM_WORLD

import sys, os
import numpy as np

from desispec.pipeline import load_prod

import optparse

parser = optparse.OptionParser(usage = "%prog [options]")
parser.add_option("--hang", action="store_true", help="make it hang")
opts, args = parser.parse_args()

grph = None
if comm.rank == 0:
    grph = load_prod(nightstr='20190829', spectrographs=None)
    # graph_db_check(grph)

if opts.hang:
    #- This command doesn't hang, but it causes later commands to hang
    grph = comm.bcast(grph, root=0)

#--- DEBUG ---
cmd1 = "rrdesi --zbest /scratch2/scratchdirs/sjbailey/desi/dc17a/spectro/redux/dc17a-test/bricks/0001m067/zbest-0001m067.fits --output /scratch2/scratchdirs/sjbailey/desi/dc17a/spectro/redux/dc17a-test/bricks/0001m067/rr-0001m067.h5 /scratch2/scratchdirs/sjbailey/desi/dc17a/spectro/redux/dc17a-test/bricks/0001m067/brick-b-0001m067.fits /scratch2/scratchdirs/sjbailey/desi/dc17a/spectro/redux/dc17a-test/bricks/0001m067/brick-r-0001m067.fits /scratch2/scratchdirs/sjbailey/desi/dc17a/spectro/redux/dc17a-test/bricks/0001m067/brick-z-0001m067.fits --ncpu 24 --ntargets 4"
cmd2 = "rrdesi --output /scratch2/scratchdirs/sjbailey/desi/dc17a/spectro/redux/dc17a-test/bricks/2766p445/rr-2766p445.h5 --zbest /scratch2/scratchdirs/sjbailey/desi/dc17a/spectro/redux/dc17a-test/bricks/2766p445/zbest-2766p445.fits /scratch2/scratchdirs/sjbailey/desi/dc17a/spectro/redux/dc17a-test/bricks/2766p445/brick-b-2766p445.fits /scratch2/scratchdirs/sjbailey/desi/dc17a/spectro/redux/dc17a-test/bricks/2766p445/brick-r-2766p445.fits /scratch2/scratchdirs/sjbailey/desi/dc17a/spectro/redux/dc17a-test/bricks/2766p445/brick-z-2766p445.fits --ncpu 24 --ntargets 4"
cmds = [cmd1, cmd2]
from redrock.external.desi import rrdesi
rrdesi(cmds[comm.rank].split()[1:])
print('Rank {} done'.format(comm.rank))
sys.stdout.flush()
comm.barrier()
#--- DEBUG ---

# grph = comm.bcast(grph, root=0)
