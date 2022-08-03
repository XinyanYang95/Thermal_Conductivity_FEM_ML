#! /bin/bash
#PBS -j oe
#PBS -N proj
#PBS -l walltime=1:00:00
#PBS -l nodes=1:ppn=1

cd $PBS_O_WORKDIR

export LD_LIBRARY_PATH=/opt/mpi/openmpi-1.6.5/lib:$LD_LIBRARY_PATH
export PATH=/opt/intel/bin:/opt/mpi/openmpi-1.6.5/bin:/opt/abaqus/Commands:$PATH

cat $PBS_NODEFILE | sort | awk 'x[$0]++ < 8 { print $0 }' > nodefile
NP=`cat nodefile | wc -l`

abq6132 double job=this_job.inp cpus=$NP interactive > this_job.log

rm nodefile
