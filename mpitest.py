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

def blat(i, j):
    print('blat({}, {})'.format(i, j))    

#-------------------------------------------------------------------------
print('Rank {} is alive'.format(comm.rank))
sys.stdout.flush()

data = None
master = 0
if comm.rank == master:
    print('Master rank is {}'.format(master))
    #- Odd: if both of these are uncommented, it will hang
    data = list(range(200000))  #- later hangs if this is bcast
    # data = list(range(100000))  #- ok to bcast

if len(sys.argv) > 1 and sys.argv[1] == '--hang':
    #- This command doesn't hang, but it causes later commands to hang
    #- Note that data isn't used at all in subsequent code
    data = comm.bcast(data, root=master)

nproc = 4
proclist = list()
for j in range(nproc):
    p = multiprocessing.Process(target=blat, args=[comm.rank, j])
    p.start()
    proclist.append(p)

sys.stdout.flush()
comm.barrier()

#- Check return codes
for i in range(comm.size):
    if i == comm.rank:
        for j in range(nproc):
            p = proclist[j]
            p.join()
            print('Rank {} proc {} pid {} exit {}'.format(comm.rank, j, p.pid, p.exitcode))
        sys.stdout.flush()
    comm.barrier()