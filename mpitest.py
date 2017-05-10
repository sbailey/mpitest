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

def blat(i, j, qin, qout):
    print('blat({}, {}, qin, qout)'.format(i, j))
    ix, jx = qin.get()
    qout.put([ix, jx])
    
    filename = 'blat-{}-{}.txt'.format(i, j)
    if os.path.exists(filename):
        os.remove(filename)
    fx = open(filename, 'w')
    fx.write('hello')
    fx.close()

#-------------------------------------------------------------------------
print('Rank {} is alive'.format(comm.rank))
sys.stdout.flush()

data = None
master = 1
if comm.rank == master:
    print('Master rank is {}'.format(master))
    #- Odd: if both of these are uncommented, it will hang
    data = list(range(200000))  #- later hangs if this is bcast
    # data = list(range(100000))  #- ok to bcast

if len(sys.argv) > 1 and sys.argv[1] == '--hang':
    #- This command doesn't hang, but it causes later commands to hang
    #- Note that data isn't used at all in subsequent code
    data = comm.bcast(data, root=master)

qin = multiprocessing.Queue()
qout = multiprocessing.Queue()
nproc = 4
proclist = list()
for j in range(nproc):
    qin.put( [comm.rank, j] )

    #- Works to call blat directly, but not within a spawned process
    # blat(comm.rank, j, qin, qout)
    print('Rank {} starting process {}'.format(comm.rank, j))
    p = multiprocessing.Process(target=blat, args=[comm.rank, j, qin, qout])
    p.start()
    proclist.append(p)

#- Doesn't help
for j in range(nproc):
    proclist[j].join()
    print('Rank {} finished process {}'.format(comm.rank, j))

comm.barrier()

#- Seems to hang in here, fetching from the queue
for j in range(nproc):
    ix, jx = qout.get()
    print('{} {} --> {} {}'.format(comm.rank, j, ix, jx))
