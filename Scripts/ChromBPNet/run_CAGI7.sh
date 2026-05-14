set -e
echo ">>>run_CAGI7.sh"
# $1 – path to model
ModName=$(basename $1)
# $2 – name of the run
# $3 – CAGI window (200 or 270)
# $4 – calculate p-values as in CBPN – YES/NO
# $5 – context – NATIVE, PLASMID, N, RANDOM
# $6 – folds, ex. 0|1|6|9
# $7 – in/out window, ex "2114-1000"
# $8 – path to peaks
echo "#=RUNNING WITH FOLLOWING PARAMETERS=#"
echo -e "${1}\n${2}\n${3}\n${4}\n${5}\n${6}\n${7}\n${8}"
echo "#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#"

log_msg() {
  current_date_time="`date "+%Y-%m-%d %H:%M:%S"`"
  echo "MESSAGE:${current_date_time}: ${1}"
}

log_msg "STARTING"
if [ "${5}" == 'PLASMID' ]; then 
  context='plasmid'
elif [ "${5}" == 'NATIVE' ]; then 
  context='native'
elif [ "${9}" == 'RANDOM' ]; then 
  context='random'
elif [ "${9}" == 'MIXED' ]; then 
  context='mixed'
else
  context='Ns'
fi
if [ "${4}" == 'YES' ]; then 
  pval_status='with_pval'
else
  pval_status='no_pval'
fi
Scorer="/home/aavas/S/variant-scorer_${3}_${context}/src/variant_scoring_${pval_status}.py"
export XLA_FLAGS="--xla_gpu_cuda_data_dir=/home/aavas/S/python/chrombpnet/cuda"

for fold in $(echo "${6}" | sed 's/|/ /g'); do
  log_msg "predicting fold ${fold}"
  
  python3.10 ${Scorer} \
    --list /home/aavas/postCAGI/Data/Variants/CBPN/CAGI7_CBPN_${3}.tsv \
    --genome /home/aavas/postCAGI/Data/ref_genomes/GRCh37.p13.genome.fa \
    --chrom_sizes /home/aavas/postCAGI/Data/ref_genomes/37.chrom.sizes \
    --model "/home/aavas/postCAGI/CBPN/Models/${ModName}/fold_${fold}/models/chrombpnet_nobias.h5" \
    --schema 'original' \
    --peak_genome /home/aavas/postCAGI/Data/ref_genomes/GRCh38.fasta \
    --peak_chrom_sizes /home/aavas/postCAGI/Data/ref_genomes/GRCh38.chrom.sizes \
    --peaks "${8}" \
    --out_prefix "/home/aavas/postCAGI/CBPN/Predictions/CBPN_CAGI7_${ModName}_${fold}_${5}_${3}_${7}_${2}"
    
  # Добавляю перенос профилей и значения MPRA
  mv "/home/aavas/postCAGI/CBPN/Predictions/CBPN_CAGI7_${ModName}_${fold}_${5}_${3}_${7}_${2}.variant_predictions.h5" "/home/aavas/postCAGI/CBPN/Predictions/profiles/CBPN_CAGI7_${ModName}_${fold}_${5}_${3}_${7}_${2}.variant_predictions.h5"
  mv "/home/aavas/postCAGI/CBPN/Predictions/CBPN_CAGI7_${ModName}_${fold}_${5}_${3}_${7}_${2}.peak_scores.tsv" "/home/aavas/postCAGI/CBPN/Predictions/peaks/CBPN_CAGI7_${ModName}_${fold}_${5}_${3}_${7}_${2}.peak_scores.tsv"
  
  python3.10 "/home/aavas/postCAGI/CBPN/Tasks/join_with_cagi.py" \
    --MPRA "/home/aavas/postCAGI/Data/MPRA_res/CAGI7_short.tsv" \
    --predictions "/home/aavas/postCAGI/CBPN/Predictions/CBPN_CAGI7_${ModName}_${fold}_${5}_${3}_${7}_${2}.variant_scores.tsv"
    rm "/home/aavas/postCAGI/CBPN/Predictions/CBPN_CAGI7_${ModName}_${fold}_${5}_${3}_${7}_${2}.variant_scores.tsv"
done

log_msg "FINISH!!!"