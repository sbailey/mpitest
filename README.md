# Testing MPI + python multiprocessing
Stephen Bailey, LBL, May 2017

The scripts in this repo test the combination of MPI + python multiprocessing,
with crazy results.  e.g. at the time of this first commit to github:

MPI broadcasting a list impacts whether later multiprocessing processes succeed
or fail, even if nothing uses that variable after the `comm.bcast`.

The size of the broadcasted array matters; e.g. 100k works, 200k doesn't,
but 500k does.

Importing modules like `argparse` or `socket` can change the behavior of
whether the spawned processes succeed or fail even if those modules aren't
used.

At NERSC:
```
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
```

