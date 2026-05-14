#Get predictions
set -e
echo ">>>deltaSVM_predict.sh"

log_msg() {
  current_date_time="`date "+%Y-%m-%d %H:%M:%S"`"
  echo "MESSAGE:${current_date_time}: ${1}"
}

if [ ! -f "/home/aavas/postCAGI/delta/Delta_Predictions.tsv" ]; then
  cp /home/aavas/postCAGI/Data/Variants/CAGI/CAGI7_short.tsv \
  /home/aavas/postCAGI/delta/Delta_Predictions.tsv
fi

cd /home/aavas/postCAGI/delta/ENCODE_models

for dir in [!_]*/; do
  model=${dir%/}
  log_msg "Calculating predictions with ${model}"

  perl /home/aavas/S/deltasvm_script/deltasvm.pl \
    /home/aavas/postCAGI/Data/Variants/deltaSVM/CAGI7_270_deltaSVM_revcomp_Ref.fasta \
    /home/aavas/postCAGI/Data/Variants/deltaSVM/CAGI7_270_deltaSVM_revcomp_Alt.fasta \
    "/home/aavas/postCAGI/delta/ENCODE_models/${model}/"*.tsv \
    /home/aavas/postCAGI/delta/predict.tsv
    
  echo -e "-\t${model}\t-" > "/home/aavas/postCAGI/delta/${model}.tsv"
  cat /home/aavas/postCAGI/delta/predict.tsv >> "/home/aavas/postCAGI/delta/${model}.tsv"
  rm /home/aavas/postCAGI/delta/predict.tsv
  
  paste /home/aavas/postCAGI/delta/Delta_Predictions.tsv <(cut -f2 /home/aavas/postCAGI/delta/${model}.tsv) > /home/aavas/postCAGI/delta/new.tsv
  rm /home/aavas/postCAGI/delta/Delta_Predictions.tsv
  rm /home/aavas/postCAGI/delta/${model}.tsv
  mv /home/aavas/postCAGI/delta/new.tsv /home/aavas/postCAGI/delta/Delta_Predictions.tsv
  
  mv "/home/aavas/postCAGI/delta/ENCODE_models/${model}" "/home/aavas/postCAGI/delta/ENCODE_models/_${model}"
  log_msg 'READY'
done
