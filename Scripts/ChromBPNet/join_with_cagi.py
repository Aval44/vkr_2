import polars as pl
import argparse

parser= argparse.ArgumentParser()
parser.add_argument('--MPRA', type=str, required=True)
parser.add_argument('--predictions', type=str, required=True)
args= parser.parse_args()

pred= (
  pl.read_csv(args.predictions, separator='\t')
  .rename({'variant_id': 'ID'})
  .drop(['chr', 'pos', 'allele1', 'allele2', 'original_jsd', 'abs_logfc_x_jsd', 'abs_logfc_x_active_allele_quantile', 'abs_logfc_x_jsd_x_active_allele_quantile', 'abs_quantile_change', 'abs_logfc', 'quantile_change'
  ])
)
cagi= pl.read_csv(args.MPRA, separator='\t')
pred= cagi.join(pred, on='ID')

pred= (
  pred
  .rename({
    'Value': 'mpra',
    'active_allele_quantile': 'aaq',
    'logfc_x_active_allele_quantile': 'logfc_x_aaq',
    'jsd_x_active_allele_quantile': 'jsd_x_aaq',
    'logfc_x_jsd_x_active_allele_quantile': 'logfc_x_jsd_x_aaq',
  })
) 

print(pred)
pred.write_csv(args.predictions[:-19]+'_---_with_MPRA.tsv', separator='\t')