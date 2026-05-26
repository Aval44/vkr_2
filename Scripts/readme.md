Файл helper_scripts.py содержит код для визуализации результатов (в виде функций), оценки качества предсказаний, построения ансамбля APE и мета-модели.  
__Визуализация__
+ Столбчатые диаграммы
  + ridge_2_barplot
  + compare_2_barplots
  + do_simple_bar
+ Гистограммы
  + compare_distributions
  + do_count_hist
+ Линейная диаграмма – do_lineplots
+ Диаграмма рассеяния – do_scatter
+ Тепловая карта
  + do_heat_triangle
  + do_clustermap
+ Визуализация результатов кросс-валидации – do_jitterplot
----------
__Расчёт метрик качества для предсказаний моделей__
+ calc_metrics
+ compare_models_by_pwm_pearson
+ compare_models_by_pwm_zscore  
----------
__Мета-модель__
+ make_ensemble
----------
__APE__
+ make_ape
