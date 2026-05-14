# run_APE.sh
#$1 Motif folder
#$2 p-value_cutoff
#$3 input_folder
#$4 output_folder
#$5 number_of_jobs
#$6 Task_name
#$7 background
function ape {
  java -cp /home/aavas/S/ape-3.0.6.jar ru.autosome.perfectosape.SNPScan \
    ${1} \
    ${3} \
    --pcm \
    --transpose \
    --compact \
    --pvalue-cutoff ${2} \
    --fold-change-cutoff 1 \
    --background ${6} \
    --precalc "${1}_APE_thr" > "${4}/${5}_$(basename ${3}).tsv"
}
export -f ape

parallel  --jobs ${5} ape  ${1} ${2} {} ${4} ${6} ::: ${3}/*

echo -e 'ID\tPWM_Name\tpval_REF\tpval_ALT\tbest_pos_REF\tstrand_REF\tbest_pos_ALT\tstrand_ALT' > "${4}/${6}.tsv"
for split in ${4}/${6}_*; do
  tail -n +2 ${split} >> "${4}/${6}.tsv"
  rm ${split}
done
echo 'DONE'