# precalc_pval_ape.sh
# $1 input_folder background
# $2 CG background
java -cp /home/aavas/S/ape-3.0.6.jar ru.autosome.ape.PrecalculateThresholds \
  $1 \
  "${1}_APE_thr" \
  --pcm \
  --transpose \
  --background ${2}