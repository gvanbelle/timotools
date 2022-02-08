
#!/bin/bash
#
# input:
#
# parallelize.batx [number of subtasks] [subtask file]
#
# Create, clean the parallel execution file
# 
touch runParallelTemp.batx
rm runParallelTemp.batx
#
# Create subtask script files
#
for ((j = 0; j< $1; j++))
do
	awk 'NR%'$1'=='$j $2 > temp$j.batx
	echo "./temp$j.batx &" >> runParallelTemp.batx
	chmod +rwx temp$j.batx
done
#
# run the multiple threads
#
chmod +rwx ./runParallelTemp.batx
./runParallelTemp.batx
#
# Clean up
#
rm runParallelTemp.batx
for ((j = 0; j< $1; j++))
do
	rm temp$j.batx
done


