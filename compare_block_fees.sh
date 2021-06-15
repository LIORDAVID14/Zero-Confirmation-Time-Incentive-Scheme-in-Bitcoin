#!/bin/bash


#ls -d /media/hdd/itay/mempoolAnalysis/*/*fees.log


Output="block_fees_comparison.csv"
echo -n > $Output

start_block=$1
end_block=$2



for ((i=$start_block; i<=$end_block; i++)); do
  
  if [ `ls -d /media/hdd/itay/blockFees/*/*${i}*.log | wc -l` -ge 3 ]; then
    alg_fees=`cat /media/hdd/itay/blockFees/*/*${i}*_speculative_fees.log | cut -f1 -d" "`
    actual_fees=`cat /media/hdd/itay/blockFees/*/*${i}*_fees_reward.log | cut -f1 -d" "`
    echo "$i,$alg_fees,$actual_fees" >> $Output
  fi
   
   
done

exit


