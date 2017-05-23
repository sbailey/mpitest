#!/usr/bin/env python

"""
Testing MPI + redrock

module load python/3.5-anaconda
salloc -N 2 -p debug

#- Fails
srun -N 2 -n 2 -c 12 $SCRATCH/mpitest/mpitest.py --bcast-size 200000

#- Succeeds
srun -N 2 -n 2 -c 12 $SCRATCH/mpitest/mpitest.py --bcast-size 100000
srun -N 2 -n 2 -c 12 $SCRATCH/mpitest/mpitest.py --bcast-size 200000 --argparse

#- Fails
srun -N 2 -n 2 -c 12 $SCRATCH/mpitest/mpitest.py --bcast-size 500000 --argparse

#- Succeeds
srun -N 2 -n 2 -c 12 $SCRATCH/mpitest/mpitest.py --bcast-size 500000
"""

from __future__ import absolute_import, division, print_function

from mpi4py import MPI
comm = MPI.COMM_WORLD

import sys, os
import multiprocessing
import optparse

def blat(i, j):
    print('blat({}, {})'.format(i, j))    

#-------------------------------------------------------------------------

print('Rank {} size {} is alive'.format(comm.rank, comm.size))
sys.stdout.flush()

# parser = optparse.OptionParser(usage = "%prog [options]")
# parser.add_option("--bcast-size", type=int, default=200000, help="bcast array size [%default]")
# # parser.add_option("-o", "--output", type=str,  help="input data")
# parser.add_option("--socket", action="store_true", help="import socket module")
# opts, args = parser.parse_args()
#
# bcast_size = opts.bcast_size
#
# if opts.socket:
#     import socket

#- Importing socket, optparse, or argparse makes the problem go away
if '--socket' in sys.argv:
    import socket

if '--argparse' in sys.argv:
    print('importing argparse')
    import argparse

# if '--optparse' in sys.argv:
#     import optparse

#- Parse other arguments by hand; can't use optparse or argparse since those
#- bizarrely make the problem go away, but only for some permutations of the
#- code

#- bcast list size; 100k works, 200k doesn't
if '--bcast-size' in sys.argv:
    i = sys.argv.index('--bcast-size')
    bcast_size = int(sys.argv[i+1])
else:
    bcast_size = 200000

if '--root' in sys.argv:
    i = sys.argv.index('--root')
    root = int(sys.argv[i+1])
else:
    root = 0

data = None
if comm.rank == root:
    print('Root MPI rank is {}'.format(root))
    print('bcast array size is {}'.format(bcast_size))
    data = list(range(bcast_size))
    # data = [float(x) for x in data]
    # import numpy as np
    # data = np.arange(bcast_size)
    # print(data.__sizeof__())

if data is None:
    print('Rank {} pre-bcast data is None'.format(comm.rank))
else:
    print('Rank {} pre-bcast data size = {}'.format(comm.rank, data.__sizeof__()))

data = comm.bcast(data, root=root)
print('Rank {} post-bcast data size = {}'.format(comm.rank, data.__sizeof__()))


for i in range(bcast_size):
    assert data[i] == i

#- Start 2 processes per MPI rank
nproc = 2
proclist = list()
for j in range(nproc):
    p = multiprocessing.Process(target=blat, args=[comm.rank, j])
    p.start()
    proclist.append(p)

sys.stdout.flush()
comm.barrier()

#- Check return codes; print results in order of MPI rank
os.system('hostname')   
for i in range(comm.size):
    if i == comm.rank:
        for j in range(nproc):
            p = proclist[j]
            p.join()
            print('Rank {} proc {} pid {} exit {}'.format(comm.rank, j, p.pid, p.exitcode))
        sys.stdout.flush()
    comm.barrier()
