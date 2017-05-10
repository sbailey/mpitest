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

#- data.json was created with dc17a-test data
# import json
# from desispec.pipeline import load_prod
# grph = load_prod(nightstr='20190829', spectrographs=None)
# fx = open('data.json', 'w')
# fx.write(json.dumps(grph))
# fx.close()

grph = None
if comm.rank == 0:
    #- load data.json is in same directory as this code script
    datafile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.json')
    grph = json.load(open(datafile))
    
    #- Try trimming: works
    # key = list(grph.keys())[0]
    # grph = grph[key]

if len(sys.argv) > 1 and sys.argv[1] == '--hang':
    #- This command doesn't hang, but it causes later commands to hang
    grph = comm.bcast(grph, root=0)

def blat(i, j, qin, qout):
    print('Hello from {}-{}'.format(i, j))
    ix, jx, zz = qin.get()
    qout.put([ix, jx, np.sum(zz)])

def foo(i):
    qin = multiprocessing.Queue()
    qout = multiprocessing.Queue()
    nproc = 4
    for j in range(nproc):
        zz = np.random.uniform(0,1, size=10)
        zz = list(zz)
        qin.put( [i, j, zz] )
        p = multiprocessing.Process(target=blat, args=[i, j, qin, qout])
        p.start()

    for j in range(nproc):
        print('Getting result {}-{}'.format(i, j))
        ix, jx, sumzz = qout.get()
        print('  -->', ix, jx, sumzz)

print('Rank {} is alive'.format(comm.rank))
sys.stdout.flush()
for i in range(comm.size):
    if i == comm.rank:
        foo(comm.rank)
        sys.stdout.flush()
    comm.barrier()
    

#- The original redrock code that was hanging inside redrock
# cmd1 = "rrdesi --zbest /scratch2/scratchdirs/sjbailey/desi/dc17a/spectro/redux/dc17a-test/bricks/0001m067/zbest-0001m067.fits --output /scratch2/scratchdirs/sjbailey/desi/dc17a/spectro/redux/dc17a-test/bricks/0001m067/rr-0001m067.h5 /scratch2/scratchdirs/sjbailey/desi/dc17a/spectro/redux/dc17a-test/bricks/0001m067/brick-b-0001m067.fits /scratch2/scratchdirs/sjbailey/desi/dc17a/spectro/redux/dc17a-test/bricks/0001m067/brick-r-0001m067.fits /scratch2/scratchdirs/sjbailey/desi/dc17a/spectro/redux/dc17a-test/bricks/0001m067/brick-z-0001m067.fits --ncpu 12 --ntargets 4"
# cmd2 = "rrdesi --output /scratch2/scratchdirs/sjbailey/desi/dc17a/spectro/redux/dc17a-test/bricks/2766p445/rr-2766p445.h5 --zbest /scratch2/scratchdirs/sjbailey/desi/dc17a/spectro/redux/dc17a-test/bricks/2766p445/zbest-2766p445.fits /scratch2/scratchdirs/sjbailey/desi/dc17a/spectro/redux/dc17a-test/bricks/2766p445/brick-b-2766p445.fits /scratch2/scratchdirs/sjbailey/desi/dc17a/spectro/redux/dc17a-test/bricks/2766p445/brick-r-2766p445.fits /scratch2/scratchdirs/sjbailey/desi/dc17a/spectro/redux/dc17a-test/bricks/2766p445/brick-z-2766p445.fits --ncpu 12 --ntargets 4"
# cmds = [cmd1, cmd2]
# from redrock.external.desi import rrdesi
# rrdesi(cmds[comm.rank].split()[1:])
# print('Rank {} done'.format(comm.rank))
# sys.stdout.flush()
# comm.barrier()
