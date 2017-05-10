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

def blat(i, j):
    print('blat({}, {})'.format(i, j))    

#-------------------------------------------------------------------------

print('Rank {} is alive'.format(comm.rank))
sys.stdout.flush()

#- Importing socket, optparse, or argparse makes the problem go away
if '--socket' in sys.argv:
    import socket

if '--optparse' in sys.argv:
    import optparse

if '--argparse' in sys.argv:
    import argparse
    
#- Parse other arguments by hand; can't use optparse or argparse since those
#- bizarrely make the problem go away

#- bcast list size; 100k works, 200k doesn't
if '--bcast-size' in sys.argv:
    i = sys.argv.index('--bcast-size')
    bcast_size = int(sys.argv[i+1])
else:
    bcast_size = 200000

data = None
master = 0
if comm.rank == master:
    print('Master rank is {}'.format(master))
    data = list(range(bcast_size))
    print(data.__sizeof__())

data = comm.bcast(data, root=master)

#- Start 4 processes per MPI rank
nproc = 4
proclist = list()
for j in range(nproc):
    p = multiprocessing.Process(target=blat, args=[comm.rank, j])
    p.start()
    proclist.append(p)

sys.stdout.flush()
comm.barrier()

#- Check return codes; do in order of MPI rank
for i in range(comm.size):
    if i == comm.rank:
        for j in range(nproc):
            p = proclist[j]
            p.join()
            print('Rank {} proc {} pid {} exit {}'.format(comm.rank, j, p.pid, p.exitcode))
        sys.stdout.flush()
    comm.barrier()