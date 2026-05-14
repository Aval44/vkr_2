# updated on march 29th, added in/out windows
# updated on march 30th, added concatenation with cagi values and AAQ calculation
# updated on april 1st, added random context
# updated on april 3rd, added mixed context
set -e
export CUDA_VISIBLE_DEVICES=0
echo ">>>train_and_run_CAGI7.sh"
# $1 – path to experiment data directory, 
#      ex. /home/aavas/postCAGI/CBPN/Training_Data/ENCSR042AWH_ATAC
ExpName=$(basename $1)
# $2 – path to bias model or NEW
# $3 – ATAC or DNASE
# $4 – name of the run
# $5 – IN window
# $6 – OUT window
# $7 – CAGI window (200 or 270)
# $8 – calculate p-values as in CBPN – YES/NO
# $9 – context – NATIVE, PLASMID, N, RANDOM
# $10 – folds, ex. 0|1|6|9
# $11 – model description, may leave blank ("")
# $12 – path to background regions file or DEFAULT
echo "#=RUNNING WITH FOLLOWING PARAMETERS=#"
echo -e "${1}\n${2}\n${3}\n${4}\n${5}\n${6}\n${7}\n${8}\n${9}\n${10}\n${11}\n${12}"
echo "#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#"

log_msg() {
  current_date_time="`date "+%Y-%m-%d %H:%M:%S"`"
  echo "MESSAGE:${current_date_time}: ${1}"
}

log_msg "STARTING"
cd "$1"
#=========
if [ -f "merged_sorted.bam" ]; then
  log_msg "Alignments are already merged. Skipping."
else
  #ADD single reads OUT!!!
  log_msg "merging and sorting alignments"
  samtools merge -o merged_unsorted.bam alignment*
  samtools sort -@10 -o merged_sorted.bam merged_unsorted.bam
  samtools index merged_sorted.bam
  rm merged_unsorted.bam
fi
#=========
if [ -f "peaks.bed" ]; then
  log_msg "Peaks are already called. Skipping."
else # needed for ENCODE DNASE
  log_msg "Peak calling heaviest alignment with MACS2"
  # $(ls -1 -S alignment*| head -n 1) is actually worse ?
  # expect filtered  pair_end reads
  macs2 callpeak \
      -t merged_sorted.bam \
      -p 0.01 \
      --shift -85 \
      --extsize 150 \
      --nomodel \
      --keep-dup all \
      --call-summits
  mv NA_peaks.narrowPeak peaks.bed
  rm NA_*
fi
#=========
if [ -f "peaks_no_blacklist.bed" ]; then
  log_msg "Peaks are already filtered. Skipping."
else
  log_msg "Filtering peaks"
  bedtools intersect -v -a peaks.bed -b /home/aavas/postCAGI/Data/exclusion_list_extended.bed > peaks_no_blacklist.bed
fi
#=========
if [ ! -f "cbpn_background_negatives.bed" ] && [ ! -f "${12}" ]; then
  log_msg "Generating background regions with chrombpnet"
  chrombpnet prep nonpeaks \
    -g /home/aavas/postCAGI/Data/ref_genomes/GRCh38.fasta \
    -p peaks_no_blacklist.bed \
    -c /home/aavas/postCAGI/Data/ref_genomes/GRCh38.chrom.sizes \
    -fl /home/aavas/postCAGI/Data/folds/fold_0.json \
    -o cbpn_background
  Backgrounds="/home/aavas/postCAGI/CBPN/Training_Data/${ExpName}/cbpn_background_negatives.bed"
elif [ -f "cbpn_background_negatives.bed" ] && [ ! -f "${12}" ]; then
  log_msg "Using existing background"
  Backgrounds="/home/aavas/postCAGI/CBPN/Training_Data/${ExpName}/cbpn_background_negatives.bed"
else
  log_msg "Using provided backgrounds"
  Backgrounds=${12}
fi
#=========
BiasPath="$2"
export XLA_FLAGS="--xla_gpu_cuda_data_dir=/home/aavas/S/python/chrombpnet/cuda"
if [ "$2" == "NEW" ]; then
  log_msg "bias model training"

  chrombpnet bias pipeline \
    -ibam merged_sorted.bam \
    -d ${3} \
    -g /home/aavas/postCAGI/Data/ref_genomes/GRCh38.fasta \
    -c /home/aavas/postCAGI/Data/ref_genomes/GRCh38.chrom.sizes \
    -p peaks_no_blacklist.bed \
    -n ${Backgrounds} \
    -b 0.8 `#0.8 Recommended_for_dnase-seq ИСПРАВИТЬ!!!` \
    -fl /home/aavas/postCAGI/Data/folds/fold_0.json \
    -il ${5} \
    -ol ${6} \
    -o "/home/aavas/postCAGI/CBPN/bias_models/${ExpName}_---_${11}_bias_model"
  BiasPath="/home/aavas/postCAGI/CBPN/bias_models/${ExpName}_---_${11}_bias_model/models/bias.h5"
fi
#=========
log_msg "main model training start"
mkdir -p "/home/aavas/postCAGI/CBPN/Models/${ExpName}_---_${11}"

for fold in $(echo "${10}" | sed 's/|/ /g'); do
  log_msg "main model fold ${fold} training"

  mkdir "/home/aavas/postCAGI/CBPN/Models/${ExpName}_---_${11}/fold_${fold}"
# !!! change batchsize
  chrombpnet pipeline \
    -ibam merged_sorted.bam \
    -d ${3} \
    -g /home/aavas/postCAGI/Data/ref_genomes/GRCh38.fasta \
    -c /home/aavas/postCAGI/Data/ref_genomes/GRCh38.chrom.sizes \
    -p peaks_no_blacklist.bed \
    -n "${Backgrounds}" \
    -fl "/home/aavas/postCAGI/Data/folds/fold_${fold}.json" \
    -bs 64 \
    -il ${5} \
    -ol ${6} \
    -b  "${BiasPath}" \
    -o "/home/aavas/postCAGI/CBPN/Models/${ExpName}_---_${11}/fold_${fold}"
done
#=========
log_msg "cbpnet prediction start"
if [ "${9}" == 'PLASMID' ]; then 
  context='plasmid'
elif [ "${9}" == 'NATIVE' ]; then 
  context='native'
elif [ "${9}" == 'RANDOM' ]; then 
  context='random'
elif [ "${9}" == 'MIXED' ]; then 
  context='mixed'
else
  context='Ns'
fi
if [ "${8}" == 'YES' ]; then 
  pval_status='with_pval'
else
  pval_status='no_pval'
fi
Scorer="/home/aavas/S/variant-scorer_${7}_${context}/src/variant_scoring_${pval_status}.py"

for fold in $(echo "${10}" | sed 's/|/ /g'); do
  log_msg "predicting fold ${fold}"
  
  python3.10 ${Scorer} \
    --list /home/aavas/postCAGI/Data/Variants/CBPN/CAGI7_CBPN_${7}.tsv \
    --genome /home/aavas/postCAGI/Data/ref_genomes/GRCh37.p13.genome.fa \
    --chrom_sizes /home/aavas/postCAGI/Data/ref_genomes/37.chrom.sizes \
    --model "/home/aavas/postCAGI/CBPN/Models/${ExpName}_---_${11}/fold_${fold}/models/chrombpnet_nobias.h5" \
    --schema 'original' \
    --peak_genome /home/aavas/postCAGI/Data/ref_genomes/GRCh38.fasta \
    --peak_chrom_sizes /home/aavas/postCAGI/Data/ref_genomes/GRCh38.chrom.sizes \
    --peaks peaks_no_blacklist.bed \
    --out_prefix "/home/aavas/postCAGI/CBPN/Predictions/CBPN_CAGI7_${ExpName}_---_${11}_${fold}_${9}_${7}_${5}-${6}_${4}"
    
  # Добавляю перенос профилей и значения MPRA
  mv "/home/aavas/postCAGI/CBPN/Predictions/CBPN_CAGI7_${ExpName}_---_${11}_${fold}_${9}_${7}_${5}-${6}_${4}.variant_predictions.h5" "/home/aavas/postCAGI/CBPN/Predictions/profiles/CBPN_CAGI7_${ExpName}_---_${11}_${fold}_${9}_${7}_${5}-${6}_${4}.variant_predictions.h5"
  mv "/home/aavas/postCAGI/CBPN/Predictions/CBPN_CAGI7_${ExpName}_---_${11}_${fold}_${9}_${7}_${5}-${6}_${4}.peak_scores.tsv" "/home/aavas/postCAGI/CBPN/Predictions/peaks/CBPN_CAGI7_${ExpName}_---_${11}_${fold}_${9}_${7}_${5}-${6}_${4}.peak_scores.tsv"
  
  python3.10 "/home/aavas/postCAGI/CBPN/Tasks/join_with_cagi.py" \
    --MPRA "/home/aavas/postCAGI/Data/MPRA_res/CAGI7_short.tsv" \
    --predictions "/home/aavas/postCAGI/CBPN/Predictions/CBPN_CAGI7_${ExpName}_---_${11}_${fold}_${9}_${7}_${5}-${6}_${4}.variant_scores.tsv"
    rm "/home/aavas/postCAGI/CBPN/Predictions/CBPN_CAGI7_${ExpName}_---_${11}_${fold}_${9}_${7}_${5}-${6}_${4}.variant_scores.tsv"
done

log_msg "FINISH!!!"