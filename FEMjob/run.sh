#! /bin/bash
b=50
for ((a=1;a<=100;a++));
do
mkdir mesh${b}_ktwo${a}
cd mesh${b}_ktwo${a}
cp ../mesh${b}.inp .
mv mesh${b}.inp mesh${b}_ktwo${a}.inp
cp ../run_abaqus_this.sh .
sed -i "s|this_kappa2|${a}.,|g" mesh${b}_ktwo${a}.inp
sed -i "s|this_job|mesh${b}_ktwo${a}|g" run_abaqus_this.sh
qsub run_abaqus_this.sh
sleep 90
cd ../
done
