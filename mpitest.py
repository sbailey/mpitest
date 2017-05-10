#!/usr/bin/env python

"""
Testing MPI + redrock

module load python/3.5-anaconda
salloc -N 2 -p debug
srun -N 2 -n 2 -c 24 $SCRATCH/mpitest/mpitest.py --hang
"""

from __future__ import absolute_import, division, print_function

from mpi4py import MPI
comm = MPI.COMM_WORLD

import sys, os
import multiprocessing
import json
import numpy as np

data = None
if comm.rank == 0:
    data = list(range(800000))

if len(sys.argv) > 1 and sys.argv[1] == '--hang':
    #- This command doesn't hang, but it causes later commands to hang
    #- Note that data isn't used at all in subsequent code
    data = comm.bcast(data, root=0)

def blat(i, j, qin, qout):
    print('Hello from {}-{}'.format(i, j))
    ix, jx, zz = qin.get()
    qout.put([ix, jx, np.sum(zz)])

#-------------------------------------------------------------------------
print('Rank {} is alive'.format(comm.rank))
sys.stdout.flush()

qin = multiprocessing.Queue()
qout = multiprocessing.Queue()
nproc = 4
for j in range(nproc):
    zz = np.random.uniform(0,1, size=10)
    zz = list(zz)
    qin.put( [comm.rank, j, zz] )

    #- Works to call blat directly, but not within a spawned process
    # blat(comm.rank, j, qin, qout)
    p = multiprocessing.Process(target=blat, args=[comm.rank, j, qin, qout])
    p.start()

for j in range(nproc):
    print('Getting result {}-{}'.format(comm.rank, j))
    ix, jx, sumzz = qout.get()
    print('  -->', ix, jx, sumzz)
    

#- The original redrock code that was hanging inside redrock
# cmd1 = "rrdesi --zbest /scratch2/scratchdirs/sjbailey/desi/dc17a/spectro/redux/dc17a-test/bricks/0001m067/zbest-0001m067.fits --output /scratch2/scratchdirs/sjbailey/desi/dc17a/spectro/redux/dc17a-test/bricks/0001m067/rr-0001m067.h5 /scratch2/scratchdirs/sjbailey/desi/dc17a/spectro/redux/dc17a-test/bricks/0001m067/brick-b-0001m067.fits /scratch2/scratchdirs/sjbailey/desi/dc17a/spectro/redux/dc17a-test/bricks/0001m067/brick-r-0001m067.fits /scratch2/scratchdirs/sjbailey/desi/dc17a/spectro/redux/dc17a-test/bricks/0001m067/brick-z-0001m067.fits --ncpu 12 --ntargets 4"
# cmd2 = "rrdesi --output /scratch2/scratchdirs/sjbailey/desi/dc17a/spectro/redux/dc17a-test/bricks/2766p445/rr-2766p445.h5 --zbest /scratch2/scratchdirs/sjbailey/desi/dc17a/spectro/redux/dc17a-test/bricks/2766p445/zbest-2766p445.fits /scratch2/scratchdirs/sjbailey/desi/dc17a/spectro/redux/dc17a-test/bricks/2766p445/brick-b-2766p445.fits /scratch2/scratchdirs/sjbailey/desi/dc17a/spectro/redux/dc17a-test/bricks/2766p445/brick-r-2766p445.fits /scratch2/scratchdirs/sjbailey/desi/dc17a/spectro/redux/dc17a-test/bricks/2766p445/brick-z-2766p445.fits --ncpu 12 --ntargets 4"
# cmds = [cmd1, cmd2]
# from redrock.external.desi import rrdesi
# rrdesi(cmds[comm.rank].split()[1:])
# print('Rank {} done'.format(comm.rank))
# sys.stdout.flush()
# comm.barrier()
