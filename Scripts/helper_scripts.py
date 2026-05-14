#==============================
#PLOTTING                     =
#==============================

def save_picture(p, title, save_pic, dpi):
    if save_pic:
        if isinstance(save_pic, str):
            p.save(f'/Users/hello/Desktop/Диплом/Тексты/Картинки/{save_pic}.png', dpi=dpi)
        elif (title != ''):
            p.save(f'/Users/hello/Desktop/Диплом/Тексты/Картинки/{title}.png', dpi=dpi)
        else:
            import random
            title= str(random.randint(1, 100000000000000))
            p.save(f'/Users/hello/Desktop/Диплом/Тексты/Картинки/{title}.png', dpi=dpi)

    return()


#===BARPLOTS===#

def ridge_2_barplot(
    df1, df2,
    x_axis='', y_axis='', title='',

    groups=('Conf > 0.05', 'All'),
    dpi=800,
    width=None, height=5,
    title_size=16,
    gradient_style='red-blue', #orange-green, #lilac-teal
    rotate_x_ticks=0, x_ticks_size=8,
    save_pic=False
):
    '''
    To compare different models
    Expects two dfs with, for example, correlation for all and for sign. 
        two cols in each: name and value
    Color guide:
    + significance All – "red-blue";
    + ROCAUC pos_neu vs neg_neu All – "lilac-teal";
    + promoter-enhancer – "orange-green".

    save_pic –  True, False or name.
                if True then title, if no title then random number
    '''
    #1️⃣ Packages Import
    import polars as pl
    from plotnine import (ggplot, aes, geom_col, geom_hline, geom_text, scale_color_manual,
        scale_fill_gradient, theme_minimal, element_text, geom_label, geom_point, guides, element_blank,
        labs, theme, element_line, element_rect, position_dodge, scale_fill_identity, guide_legend
    )

    #2️⃣ Comb data
    df1= (
        df1
        .with_columns(pl.lit(groups[0]).alias('group'))
        .rename({df1.columns[0]: 'name', df1.columns[1]: 'value'})
    )
    df2= (
        df2
        .with_columns(pl.lit(groups[1]).alias('group'))
        .rename({df2.columns[0]: 'name', df2.columns[1]: 'value'})
    )
    df= pl.concat([df1, df2])
    max_abs_value= df['value'].abs().max()
    df= df.with_columns(
        pl.when(pl.col('value') >= 0)
          .then(pl.col('value') + 0.025 * max_abs_value)
          .otherwise(pl.col('value') - 0.025 * max_abs_value)
          .alias('y')
    )

    #3️⃣ Gradient (with Gemini flash)
    max_abs_values=[df.filter(pl.col('group') == x)['value'].abs().max() for x in groups]
    if (gradient_style == 'red-blue'):
        def get_color(val, group): 
            if (group == groups[0]):
                norm= abs(val) / max_abs_values[0]
                return f"#{int(166-(166-31)*norm):02x}{int(206-(206-120)*norm):02x}{int(227-(227-180)*norm):02x}"
            else:
                norm= abs(val) / max_abs_values[1]
                return f"#{int(249-(249-235)*norm):02x}{int(152-(152-67)*norm):02x}{int(153-(153-69)*norm):02x}"
        g0_color= '#2078B4'
        g1_color= '#EB4345'
        
    if (gradient_style == 'orange-green'):      
        def get_color(val, group): 
            if (group == groups[0]):
                # Оранжевая: от #FFE5B4 (светлый) до #FF8C00 (насыщенный)
                norm= abs(val) / max_abs_values[0]
                return f"#{int(255-(255-255)*norm):02x}{int(229-(229-140)*norm):02x}{int(180-(180-0)*norm):02x}"
            else:
                # Зеленая: от #E0FFE0 (светлый) до #2E8B57 (насыщенный)
                norm= abs(val) / max_abs_values[1]
                return f"#{int(163-(163-46)*norm):02x}{int(198-(198-139)*norm):02x}{int(149-(149-87)*norm):02x}"
        g0_color= '#FF8C00'
        g1_color= '#2E8B57'

    if (gradient_style == 'lilac-teal'):      
        def get_color(val, group): 
            if (group == groups[0]):
                # Лилово-голубой: от #D9E4F0 до #335882 (насыщенный)
                norm= abs(val) / max_abs_values[0]
                return f"#{int(217-(217-51)*norm):02x}{int(228-(228-88)*norm):02x}{int(240-(240-130)*norm):02x}"
            else:
                # Бирюзовый (Teal): от #E0FFFF до #00A3A3 (насыщенный)
                norm= abs(val) / max_abs_values[1]
                return f"#{int(224-(224-0)*norm):02x}{int(255-(255-163)*norm):02x}{int(255-(255-163)*norm):02x}"
        g0_color= '#335882'
        g1_color= '#00A3A3'

    df= df.with_columns(
        pl.struct(['value', 'group']).map_elements(lambda x: get_color(x['value'], x['group']),
        return_dtype=pl.String).alias('color_hex')
    )

    #4️⃣ Plot
    if (width == None):
        n_cat= df.n_unique(subset=['name'])
        width= 3.5+6/5*n_cat
        
    p= (
        ggplot(df, 
               aes(
                   x='reorder(name, value, max, ascending=False)', 
                   y='value', 
                   fill='color_hex', 
                   group='group'
               )
        )
        + geom_col(position=position_dodge(width=0.8), width=1, color='black')
        + geom_text(
            mapping=aes(x='name', y='y', label='value', group='group'),
            va='center', 
            size=height+1,
            position=position_dodge(width=1),
            family='Futura', #Avenir Futura Geneva
            format_string='{:.3f}'
        )
        + geom_point( # для легенды
            mapping=aes(x='name', y='value', color='group'), 
            alpha=0,
        )
        + scale_color_manual(values={groups[0]: g0_color, groups[1]: g1_color})
        + guides(
            color=guide_legend(override_aes={'size': 4+ height/5*2, 'alpha': 1, 'shape': 's'}),
            fill=guide_legend(override_aes={'color': '#E5FEFF'})
        )
        + geom_hline(yintercept=0, size=1)
        + theme_minimal()
        + labs(
            x=x_axis, 
            y=y_axis,
            title=title
        )
        + theme(
            figure_size=(width, height),
            dpi=dpi,
            plot_margin=0.03,
            
            plot_title=element_text(vjust=0.4, size=title_size),
            legend_title=element_blank(),
            legend_box_margin=0,
            legend_text= element_text(size=11+height/5*3, family="Arial", weight='heavy'),
            axis_line_x=element_line(size=0.8),
            axis_text_x=element_text(rotation=rotate_x_ticks, size=x_ticks_size),
            axis_title_x=element_text(vjust=0.9),
            axis_text_y=element_text(family="Arial", weight='light'),
            
            plot_background=element_rect(fill="#E5FEFF"),
            panel_background=element_rect(fill="#D9F4FA"), # #B4E9F5 #00FFFF #D9F4FA #E5FAFF  E6FCFC CCFBFF E5FDFF
            panel_border=element_rect(size=0.3),
            
            text=element_text(family="Proxima Nova", weight='heavy'),
            axis_text=element_text(family="Geneva"),
            panel_grid_major=element_line(color='black', size=0.2),
            panel_grid_minor=element_line(color='grey', size=0.1),
        )
        + scale_fill_identity()
    )
    save_picture(p, title, save_pic, dpi)
             
    return(p)



def compare_2_barplots(
    df,
    bins, predict_1, predict_2, 

    y_cutoff=0,
    color_main='#ADADAD', color_1='#F94B51', color_2='#38F2BC',
    x_axis='', y_axis='', title='',
    bin_width=10,
    dpi=800,
    width=None, height=5,
    title_size=16,
    save_pic=False
):
    '''
    Compare metrics in (for example) from_start bins
    df – polars dataFrame, has value, predict_1, predict_2 values
    bins, predict_1, predict_2 – column names

    y_cutoff – cut y axis by min_value*y_cutoff
    color_1, color_2 – color of models, color_main – intersect
    bin_width – IMPORTAINT, adjust to the scale of data
    '''
    #1️⃣ Packages Import
    import polars as pl
    from plotnine import (
        ggplot, aes, geom_col, labs, scale_fill_manual,
        theme, element_text, theme_minimal, element_blank, element_line,
        element_rect, coord_cartesian, scale_y_continuous
    )

    #2️⃣ Add min column to dataframe etc.
    df= (
        df
        .with_columns(pl.min_horizontal(predict_1, predict_2).alias('MAIN'))
        #.with_columns(pl.col(bins).cast(pl.String))
    )

    min_value= df['MAIN'].min()
    max_value= df.with_columns(pl.min_horizontal(predict_1, predict_2).alias('МАХ'))['МАХ'].max()

    if not width:
        width= df['MAIN'].len()/4



    #3️⃣ Plot
    p= (
        ggplot(data=df, mapping=aes(x=bins))
        + geom_col(
            mapping=aes(y=predict_1, fill=f'"{predict_1}"'),
            color='#2F4F4F',
            width=bin_width,
        )
        + geom_col(
            mapping=aes(y=predict_2, fill=f'"{predict_2}"'),
            color='#2F4F4F',
            width=bin_width,
        )
        + geom_col(
            mapping=aes(y='MAIN'),
            color='#2F4F4F',
            fill=color_main,
            width=bin_width,
        )
        + scale_fill_manual(values={
            predict_1: color_1,
            predict_2: color_2,
        })
        + scale_y_continuous(expand=(0, 0))           
        + coord_cartesian(ylim=(min_value * y_cutoff, max_value * 1.2))
        + theme_minimal()
        + labs(
            x=x_axis, 
            y=y_axis,
            title=title,
        )
        + theme(
            figure_size=(width, height),
            dpi=dpi,
            plot_margin=0.03,
            
            plot_title=element_text(vjust=0.4, size=title_size),
            
            legend_title=element_blank(),
            legend_text= element_text(size=9, family="Arial", weight='heavy'),
            legend_position=(0.95, 0.95),
            
            axis_line_x=element_line(size=1.4),
            axis_text_x=element_text(rotation=0, family="Arial", weight='light', hjust=1.5),
            axis_title_x=element_text(vjust=0.9),
            axis_text_y=element_text(family="Arial", weight='light'),
            
            plot_background=element_rect(fill="#E5FEFF"),
            panel_background=element_rect(fill="#D9F4FA"), # #B4E9F5 #00FFFF #D9F4FA #E5FAFF  E6FCFC CCFBFF E5FDFF
            panel_border=element_rect(size=0.3),
            
            text=element_text(family="Proxima Nova", weight='heavy'),
            axis_text=element_text(family="Geneva"),
            panel_grid_major_x=element_blank(),
            panel_grid_minor_x=element_blank(),
            panel_grid_major_y=element_line(color='black', size=0.2),
            panel_grid_minor_y=element_line(color='grey', size=0.1),
        )
    )
    save_picture(p, title, save_pic, dpi)
             
    return(p)



def do_simple_bar(
    df,
    value_col, name_col,
    x_axis=False, 

    color='#E0D78A',
    breaks=None,
    title='',
    dpi=800,
    bin_width=1,
    width=10, height=5,
    title_size=16,
    save_pic=False
):
    '''
    PLACEHOLDER
    '''
    #1️⃣ Packages Import
    import polars as pl
    from plotnine import (
        ggplot, aes, geom_col, labs, scale_fill_manual,
        theme, element_text, theme_minimal, element_blank, element_line,
        element_rect, scale_y_continuous, scale_x_discrete
    )
    if not x_axis: x_axis= name_col
    if not breaks: breaks= df[name_col].to_list()

    #2️⃣ Customze width


    #3️⃣ Plot
    p= (
        ggplot(df, aes(x=name_col, y=value_col))    
        + geom_col(
            color='navy',
            fill=color,
            size=0.42,
            width=bin_width,
        )
        + scale_y_continuous(expand=(0, 0, 0.12, 0))
        + scale_x_discrete(limits=df[name_col].to_list(), breaks=breaks)
        + theme_minimal()
        + labs(
            x=x_axis, 
            title=title,
        )
        + theme(
            figure_size=(width, height),
            dpi=dpi,
            plot_margin=0.03,
            
            plot_title=element_text(vjust=0.4, size=title_size),
            
            axis_line_x=element_line(size=1.4),
            axis_text_x=element_text(rotation=0, family="Arial", weight='light', size=7),
            axis_title_x=element_text(vjust=0.9),
            axis_text_y=element_text(family="Arial", weight='light'),
            
            plot_background=element_rect(fill="#E5FEFF"),
            panel_background=element_rect(fill="#D9F4FA"), # #B4E9F5 #00FFFF #D9F4FA #E5FAFF  E6FCFC CCFBFF E5FDFF
            panel_border=element_rect(size=0.3),
            
            text=element_text(family="Proxima Nova", weight='heavy'),
            axis_text=element_text(family="Geneva"),
            panel_grid_major_x=element_blank(),
            panel_grid_minor_x=element_blank(),
            panel_grid_major_y=element_line(color='black', size=0.2),
            panel_grid_minor_y=element_line(color='grey', size=0.1),
        )
    )
    save_picture(p, title, save_pic, dpi)
             
    return(p)



#===HISTPLOTS===#

def compare_distributions(
    df,
    value_col, group_col,

    dpi=800,
    width=None, height=5, nbins=None,
    title='', x_axis='',
    title_size=16,
    color_style='red-blue', 
    test='KS', #what else?
    save_pic=False
):
    '''
    To compare two models (density plot with overlay)
    Expects df in long format with
    value_col
    group_col

    nbins
    color_style – one of  salad-green, yellow-gold or red-blue
    save_pic –  True, False or name.
                if True then title, if no title then random number
    '''
    #1️⃣ Packages Import
    import numpy as np
    import polars as pl
    from scipy.stats import ks_2samp
    from plotnine import (
        ggplot, aes, geom_histogram, geom_density, labs, scale_fill_manual,
        theme, element_text, theme_minimal, element_blank, element_line,
        element_rect, scale_y_continuous
    )

    #2️⃣ Customze bins, width and colors
    if (color_style == 'red-blue'):
        colors= ['#A63D28', '#2891A6'] # #A63D28 or crismon
    elif (color_style == 'yellow-gold'):
        colors= ['yellow', 'goldenrod']
    else: colors= ['khaki', 'seagreen']
        
    if ((nbins != None) & (width == None)):
        width= nbins * 7 / 50
    elif ((width != None) & (nbins == None)):
        nbins= width * 50 / 7
    elif ((width == None) & (nbins == None)):
        nbins= 50
        width= 7

    #3️⃣ Divergence
    groups= df[group_col].unique()
    if (test == 'KS'):
        _, pval = ks_2samp(df.filter(pl.col(group_col) == groups[0])[value_col], df.filter(pl.col(group_col) == groups[1])[value_col])
        test_result= f'KS pval: {pval:.3e}\n'


    #4️⃣ Plot
    p= (
        ggplot(df, 
               aes(
                   x=value_col, 
                   fill=group_col, 
               )
        )    
        + geom_histogram(
            aes(y='..density..'), 
            bins=nbins, 
            position='identity', 
            alpha=0.5, 
            color='navy', 
            size=0.42
        )
        #+ geom_density(alpha=0)
        + scale_fill_manual(values=colors)
        + scale_y_continuous(expand=(0, 0, 0, 0.1))
        + theme_minimal()
        + labs(
            x=x_axis, 
            title=title,
            fill=test_result
        )
        + theme(
            figure_size=(width, height),
            dpi=dpi,
            plot_margin=0.03,
            
            plot_title=element_text(vjust=0.4, size=title_size),
            
            legend_title=element_text(size=10, family="Arial", weight='light'),
            legend_text= element_text(size=9, family="Arial", weight='heavy'),
            legend_position=(0.95, 0.95),
            
            axis_line_x=element_line(size=1.4),
            axis_text_x=element_text(rotation=0, family="Arial", weight='light'),
            axis_title_x=element_text(vjust=0.9),
            axis_text_y=element_text(family="Arial", weight='light'),
            
            plot_background=element_rect(fill="#E5FEFF"),
            panel_background=element_rect(fill="#D9F4FA"), # #B4E9F5 #00FFFF #D9F4FA #E5FAFF  E6FCFC CCFBFF E5FDFF
            panel_border=element_rect(size=0.3),
            
            text=element_text(family="Proxima Nova", weight='heavy'),
            axis_text=element_text(family="Geneva"),
            panel_grid_major=element_blank(),
            panel_grid_minor=element_blank(),
            panel_grid_major_y=element_line(color='black', size=0.2),
            panel_grid_minor_y=element_line(color='grey', size=0.1),
        )
    )
    save_picture(p, title, save_pic, dpi)
             
    return(p)



def do_count_hist(
    df,
    value_col,
    x_axis, 

    nbins=None,
    color='#E0D78A',
    title='',
    dpi=800,
    width=None, height=5,
    title_size=16,
    save_pic=False
):
    '''
    PLACEHOLDER
    '''
    #1️⃣ Packages Import
    import numpy as np
    import polars as pl
    from scipy.stats import ks_2samp
    from plotnine import (
        ggplot, aes, geom_histogram, labs, scale_fill_manual,
        theme, element_text, theme_minimal, element_blank, element_line,
        element_rect, scale_y_continuous, after_stat
    )

    #2️⃣ Customze width
        
    if ((nbins != None) & (width == None)):
        width= nbins * 7 / 50
    elif ((width != None) & (nbins == None)):
        nbins= width * 50 / 7
    elif ((width == None) & (nbins == None)):
        nbins= 50
        width= 7


    #3️⃣ Plot
    p= (
        ggplot(df, aes(x=value_col))    
        + geom_histogram(
            mapping=aes(y='..count..'),
            bins=nbins, 
            position='identity',
            color='navy',
            fill=color,
            size=0.42
        )
        + scale_y_continuous(expand=(0, 0, 0.12, 0))
        + theme_minimal()
        + labs(
            x=x_axis, 
            title=title,
        )
        + theme(
            figure_size=(width, height),
            dpi=dpi,
            plot_margin=0.03,
            
            plot_title=element_text(vjust=0.4, size=title_size),
            
            axis_line_x=element_line(size=1.4),
            axis_text_x=element_text(rotation=0, family="Arial", weight='light'),#, hjust=1),
            axis_title_x=element_text(vjust=0.9),
            axis_text_y=element_text(family="Arial", weight='light'),
            
            plot_background=element_rect(fill="#E5FEFF"),
            panel_background=element_rect(fill="#D9F4FA"), # #B4E9F5 #00FFFF #D9F4FA #E5FAFF  E6FCFC CCFBFF E5FDFF
            panel_border=element_rect(size=0.3),
            
            text=element_text(family="Proxima Nova", weight='heavy'),
            axis_text=element_text(family="Geneva"),
            panel_grid_major_x=element_blank(),
            panel_grid_minor_x=element_blank(),
            panel_grid_major_y=element_line(color='black', size=0.2),
            panel_grid_minor_y=element_line(color='grey', size=0.1),
        )
    )
    save_picture(p, title, save_pic, dpi)
             
    return(p)



#===LINEPLOTS===#

def do_lineplots(
    df,
    x_col, y_cols, 
    x_axis='', y_axis='',
    title='',
    breaks=[],

    color_list=['#84578E', '#8E6857', '#618E57', '#577D8E', 'black'],
    linetype_list=['solid', 'dashed', 'dashdot', 'dotted', 'solid'],
    y_cutoff=0,
    dpi=800,
    width=None, height=5,
    title_size=16,
    save_pic=False

):
    '''
    df in wide form, x_col,
    y_cols – string or list of strings

    breaks=[] – list of x axis ticks to show
    color_list – default has length 5, if more – repeated
    linetype_list – default has length 4, if more – repeated
    y_cutoff=0 – y axis cutoff: min_value * y_cutoff
    '''
    import polars as pl
    from plotnine import (
        ggplot, aes, geom_line, labs, scale_color_manual, scale_linetype_manual,
        theme, element_text, theme_minimal, element_blank, element_line,
        element_rect, coord_cartesian, scale_y_continuous, scale_x_continuous
    )

    if isinstance(y_cols, str): y_cols= [y_cols]
    min_value= df.with_columns(pl.min_horizontal(y_cols).alias('MIN'))['MIN'].min()
    max_value= df.with_columns(pl.max_horizontal(y_cols).alias('МАХ'))['МАХ'].max()

    if not width:
        width= df[x_col].len()/8
    color_list= color_list[:len(y_cols)]
    linetypes = linetype_list[:len(y_cols)]

    p= (ggplot(data=df, mapping=aes(x=x_col)))
    for i in range(len(y_cols)):
        p += geom_line(
            mapping=aes(y=y_cols[i], 
                color=f'"{y_cols[i]}"',
                linetype=f'"{y_cols[i]}"'
            ),
            size=0.8,
        )
    p= (
        p
        + scale_color_manual(values=dict(zip(y_cols, color_list)))
        + scale_linetype_manual(values=dict(zip(y_cols, linetypes)))
        + scale_y_continuous(expand=(0, 0))
        + scale_x_continuous(breaks=breaks)  #ADD logic!           
        + coord_cartesian(ylim=(min_value * y_cutoff, max_value * 1.05))
        + theme_minimal()
        + labs(
            x=x_axis, 
            y=y_axis,
            title=title,
        )
        + theme(
            figure_size=(width, height),
            dpi=dpi,
            plot_margin=0.03,
            
            plot_title=element_text(vjust=0.4, size=title_size),
            
            legend_title=element_blank(),
            legend_text= element_text(size=9, family="Arial", weight='heavy'),
            #legend_position=(0.95, 0.95),
            legend_position='right',
            
            axis_line_x=element_line(size=1.4),
            axis_text_x=element_text(rotation=0, family="Arial", weight='light', hjust=1.5),
            axis_title_x=element_text(vjust=0.9),
            axis_text_y=element_text(family="Arial", weight='light'),
            
            plot_background=element_rect(fill="#E5FEFF"),
            panel_background=element_rect(fill="#D9F4FA"), # #B4E9F5 #00FFFF #D9F4FA #E5FAFF  E6FCFC CCFBFF E5FDFF
            panel_border=element_rect(size=0.3),
            
            text=element_text(family="Proxima Nova", weight='heavy'),
            axis_text=element_text(family="Geneva"),
            panel_grid_major=element_line(color='#A69C9C', size=0.5),
            #panel_grid_minor=element_line(color='#B0A5A5', size=0.35),
            panel_grid_minor=element_blank(), #ADD logic!
        )
    )
    save_picture(p, title, save_pic, dpi)
             
    return(p)    



#===SCATTERPLOTS===#

def do_scatter(
    df,
    type, # 'sig_vs_all', 'no_group' or 'groups',
    val_col_1, val_col_2,
    x_axis, y_axis, 

    title='', 
    regression_line=False,
    color=None,
    pearson=True,
    conf_col='Confidence',
    dpi=800,
    width=5, height=5,
    title_size=16,
    save_pic=False
):
    '''
    Various scatterplots in one function
    ============
    df – polars dataframe with comparable columns
    type – 'sig_vs_all' – df must have 'Confidence' column
         – 'no_group' – density style
         –  group column name
    val_col_1, val_col_2 – columns you want to compare
    x_axis, y_axis – must specify

    title=''
    regression_line=False
    pearson=True
    color=None – custom color for sig_vs_all, list of colors for groups, gradient for no_group
    save_pic=False – True, False or name.
                     if True then title, if no title then random number
    '''
    #1️⃣ Packages Import
    import polars as pl
    from scipy.stats import pearsonr
    from plotnine import (
        ggplot, aes, geom_point, scale_color_manual, guides, guide_legend,
        theme_minimal, labs, theme, element_text, element_blank, element_line,
        element_rect, geom_hline, geom_smooth, annotate, geom_pointdensity,
        scale_color_gradientn, scale_fill_manual, scale_linetype_manual
    )

    #2️⃣ Set colors
    if (type == 'sig_vs_all'):
        if isinstance(color, str): color= [color, '#CFD4DC']
        else: color= ['#264150', '#CFD4DC'] #FFC000 #FFAB0D
    elif (type == 'no_group'):
        if not isinstance(color, list): color= ['#172831', '#43748E', '#C4D0DC', '#E4ECF2']
    else:
        def_colors= ['#E0FFFF', '#335882', '#8FAF6F', '#6F8FAF', '#AF8F6F']
        if isinstance(color, list): color= color+def_colors
        else: color= def_colors
        num_groups= df.n_unique(subset=[type])
        color= color[:num_groups]

    #3️⃣ Pearson
    if (type == 'sig_vs_all'):
        sign_corr= pearsonr(df.filter(pl.col(conf_col) >= 0.05)[val_col_1], df.filter(pl.col(conf_col) >= 0.05)[val_col_2])[0]
        all_corr= pearsonr(df[val_col_1], df[val_col_2])[0]
        pearson_res= [f'Sign, R={sign_corr:.3f}', f'All, R={all_corr:.3f}']
        if not pearson: pearson_res= ['Sign', 'All']
        '''
        #! Additional conf lines for CAGI
        conf_plus_border= max(df.filter(pl.col(conf_col) < 0.05)[val_col_2].to_list())
        conf_minus_border= min(df.filter(pl.col(conf_col) < 0.05)[val_col_2].to_list())
        '''
    elif (type == 'no_group'):
        corr= pearsonr(df[val_col_1], df[val_col_2])[0]
        pearson_res= f'Pearson R:\n{corr:.3f}'
        if not pearson: pearson_res=''
    else:
        # add no pearson parameter!!!
        pearson_res= [
            f'{group}\nR={pearsonr(df.filter(pl.col(type) == group)[val_col_1], df.filter(pl.col(type) == group)[val_col_2])[0]:.3f}'
            for group in df[type].unique().to_list()
        ]
        

    #4️⃣ Plot
        
    p= ggplot(
        df, 
        aes(
            x=val_col_1, 
            y=val_col_2,
        )
    )
    if (type == 'sig_vs_all'):
        p= (p 
            + geom_point(
                shape='o',
                mapping=aes(fill=df[conf_col] < 0.05), 
                alpha=0.5,
                size=0.9, 
                stroke=0.05,
                color='black',
                show_legend=False,
            )
            #+ geom_hline(yintercept=conf_plus_border, linetype='dashed', color='black', size=0.65)
            #+ geom_hline(yintercept=conf_minus_border, linetype='dashed', color='black', size=0.65)
            + scale_fill_manual(
                values=color,
                labels=pearson_res,
            )
        )
        if regression_line:
            p = (p 
                + geom_smooth(
                    mapping=aes(linetype=f'"{pearson_res[1]}"'), 
                    method='lm', size=0.6, se=False, color='black'
                )
                + geom_smooth(
                    data=df.filter(pl.col(conf_col) >= 0.05),
                    mapping=aes(linetype=f'"{pearson_res[0]}"'), 
                    method='lm', size=0.6, se=False, color='black'
                )
                + scale_linetype_manual(
                    values={pearson_res[1]: 'solid', pearson_res[0]: 'dashed'}
                )
            )
        else:
            p= p + annotate(
                'text',
                x=0.98*min(df[val_col_1].to_list()), 
                y=0.9*max(df[val_col_2].to_list()),
                label='\n'.join(pearson_res),
                size=10,
                fontweight='bold',
                ha='left',
                va='top',
            )
    elif (type == 'no_group'):
        p= (p 
            + geom_pointdensity(
                alpha=0.6,
                size=0.8, 
                stroke=0.35,
                show_legend=False,
            )
            + annotate(
                'text',
                x=0.98*min(df[val_col_1].to_list()), 
                y=0.9*max(df[val_col_2].to_list()),
                label=pearson_res,
                size=10,
                fontweight='bold',
                ha='left',
                va='top',
            )
            + scale_color_gradientn(colors=color, guide=None)
        )
        if regression_line:
            p= p + geom_smooth(method='lm', linetype='dashed', size=0.8, color='black')
    else:
        p= (p 
            + geom_point(
                mapping=aes(color=type),
                alpha=0.4,
                size=0.7,
                stroke=0.35,
            )
            + scale_color_manual(
                values=color,
                labels=pearson_res
            )
            + guides(color=guide_legend(override_aes={'size': 6, 'alpha': 1, 'shape': 's'}))
        )
        if regression_line:
            p= p + geom_smooth(method='lm', mapping=aes(color=type), linetype='dashed', size=0.8, show_legend=False)
            
    p= (
        p
        + theme_minimal()
        + labs(
            x=x_axis, 
            y=y_axis,
            title=title
        )
        + theme(
            figure_size=(width, height),
            dpi=dpi,
            plot_margin=0.03,
            
            plot_title=element_text(vjust=0.4, size=title_size),
            
            legend_title=element_blank(), 
            legend_text= element_text(size=8, family="Avenir", weight='heavy'),
            legend_position=(0.05, 0.95),
            legend_background=element_rect(fill='#D9F4FA', color='black', size=0.5),
            #legend_key=element_rect(fill='#00FFFF', color='#00FFFF'),
            legend_key=element_blank(),
            
            axis_line_x=element_line(size=0.8),
            axis_text_x=element_text(rotation=0, size=8, family="Arial", weight='light'),
            axis_title_x=element_text(vjust=0.9),
            axis_text_y=element_text(family="Arial", weight='light'),
            
            plot_background=element_rect(fill="#E5FEFF"),
            #plot_background=element_rect(fill="white"),
            panel_background=element_rect(fill="#D9F4FA"), # #B4E9F5 #00FFFF #D9F4FA #E5FAFF  E6FCFC CCFBFF E5FDFF D9F4FA
            panel_border=element_rect(size=0.3),
            
            text=element_text(family="Proxima Nova", weight='heavy'),
            axis_text=element_text(family="Geneva"),
            panel_grid_major=element_line(color='#A69C9C', size=0.5),
            panel_grid_minor=element_line(color='#B0A5A5', size=0.35),
        )
    )
    save_picture(p, title, save_pic, dpi)
             
    return(p)



#===HEATMAPS===#

def do_heat_triangle(
    df_long,
    values_col,

    title='',
    legend_name='',
    rotate_x_ticks=None,
    color_list=['#DC143C', '#FF8C00', '#FFDAB9', '#E6E6FA'][::-1], #['#DC143C', 'white', '#9370DB']
    title_size=16,
    height=5,
    save_pic=False,
    dpi=800,
    annot_size=None
):
    '''
    Half of the usual heatmap with 1.0 diagonal
    ===========
    df_long polars df – in long form: item1 | item2 | values_col
    values_col

    legend_name=''
    title=''
    rotate_x_ticks=None – degrees
    color_list – gradient from min value to max. 
        Note: label color for "x < mean" values is black otherwise white.
    '''
    #1️⃣ Packages Import
    import polars as pl
    from plotnine import (ggplot, aes, geom_tile, geom_text, scale_color_identity,
        scale_fill_gradient2, scale_x_discrete, scale_y_discrete, theme_minimal, labs,
        theme, element_text, element_rect, element_blank, coord_fixed, scale_fill_gradientn
    )
    #from mizani.bounds import rescale_mid


    #2️⃣ Data prep
    df_long= (
        df_long
        .with_columns(pl.col(values_col).cast(pl.Float64))
        .with_columns(
            pl.when(pl.col(values_col).abs() > (pl.col(values_col).max()+pl.col(values_col).min())/pl.lit(2))
                .then(pl.lit('white'))
                .otherwise(pl.lit('black'))
                .alias('text_color')
        )
    )

    xy= df_long.columns
    xy.remove(values_col)
    xy.remove('text_color')

    items= df_long[xy[0]].unique(maintain_order=True).to_list() #Я чего-то не понимаю, и без maintain_order квадраты почему-то путаются
    height= 5+(1/4)*len(items)
    if not annot_size: annot_size= 15-0.5*len(items)

    #3️⃣ Plot
    p= (
        ggplot(
            data=df_long,
            mapping=aes(x=xy[0], y=xy[1], fill=values_col)
        )
        + geom_tile(color='white', width=0.98, height=0.98,)
        + coord_fixed()
        + geom_text(
            aes(label=df_long[values_col].round(3).cast(pl.String), color='text_color'),
            size=annot_size,
            show_legend=False,
        )
        + scale_color_identity()
        #+ scale_fill_gradient2(
        #    low=color_list[-1],
        #    mid=color_list[-2],
        #    high=color_list[-3],
        #    limits=[df_long[values_col].min(), df_long[values_col].max()],
        #    rescaler=lambda x, from_range: rescale_mid(x, mid=0, from_range=from_range), #Ад в этом разбираться :(
        #)
        + scale_fill_gradientn(
            colors=color_list,
            limits=[df_long[values_col].min(), df_long[values_col].max()]
        )
        + scale_x_discrete(limits=items)
        + scale_y_discrete(limits=items[::-1])
        + theme_minimal()
        + labs(
            title=title,
            fill=legend_name,
            x='', 
            y='',
        )
        + theme(
            figure_size=(height+1.5, height),
            dpi=dpi,
            plot_margin=0.03,
            
            plot_title=element_text(vjust=0.4, size=title_size),
            axis_text_x=element_text(family="Arial", weight='light'),
            axis_text_y=element_text(family="Arial", weight='light'),
            text=element_text(family="Proxima Nova", weight='heavy'),

            plot_background=element_rect(fill="#E5FEFF"),
            panel_background=element_rect(fill="#E5FEFF"),

            panel_grid=element_blank(),
        )
    )
    if rotate_x_ticks:
        p= p + theme(axis_text_x=element_text(rotation=rotate_x_ticks, family="Arial", weight='light', hjust=1))

    save_picture(p, title, save_pic, dpi)
             
    return(p)



def do_clustermap(
    df_long, value_col, x_col, y_col,
    title='',
    rotate_x_ticks=0,
    save_fig=False,
    metric='euclidean', method='average'
):
    '''
    PLACEHOLDER
    '''
    import polars as pl
    import matplotlib.pyplot as plt
    import seaborn as sns
    from matplotlib.colors import LinearSegmentedColormap
    
    df_long= df_long.with_columns(pl.col(value_col).cast(pl.Float64))

    wide= df_long.pivot(
        values=value_col,
        index=x_col,
        columns=y_col,
        aggregate_function='first'
    )
    
    heatmap_width= 6 + (4 / 8) * len(wide.columns[1:])
    colors= ['#4169E1', '#ADD8E6', '#7DF9FF'][::-1]
    cmap= LinearSegmentedColormap.from_list('', colors)
    cbar_ax_pos= [1.02, 0.1, 0.01, 0.8] 
    
    cluster= sns.clustermap(
        data=wide.drop('column_0'), 
        yticklabels=wide['column_0'], 
        xticklabels=wide.columns[1:],
        annot=True, fmt=".3f",
        cmap=cmap,
        linewidths=0.8,
        linecolor=(1, 1, 1, 0.2),
        figsize=(heatmap_width, heatmap_width),
        dendrogram_ratio=(0.1, 0.1),
        cbar_pos=cbar_ax_pos,
        cbar_kws={"shrink": 1}, # Gemini
        method=method,
        metric=metric,
    )
    
    cluster.ax_cbar.tick_params(labelsize=10)
    plt.setp(cluster.ax_cbar.get_yticklabels(), family='Proxima Nova') # Gemini
    
    cluster.fig.suptitle(title, family='Proxima Nova', fontsize=22, y=1.02)
    
    if save_fig:
        if isinstance(save_fig, str):
            cluster.savefig(f'/Users/hello/Desktop/Диплом/Тексты/Картинки/{save_fig}.png')
        elif (title != ''):
            cluster.savefig(f'/Users/hello/Desktop/Диплом/Тексты/Картинки/{title}.png')
        else:
            import random
            title= str(random.randint(1, 100000000000000))
            cluster.savefig(f'/Users/hello/Desktop/Диплом/Тексты/Картинки/{title}.png')
    
    plt.show()

    return()



#===DISTRIBUTION PLOTS===#

def do_jitterplot(
    data, metric,
    x_axis, y_axis, title,

    models_list=None,
    dodged=True,
    baseline=None, baseline_name='MLRG_5',
    baseline_min=None, baseline_min_name='LegZoi',
    save_pic=False,
    width=None, height=5, dpi=800,
    MODEL= 'Model', ELE='Element_type', FOLD='fold_id'
):
    '''
    Draw jitterplot, mostly for ensemble comparison in CV
    ================
    data - polars df or a path to a .tsv file. Has 'Model', 'Element_type', 'fold_id' and score columns
    metric – column name of the score. may be a list of two (all/confident subset)
    x_axis, y_axis, title – axis names, "" if empty
    #
    models_list – plot only selected models(ensembles)
    dodged=True – separate based on ELE column ("Element_type" by default)
    baseline=None – baseline as a dashed line, list for two metrics (ex. Ashi)
    baseline_min=None – performance of the best individual model (ex. LegZoi)
    save_pic=False – save .png to Картинки folder
    '''
    #1️⃣ Packages Import
    import polars as pl
    from plotnine import (ggplot, aes, geom_point, position_dodge, stat_summary, geom_hline,
        geom_text, scale_fill_manual, theme_minimal, labs, theme, element_text, element_blank,
        element_rect, element_line, facet_wrap, position_jitterdodge, geom_label, geom_vline, 
        guide_legend
    )

    #2️⃣ Data_prep / pivot_longer
    if isinstance(data, str):
        data= pl.read_csv(data, separator='\t')

    if isinstance(metric, str):
        metric= [metric]

    if baseline:
        if isinstance(baseline, str):
            baseline= [baseline]
        baseline= pl.DataFrame({
            'metric':  metric,
            'baseline': baseline,
            'label':  [baseline_name for _ in range(len(metric))]
        })

    if baseline_min:
        if isinstance(baseline_min, str):
            baseline_min= [baseline_min]
        baseline_min= pl.DataFrame({
            'metric':  metric,
            'baseline': baseline_min,
            'label':  [baseline_min_name for _ in range(len(metric))]
        })

    if models_list:
        data= data.filter(pl.col(MODEL).is_in(models_list))

    if not dodged:
        data= data.filter(pl.col(ELE) == 'All')

    data= (
        data
        .unpivot(
            on=metric,
            index=[MODEL, ELE, FOLD],
            variable_name='metric',
            value_name='score'
        )
        .with_columns(
            pl.col(FOLD).str.split(' ').list.get(1)
        )
    )
    labels_df= (
        data
        .group_by(ELE, MODEL, 'metric')
        .agg(
            pl.col('score').mean().round(4).alias('label'),
            (pl.col('score').max()+0.015).alias('y')
        )
    )

    #3️⃣ Plot
    p= (
        ggplot(
            data,
            aes(
                x='Model', 
                y='score',
                fill=ELE #ELE #ELE #data[ELE] #'Element_type' #ELE
            ),
        )
    )

    # Добавляем baseline
    for bl, bl_color in [(baseline, 'darkblue'), (baseline_min, 'red')]:
        if isinstance(bl, pl.DataFrame):
            p= (
                p
                + geom_hline(
                    data=bl,
                    mapping=aes(yintercept='baseline'),
                    color=bl_color,
                    size=0.9,
                    linetype='dashed',
                    inherit_aes=False
                )
            )

    # Точки и аннотация
    p= (
        p
        + geom_point(
            shape='o',
            color='black',
            stroke=0.4,
            size=4.5,
            alpha=0.8,
            position=position_jitterdodge(
                jitter_width=0.25, 
                dodge_width=1, 
                random_state=44
            ), 
        )
        + geom_text(
            aes(label=FOLD),
            position=position_jitterdodge(
                jitter_width=0.25, 
                dodge_width=1, 
                random_state=44
            ), 
            size=6,
            va='center',
            color='#3D3D3D'
        ) 
        + stat_summary(
            geom='errorbar',
            fun_y=lambda y: y.mean(), 
            fun_ymin=lambda y: y.mean(), 
            fun_ymax=lambda y: y.mean(),
            position=position_dodge(width=1),
            width=0.5,
            color='black',
            size=1,
            alpha=0.5
        )
        + stat_summary(
            mapping=aes(group=ELE),
            geom='point',
            shape='D',
            fun_y=lambda y: y.mean(), 
            position=position_dodge(width=1),
            size=2,
            color='black', fill='black',
            alpha=0.8
        )
        + geom_label(
            data=labels_df,
            mapping=aes(label='label', fill=ELE, x=MODEL, y='label'),
            #mapping=aes(label='label', fill=ELE, x=MODEL),
            #fun_y=lambda y: y.mean(),
            position=position_dodge(width=1),
            #va='bottom',
            size=6.5,
            color='black',
            show_legend=False,
        )
    )

    # Аннотация для baseline
    for bl, bl_color in [(baseline, 'darkblue'), (baseline_min, 'red')]:
            if isinstance(bl, pl.DataFrame):
                p=(
                    p           
                    + geom_text(
                        data=bl,
                        mapping=aes(x=0.1, y='baseline', label='label'),
                        va='bottom', ha='left',
                        color=bl_color,
                        size=10,
                        inherit_aes=False
                    )
                )

    #4️⃣ Theme setting
    n_models= data.n_unique(subset=[MODEL])
    if (width is None): width= 2.5 + 1.5 * n_models

    if (n_models <= 3):
        width*= len(metric)
        p= p + facet_wrap('metric', scales='free_y', ncol=len(metric))
    else:
        height*= len(metric)
        p= p + facet_wrap('metric', scales='free_y', nrow=len(metric))

    p= (
        p
        + scale_fill_manual(
            values=['#25DA9E', '#36896C', '#49B3E4'],
            guide=guide_legend(override_aes={'size': 10})
        )
        + geom_vline( # разделители/сетка
            xintercept=[i + 0.5 for i in range(data.unique(MODEL)[MODEL].len()+1)], 
            color='#B0A5A5',
            size=0.6,
            linetype='dashed'
        )
        + theme_minimal()
        + labs(
            x=x_axis, 
            y=y_axis,
            title=title
        )
        + theme(
            figure_size=(width, height),
            dpi=dpi,
            plot_margin=0.03,

            plot_title=element_text(vjust=0.5, size=16),

            legend_title=element_blank(), 
            legend_text= element_text(size=15, family="Avenir", weight='heavy'),
            legend_background=element_blank(),
            legend_key=element_blank(),

            axis_line_x=element_line(size=0.8),
            axis_title_x=element_text(vjust=0.9),
            axis_text_y=element_text(family="Arial", weight='light'),


            plot_background=element_rect(fill="#E5FEFF"),
            panel_background=element_rect(fill="#D9F4FA"), # #B4E9F5 #00FFFF #D9F4FA #E5FAFF  E6FCFC CCFBFF E5FDFF D9F4FA
            panel_border=element_rect(size=0.3),

            text=element_text(family="Proxima Nova", weight='heavy'),
            axis_text=element_text(family="Geneva"),
            panel_grid_major=element_line(color='#A69C9C', size=0.5),
            panel_grid_minor=element_line(color='#B0A5A5', size=0.35),
            panel_ontop=True

        )
    )
    save_picture(p, title, save_pic, dpi)

    return(p)



#===========================
#METRICS                   =
#===========================

def calc_metrics(
    comb_df, 
    name=None,
    VALUE='Value', CONF='Confidence', PREDICT='Predict', ELE='is_promoter'
):
    '''
    Calculates various metics for a given prediction
    =============
    comb_df – polars dataframe (or a path to) with 'Value', 'Confidence', 'is_promoter' & 'Predict' columns
            – list containing two dfs (paths), one is CAGI, other is prediction (joined by IDs)

    name=None – pass prediction id to be included in results. Good for later concatenation.
    PREDICT='Predict' – name of a column with predictions
    =============
    RETURNS a Tuple of Polars DataFrames
    + df with metrics for all/promoter/enchancer
    + combined df without nulls
    '''
    #1️⃣ Packages Import
    import polars as pl
    from scipy import stats
    import numpy as np
    from sklearn.metrics import roc_auc_score, average_precision_score

    #2️⃣ Data import (if paths provided)
    def load_df(df):
        if (type(df) == type('kkk')):
            df= pl.read_csv(df, separator='\t')
        return(df)
    if isinstance(comb_df, list):
        comb_df= [load_df(x) for x in comb_df]
        comb_df= comb_df[0].join(comb_df[1], on='ID', how='left')
    else: comb_df= load_df(comb_df)
    comb_df= comb_df.drop_nulls(subset=[PREDICT])

    if (name == None): name= []
    else: name= [name]

    ###⤵️ SUBROUTINE
    def calc_metrics_for_subset(subset, expr_filter):
        #rprint(1,comb_df)
        df= comb_df.filter(expr_filter)
        #print(2,df)
        #3️⃣ Separating variant into pos/neg/neu groups
        df= df.with_columns(
            ((pl.col(VALUE) > 0) & (pl.col(CONF) > 0.05)).alias('pos'),
            ((pl.col(VALUE) < 0) & (pl.col(CONF) > 0.05)).alias('neg'),
            (pl.col(CONF) > 0.05).alias('posneg'),
            (pl.col(CONF) <= 0.05).alias('neu')
        )
        POSNEU= df.filter(pl.col('neg')==False)
        POSNEG= df.filter(pl.col('neu')==False)
        NEGNEU= df.filter(pl.col('pos')==False)
        POSNEGNEU= df.with_columns(pl.col(PREDICT).abs())

        #4️⃣ Calculate metrics
        pearson= stats.pearsonr(df[VALUE], df[PREDICT])[0]
        pearsonc= stats.pearsonr(df.filter(pl.col(CONF) > 0.05)[VALUE], df.filter(pl.col(CONF) > 0.05)[PREDICT])[0]
        spearman= stats.spearmanr(df[VALUE], df[PREDICT])[0]
        spearmanc= stats.spearmanr(df.filter(pl.col(CONF) > 0.05)[VALUE], df.filter(pl.col(CONF) > 0.05)[PREDICT])[0]
        pearson_abs= stats.pearsonr(df[VALUE].abs(), df[PREDICT].abs())[0]
        pearsonc_abs= stats.pearsonr(df.filter(pl.col(CONF) > 0.05)[VALUE].abs(), df.filter(pl.col(CONF) > 0.05)[PREDICT].abs())[0]
        pos_neu= roc_auc_score(POSNEU['pos'], POSNEU[PREDICT])
        pos_neg= roc_auc_score(POSNEG['pos'], POSNEG[PREDICT])
        neg_neu= roc_auc_score(NEGNEU['neg'], NEGNEU[PREDICT]*(-1))
        posneg_neu= roc_auc_score(POSNEGNEU['posneg'], POSNEGNEU[PREDICT])
        posneg_neu_pr= average_precision_score(POSNEGNEU['posneg'], POSNEGNEU[PREDICT])
        metrics= name + [
            subset,
            pearson,
            pearsonc,
            spearman,
            spearmanc,
            pearson_abs,
            pearsonc_abs,
            pos_neu,
            pos_neg,
            neg_neu,
            posneg_neu,
            posneg_neu_pr
        ]

        return(metrics)

    #5️⃣ Combining metrics for subsets
    filters= [
        pl.lit(True),
        pl.col(ELE) == False,
        pl.col(ELE) == True
    ]
    subsets= ['All', 'Enhancer', 'Promoter']

    metrics= [calc_metrics_for_subset(subset, expr_filter) for subset, expr_filter in zip(subsets, filters)]

    if (name != []): name= ['Model']
    schema= name + [
        'Element_type',
        'Pearson R',
        'Pearson R on sign',
        'Spearman',
        'Spearman on sign',
        'R unsigned',
        'R unsigned on sign',
        'ROCAUC pos vs neu',
        'ROCAUC pos vs neg',
        'ROCAUC neg vs neu',
        'ROCAUC sign vs neu',
        'auPRC sign vs neu',
    ]
    comb_metrics= pl.DataFrame(np.array(metrics), schema=schema)
    if (name == []):
        comb_metrics= comb_metrics.with_columns(pl.exclude('Element_type').cast(pl.Float64))
    else: comb_metrics= comb_metrics.with_columns(pl.exclude('Model', 'Element_type').cast(pl.Float64)).sort(by='Element_type')
    
    return(comb_metrics, comb_df)
    


def compare_models_by_pwm_pearson(
    df_binding, df_prediction,
    task_name,

    save_figs=False,
    MODELS=None
):
    '''
    Calculates PearsonR for variants in specific binding sites
    AND
    Top binding sites by occurance
    =============
    df_binding, df_prediction – polars_df or paths
    task_name – included in plot titles and plot filenames

    save_figs=False – saved in Тексты folder
    MODELS=None – custom set of models with predefined order
    =============
    RETURNS A DICT
    + 'top_df': "sorted list of most occurent binding sites", 
    + 'top_pic'
    + 'raw_data': mapped predictions and TF bining sites (no filtration or correlation)
    + 'bar_all': bar correlation plot for top_20 TFs
    + 'bar_sign': bar correlation plot for sign variants from top_20 sign TFs
    + 'heat_all': heatmap correlation plot for top_20 TFs
    + 'heat_sign': heatmap correlation plot for sign variants from top_20 sign TFs
    + 'corr_all': data20_all,
    + 'corr_sign': data20_sign,
    '''
    #1️⃣ Packages/Data Import
    import polars as pl
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
    import seaborn as sns
    
    if(type(df_binding) == type('88005553535')):
        df_binding= pl.read_csv(df_binding, separator='\t', glob=False)
    if(type(df_prediction) == type('88005553535')):
        df_prediction= pl.read_csv(df_prediction, separator='\t', glob=False)
    if (MODELS is None) :
        MODELS= df_prediction.columns[4:]+ ['PWM']

    #2️⃣ Mapping CAGI7 Value/Confidence data, predictions on binding data
    df_binding= (
        df_binding
        .with_columns(
            pl.col('ID').str.split(':').list.get(0),
            (pl.col('pval_REF')/pl.col('pval_ALT')).log(2).alias('PWM'),
            pl.col('PWM_Name').str.split('.').list.get(0)
        )
        .join(
            pl.read_csv('/Users/hello/Desktop/Диплом/Данные/CAGI_7/CAGI7_short.tsv', separator='\t').select(
                ['ID', 'Value', 'Confidence', 'chr', 'pos', 'ref', 'alt', 'strand']
            ), 
            on='ID', 
            how='left'
        )
        .with_columns(
             pl.when(pl.col('Confidence') >= 0.05).then(pl.lit('sign')).otherwise(pl.lit('not_sign')).alias('is_sign'),
        )
    )
    data= df_binding.join(df_prediction, on=['ID', 'Value', 'Confidence'], how='inner')
    
    #3️⃣ Top_20 TFs by binding sites occurance
    top= (
        data
        .group_by(['PWM_Name', 'is_sign'])
        .agg(pl.col('ID').len().alias('num'))
        .pivot('is_sign', index='PWM_Name', values='num')
        .fill_null(0)
    )
    if ('sign' not in top.columns):
        top= top.with_columns(pl.lit(0).alias('sign'))
    top= (
        top
        .with_columns((pl.col('sign') + pl.col('not_sign')).alias('all'))
        .sort(by='all', descending=True)
    )
    
    #= PLOT
    fig, axes = plt.subplots(2, 1, figsize=(17, 20), dpi=200)
    fig.patch.set_facecolor('#E5FEFF')

    for i, ax in enumerate(axes):
        ax.set_facecolor('#D9F4FA')
        if (i == 0):
            sns.barplot(data=top.head(20), x='all', y='PWM_Name', 
                        color='#72CFE9', edgecolor='black', linewidth=1.2, ax=ax)
            sns.barplot(data=top.head(20), x='sign', y='PWM_Name', 
                        color='#2A5D78', edgecolor='black', linewidth=.8, ax=ax)
            ax.set_title(f'Частота встречаемости мотивов среди всех SNV | {task_name}', family='Proxima Nova', fontsize=18, pad=30)
            
            label1= mpatches.Patch(facecolor='#2A5D78', edgecolor='black', label='Significant')
            label2 = mpatches.Patch(facecolor='#72CFE9', edgecolor='black', label='Not significant')
            ax.legend(handles=[label1, label2], loc='lower right', fontsize=18, frameon=False)
        else: 
            sns.barplot(data=top.sort(by='sign', descending=True).head(20), x='sign', y='PWM_Name', 
                        color='#2A5D78', edgecolor='black', linewidth=.8, ax=ax)
            ax.set_title(f'Частота встречаемости мотивов среди значимых SNV | {task_name}', family='Proxima Nova', fontsize=18, pad=30)
        
        ax.set_ylabel('')
        ax.set_xlabel('')
        ax.grid(axis='x')
        ax.tick_params(axis='both', labelsize=16) 
        ax.set_yticklabels(ax.get_yticklabels(), family='Proxima Nova')
        
    plt.tight_layout()
    if save_figs:
        plt.savefig(f'/Users/hello/Desktop/Диплом/Тексты/Картинки/Топ встречающихся мотивов | {task_name}.png')
    top_pic= plt.gcf()
    plt.close()
    #===
    
    #4️⃣ Sign vs All
    data_all= (
        data
        .filter(pl.col('PWM_Name').is_in(top.filter(pl.col('all') > 30)['PWM_Name']))
        .join(top, on='PWM_Name', how='left')
    )
    data_sign= (
        data
        .filter(
            pl.col('Confidence') >= 0.05,
            #pl.col('PWM_Name').is_in(top.filter(pl.col('sign') > 30).sort(by='sign', descending=True)['PWM_Name'].to_list()[:20]),
            pl.col('PWM_Name').is_in(top.filter(pl.col('sign') > 30)['PWM_Name']),
        )
        .join(top, on='PWM_Name', how='left')
    )

    #5️⃣ Calculating PearsonR
    def corr_expr(name):
        return(pl.corr(pl.col('Value').filter(pl.col(name).is_not_null()),
                        pl.col(name).filter(pl.col(name).is_not_null())).alias(name))     
    data_all=(
        data_all
        .group_by('PWM_Name')
        .agg([corr_expr(model) for model in MODELS]+[pl.col('all').last()])
        .sort(by='all', descending=True)
        #.with_columns(pl.col('PWM'))
    )
    data20_all= data_all.head(20)

    data_sign=(
        data_sign
        .group_by('PWM_Name')
        .agg([corr_expr(model) for model in MODELS]+[pl.col('sign').last()])
        .sort(by='sign', descending=True)
        #.with_columns(pl.col('PWM'))
    )
    data20_sign= data_sign.head(20)

    #6️⃣ Heatmaps
    heatmap_width= 4.5 + (6 / 8) * len(MODELS)
    heatmap_height= 5 + (9 / 20) * data20_all['PWM'].len()

    pos_colors= ['#4169E1', '#ADD8E6', '#7DF9FF'][::-1] 
    neg_colors= ['#7DF9FF', '#C02E11']

    colors= ['#FFC88A', '#7DF9FF', '#ADD8E6', '#4169E1'] #'#6495ED', '#ADD8E6', '#7DF9FF – pos_old
    color_pos= [0.0, 0.5, 0.75, 1.0]
    cmap= LinearSegmentedColormap.from_list('', list(zip(color_pos, colors)))
    norm= TwoSlopeNorm(vcenter=0)


    #= PLOT All
    fig, ax = plt.subplots(figsize=(heatmap_width, heatmap_height), dpi=250)
    fig.patch.set_facecolor('#E5FEFF')

    heat= sns.heatmap(
        data=data20_all.drop(['PWM_Name', 'all']), 
        yticklabels=data20_all['PWM_Name'],  
        xticklabels=data20_all.columns[1:-1],
        annot=True, fmt=".3f",
        cmap=cmap,
        norm=norm,
        linewidths=0.8,
        linecolor=(1, 1, 1, 0.2) 
    )

    v_min= data20_all.drop(['PWM_Name', 'all']).min().min_horizontal().item()
    v_max= data20_all.drop(['PWM_Name', 'all']).max().max_horizontal().item()
    cbar= heat.collections[0].colorbar #Gemini
    cbar.ax.set_ylim(v_min, v_max)
    
    plt.title(f'Сравнение корреляций на всех вариантах | {task_name}', family='Proxima Nova', fontsize=18, pad=30)
    plt.yticks(rotation=0,family='Proxima Nova', fontsize=14)
    plt.xticks(fontsize=11)
    
    plt.tight_layout() 
    if save_figs:
        plt.savefig(f'/Users/hello/Desktop/Диплом/Тексты/Картинки/Сравнение корреляций на всех вариантах | {task_name} | heat.png')
    heat_all= plt.gcf()
    plt.close()
    #===

    #= PLOT sign
    if (data20_sign['sign'].len() > 0):
        heatmap_height= 5 + (9 / 20) * data20_sign['PWM'].len()
        fig, ax = plt.subplots(figsize=(heatmap_width, heatmap_height), dpi=250)
        fig.patch.set_facecolor('#E5FEFF')
        norm= TwoSlopeNorm(vcenter=0)

        heat= sns.heatmap(
            data=data20_sign.drop(['PWM_Name', 'sign']), 
            yticklabels=data20_sign['PWM_Name'], 
            xticklabels=data20_sign.columns[1:-1],
            annot=True, fmt=".3f",
            cmap=cmap,
            norm=norm,
            linewidths=0.8,
            linecolor=(1, 1, 1, 0.2) 
        )

        v_min= data20_sign.drop(['PWM_Name', 'sign']).min().min_horizontal().item()
        v_max= data20_sign.drop(['PWM_Name', 'sign']).max().max_horizontal().item()
        cbar= heat.collections[0].colorbar #Gemini
        cbar.ax.set_ylim(v_min, v_max)

        plt.title(f'Сравнение корреляций на значимых вариантах | {task_name}', family='Proxima Nova', fontsize=18, pad=30)
        plt.yticks(rotation=0,family='Proxima Nova', fontsize=14)
        plt.xticks(fontsize=11)
        
        plt.tight_layout()
        if save_figs:
            plt.savefig(f'/Users/hello/Desktop/Диплом/Тексты/Картинки/Сравнение корреляций на значимых вариантах | {task_name} | heat.png')
        heat_sign= plt.gcf()
        plt.close()
    else: heat_sign=''
    #===

    #7️⃣ Barplots
    data20_all= (
        data20_all
        .with_columns(pl.col('PWM').abs())
        .unpivot(
            on=MODELS, 
            index='PWM_Name', 
            variable_name='Model',
            value_name='Predict'
        )
        .sort(by='Predict', descending=True)
    )

    data20_sign= (
        data20_sign
        .with_columns(pl.col('PWM').abs())
        .unpivot(
            on=MODELS, 
            index='PWM_Name', 
            variable_name='Model',
            value_name='Predict'
        )
        .sort(by='Predict', descending=True)
    )

    #= PLOT All
    half= data20_all['PWM_Name'].unique(maintain_order=True).to_list()[:10]
    data20_all= data20_all.with_columns(pl.when(pl.col('PWM_Name').is_in(half)).then(pl.lit(0)).otherwise(pl.lit(1)).alias('ROW'))
    model_order= data20_all['Model'].unique(maintain_order=True).to_list()

    pic= sns.FacetGrid(data20_all, row='ROW', aspect=4, height=5, sharex=False)
    pic.map_dataframe(sns.barplot, x='PWM_Name', y='Predict', hue='Model', palette='viridis', hue_order=model_order)
    pic.add_legend(title='Model', loc='center left', bbox_to_anchor=(.9, 0.5), fontsize=18, title_fontsize=20)
    pic._legend.get_title().set_fontsize(21)
    pic.set_titles('')
    pic.fig.suptitle(f'Сравнение корреляций на всех вариантах | {task_name}')
    plt.ylabel('Pearson R')
    pic.fig.set_facecolor('#E5FEFF') #Gemini
    for ax in pic.axes.flat: 
        ax.set_facecolor('#E5FEFF') #Gemini
        ax.set_yticklabels(ax.get_yticklabels(), family='Proxima Nova')
        ax.set_ylabel('Pearson R', family='Proxima Nova')
        ax.set_xlabel('')
    
    #plt.tight_layout()
    if save_figs:
        plt.savefig(f'/Users/hello/Desktop/Диплом/Тексты/Картинки/Сравнение корреляций на всех вариантах | {task_name} | bar.png', bbox_inches='tight')
    bar_all= plt.gcf()
    plt.close()
    #===

    #= PLOT sign
    if (data20_sign['PWM_Name'].len() > 0):
        half= data20_sign['PWM_Name'].unique(maintain_order=True).to_list()[:10]
        data20_sign= data20_sign.with_columns(pl.when(pl.col('PWM_Name').is_in(half)).then(pl.lit(0)).otherwise(pl.lit(1)).alias('ROW'))
        model_order= data20_sign['Model'].unique(maintain_order=True).to_list()

        pic= sns.FacetGrid(data20_sign, row='ROW', aspect=4, height=5, sharex=False)
        pic.map_dataframe(sns.barplot, x='PWM_Name', y='Predict', hue='Model', palette='viridis', hue_order=model_order)
        pic.add_legend(title='Model', loc='center left', bbox_to_anchor=(.9, 0.5), fontsize=18, title_fontsize=20)
        pic._legend.get_title().set_fontsize(21) # Gemini (без этого почему-то не работает)
        pic.set_titles('')
        pic.fig.suptitle(f'Сравнение корреляций на значимых вариантах | {task_name}')
        pic.fig.set_facecolor('#E5FEFF') #Gemini
        for ax in pic.axes.flat: 
            ax.set_facecolor('#E5FEFF') #Gemini
            ax.set_yticklabels(ax.get_yticklabels(), family='Proxima Nova')
            ax.set_ylabel('Pearson R', family='Proxima Nova')
            ax.set_xlabel('')
        
        #plt.tight_layout()
        if save_figs:
            plt.savefig(f'/Users/hello/Desktop/Диплом/Тексты/Картинки/Сравнение корреляций на значимых вариантах | {task_name} | bar.png', bbox_inches='tight')
        bar_sign= plt.gcf()
        plt.close()
    else: bar_sign= ''
    #===

    return({
        'top_df': top,
        'top_pic': top_pic,
        'raw_data': data,
        'bar_all': bar_all,
        'bar_sign': bar_sign,
        'heat_all': heat_all,
        'heat_sign': heat_sign,
        'corr_all': data_all,
        'corr_sign': data_sign,
    })



def compare_models_by_pwm_zscore(
    df_binding, df_effect,
    task_name,

    save_fig=False,
    MODELS=None
):
    '''
    As in M.Beer? | OLD version without clustering
    =============
    df_binding, df_effect – polars_df or paths
    task_name – included in plot titles and plot filenames

    save_fig=False – save in __Тексты__ folder
    MODELS=None – custom set of models with predefined order
    =============
    RETURNS A DICT
    + 'zscore_df': "sorted list of most occurent binding sites", 
    + 'zscore_pic': a heatmap (sorted by MPRA_Effect >= 0)
    '''
    #1️⃣ Packages/Data Import
    import polars as pl
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    import seaborn as sns
    
    if(type(df_binding) == type('')):
        df_binding= pl.read_csv(df_binding, separator='\t', glob=False)
    if(type(df_effect) == type('')):
        df_effect= pl.read_csv(df_effect, separator='\t', glob=False)
    if (MODELS is None) :
        MODELS= df_effect.columns[1:]
    MODELS= MODELS + ['MPRA\neffect']

    #2️⃣ Mapping CAGI7 Value/Confidence data on binding data | MPRA_effect column
    df_binding= (
        df_binding
        .with_columns(
            pl.col('ID').str.split(':').list.get(0),
            pl.col('PWM_Name').str.split('.').list.get(0)
        )
        .join(
            pl.read_csv('/Users/hello/Desktop/Диплом/Данные/CAGI_7/CAGI7_short.tsv', separator='\t').select(
                ['ID', 'Value', 'Confidence', 'chr', 'pos', 'ref', 'alt', 'strand']
            ), 
            on='ID', 
            how='left'
        )
        .with_columns((pl.col('Confidence') >= 0.05).alias('MPRA\neffect'))
    )
    
    #3️⃣ Merging binding data and model predicted effects, calculating Z-score.
    z_scores= (
        df_binding
        .join(df_effect, on='ID', how='left')
        .group_by('PWM_Name').agg(pl.col(MODELS).mean())
        .with_columns([
            ((pl.col(model) - pl.col(model).mean()) / pl.col(model).std())
            for model in MODELS
        ])
        .sort(by='MPRA\neffect', descending=True)
    )

    #4️⃣ Heatmap
    zscores_top= z_scores.filter(pl.col('MPRA\neffect') >= 0)
    heatmap_width= 6 + (7 / 8) * len(MODELS)
    fig, ax = plt.subplots(figsize=(heatmap_width, 15), dpi=250)
    fig.patch.set_facecolor('#E5FEFF')
    colors= ['#4169E1', '#ADD8E6', '#7DF9FF'][::-1] #'#6495ED', '#ADD8E6', '#7DF9FF
    cmap= LinearSegmentedColormap.from_list('', colors)
    sns.heatmap(
        data=zscores_top.drop(['PWM_Name']), 
        yticklabels=zscores_top['PWM_Name'], 
        xticklabels=zscores_top.columns[1:],
        annot=True, fmt=".3f",
        cmap=cmap,
        linewidths=0.8,
        linecolor=(1, 1, 1, 0.2),
        cbar_kws={'label': 'z-score'}
    )
    
    plt.title(f'Сравнение моделей по значимости мотивов | {task_name}', family='Proxima Nova', fontsize=18, pad=30)
    y_fontsize= 5 + (11 * 20) / zscores_top['PWM_Name'].len()
    plt.yticks(rotation=0,family='Proxima Nova', fontsize=y_fontsize)
    plt.xticks(fontsize=12)
    
    plt.tight_layout() 
    if save_fig:
        plt.savefig(f'/Users/hello/Desktop/Диплом/Тексты/Картинки/Z_Score | {task_name} | heat.png')
    zscore_pic= plt.gcf()
    plt.close()
    #===
 
    return({
        'zscore_df': z_scores,
        'zscore_pic': zscore_pic,
    })


#===========================
#ENSEMBLING                =
#===========================

def make_ensemble(
    data,
    ensemble_name,
    model,
    
    gs_parameters=dict(),
    use_scaler=True,
    save_result=True, add_result_to=None,
    custom_folds=None,
    gs_jobs=1,
    VALUE='Value', CONF='Confidence', CHR='chr', ELE='is_promoter', ID='ID',
    categories=None
):
    '''
    Create and score ensembles (meta-models) of different predictions with cross validation
    ==============
    data – polars df (or a list of dfs) with model prediction columns, "Value", "Confidence", "chr", 
        "is_promoter" and "ID""
    ensemble_name – ex. "lasso with\nAlphaGenome"
    model – sklearn-compatible
    #
    gs_parameters – dict, prameters for sklearn`s grid_search
    use_scaler=True – switch on/off sklearn StandardScaler
    save_result=True – save raw (across folds) and mean metrics as .tsv files
    add_result_to=None – add results to a combined table, path or list of paths should be provided
    custom_folds=None – replace hardcoded ones
    categories – pass a list of categorical columns' names to Catboost
    ==============  
    RETURNS A DICT
    + prints chosen parameters for each fold and feature importances
    + 'raw_metrics': metrics for all folds (df)
    + 'mean_metrics': df, also printed
    + 'pearson_plot': plotnine jitterplot
    '''
    #1️⃣ Packages import, data prep
    from tqdm.notebook import tqdm
    import polars as pl
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import GridSearchCV
    from sklearn.base import clone

    pl.Config.set_tbl_cols(-1)
    pl.Config.set_tbl_rows(-1)
    pl.Config.set_float_precision(4)
    pl.Config.set_tbl_width_chars(200)

    if isinstance(data, pl.DataFrame):
        #data= data.drop_nulls()
        model_names= [model for model in data.columns if model not in [VALUE, CONF, CHR, ELE, ID]]
    else: 
        #data= [df.drop_nulls() for df in data]
        model_names= [model for model in data[0].columns if model not in [VALUE, CONF, CHR, ELE, ID]]


    #2️⃣ Ensembling & Scoring Subroutine
    def score_fold(f_index, fold):
        def get_gspredict(d_index, data):
            current_model= clone(model)
            if categories:
                current_model.set_params(cat_features=categories)
            Train= data.filter(~ pl.col(CHR).is_in(fold)).drop(CHR)
            Test= data.filter(pl.col(CHR).is_in(fold)).drop(CHR)
            Train_X= Train.drop([VALUE, CONF, ELE, ID])
            Train_y= Train[VALUE].to_list()
            Test_X= Test.drop([VALUE, CONF, ELE, ID])
            Test_y= Test.select([VALUE, CONF, ELE, ID])

            if use_scaler:
                Train_X= scaler.transform(Train_X)
                Test_X= scaler.transform(Test_X)

            if gs_parameters:
                grid_search= GridSearchCV(
                    estimator= current_model, 
                    param_grid= gs_parameters,
                    refit=True,
                    cv=2,
                    n_jobs=gs_jobs
                )
                grid_search.fit(Train_X, Train_y)
                predicts= grid_search.predict(Test_X)
                best_params.append(f'{f_index} fold {d_index} {grid_search.best_params_}')
                current_model= grid_search.best_estimator_
            else:
                current_model.fit(Train_X, Train_y)
                predicts= current_model.predict(Test_X)

            # TODO для других случаев
            if (str(f_index) not in coefs):
                if hasattr(current_model, 'coef_'):
                    coefs[str(f_index)]= [list(current_model.coef_)]
                elif hasattr(current_model, 'feature_importances_'):
                    coefs[str(f_index)]= [list(current_model.feature_importances_)]
            else:
                if hasattr(current_model, 'coef_'):
                    coefs[str(f_index)].append(list(current_model.coef_))
                elif hasattr(current_model, 'feature_importances_'):
                    coefs[str(f_index)].append(list(current_model.feature_importances_))

            Prediction= Test_y.with_columns(pl.Series(predicts).alias('Predict'))

            return(Prediction)

        if isinstance(data, list):
            if use_scaler:
                scaler= StandardScaler().fit(pl.concat(data).unique('ID').drop([VALUE, CONF, CHR, ELE, ID]))
            predicts= pl.concat(
                map(
                    lambda x: get_gspredict(*x), 
                    tqdm(enumerate(data, start=1), 
                        desc='FOLD:', colour='blue', leave=False,
                        dynamic_ncols=True, total=len(data),
                    )
                )
            )
        else: 
            if use_scaler:
                scaler= StandardScaler().fit(data.drop([VALUE, CONF, CHR, ELE, ID]))
            predicts= get_gspredict('', data)
        predicts= predicts.group_by([VALUE, CONF, ELE, ID]).agg(pl.all().min())

        metrics, _ = calc_metrics(predicts, name=ensemble_name)
        metrics= metrics.with_columns(
            pl.lit(f'fold {f_index}').alias('fold_id'),
            pl.lit(':'.join(fold)).alias('fold_info'),
        )

        return(metrics)

    #3️⃣ Hardcoded folds
    if not custom_folds:
        folds= [                #8 штук
            ['chr1'], #8413
            ['chr2'], #7960
            ['chr5', 'chr16'], #8177
            ['chr3', 'chr12'], #9656
            ['chr7', 'chr9'], #8461
            ['chr4', 'chr10'], #8320
            ['chr6','chr8'], #10693
            ['chr17', 'chr11'], #8561 # мне кажется, нормально
        ]
    else: folds= custom_folds

    #4️⃣ Ensembling
    best_params= []
    coefs= {'Model': model_names}

    ensemble_metrics= pl.concat(
        map(lambda x: score_fold(*x), 
            tqdm(
                enumerate(folds, start=1),
                desc='PROGRESS:', colour='red',
                dynamic_ncols=True, total=len(folds),
            )

        )
    )

    metrics_mean_show= (
        ensemble_metrics
        .drop(['fold_id', 'fold_info', 'Model'])
        .group_by('Element_type')
        .agg(pl.all().mean())
    )


    #5️⃣ Save/print results
    if (gs_parameters != dict()):
        print('BEST PARAMETERS')
        print('\n'.join(best_params))
        print('\n')

    if (len(coefs.keys()) > 1):
        print('IMPORTANCE')
        for i in range(len(folds)):
            i= str(1+i)
            coefs[i]= [sum(x) / len(x) for x in zip(*coefs[i])]
        coefs= (
            pl.DataFrame(coefs)
            .with_columns(
                pl.mean_horizontal(pl.exclude('Model')).alias('mean')
            )
        )
        print(coefs.sort(by=pl.col('mean').abs(), descending=True).head(40))
        print('\n')

    print('METRICS MEAN')
    print(metrics_mean_show)

    if save_result:
        ensemble_metrics.write_csv(f'{ensemble_name.replace("\n", " ")} metrics.tsv', separator='\t')
        metrics_mean_show.write_csv(f'MEAN {ensemble_name.replace("\n", " ")} metrics.tsv', separator='\t')

    if add_result_to:
        def add_result(path):
            comb_df= pl.concat([
                pl.read_csv(path, separator='\t'),
                ensemble_metrics
            ])
            comb_df.write_csv(path, separator='\t')

            return()

        if isinstance(add_result_to, list):
            for path in add_result_to: add_result(path)
        else: add_result(add_result_to)

    p= do_jitterplot(
        ensemble_metrics,
        ['Pearson R', 'Pearson R on sign'],
        x_axis='', y_axis='', title='', dpi=100
    )

    return({
        'raw_metrics': ensemble_metrics,
        'mean_metrics': metrics_mean_show,
        'pearson_plot': p
    })



def make_ape(
    affinity_df, affinity_threshold, motif_occurance_threshold,
    expression_df, expression_threshold, #Human protein atlas nTPM
    cagi_df, 
    cagi_value_col='Value', cagi_chromosome_col='chr', cagi_confidence_col='Confidence', cagi_element_col='is_promoter',
    method= ['ABS_MAX', 'AVG'], #across TF, across ID
    folds='default'
):
    '''
    Create and score APE PWM encembles
    Pass custom fold with train and test for final prediction or multiple for CV parameter optimization 
    ==============
    affinity_df – has CAGI ID, PWM name (starts with TF) and p-values from perfectos-ape. default ape-scoring script output
    affinity_threshold
    motif_occurance_threshold – if a motif is rare, it's correlation may be unstable
    expression_df, expression_threshold – from HPA, threshold for nTPM column
    cagi_df – default short one

    method= ['ABS_MAX', 'AVG'] – list containing methods for motif or tf aggregation
        ABS_MAX, AVG or WEIGHTED
    folds– train and predict custom folds. Default is standard cagi
    ==============  
    RETURNS A DICT
    + i – number of the fold, is a dict:
        + corr_df_motif
        + corr_df_tf
        + prediction
        + metrics
    + final – ploars df with mean metrics values across folds
    '''
    import polars as pl
    from scipy import stats
    import warnings
    warnings.filterwarnings('ignore', category=stats.ConstantInputWarning)

    if isinstance(affinity_df, str): affinity_df=pl.read_csv(affinity_df, separator='\t')
    if isinstance(expression_df, str): expression_df=pl.read_csv(expression_df, separator='\t')
    if isinstance(cagi_df, str): cagi_df=pl.read_csv(cagi_df, separator='\t')

    affinity_df= (
        affinity_df
        .with_columns(pl.col('ID').str.split(':').list.get(0))
        .join(cagi_df.select(['ID', cagi_value_col, cagi_chromosome_col]), on='ID')
    )

    if (folds == 'default'):
        folds= {
            ('chr14','chr20','chr15','chr13', 'chr21','chr22', 'chr18',): ('chr19',),
            ('chr19','chr20','chr15','chr13', 'chr21','chr22', 'chr18',): ('chr14',),
            ('chr19','chr14','chr15','chr13', 'chr21','chr22', 'chr18',): ('chr20',),
            ('chr19','chr14','chr20','chr13', 'chr21','chr22', 'chr18',): ('chr15',),
            ('chr19','chr14','chr20','chr15','chr22', 'chr18',): ('chr13', 'chr21',),
            ('chr19','chr14','chr20','chr15','chr13', 'chr21',): ('chr22', 'chr18',),
        }

    TF_exclusion_list= (
        expression_df
        .filter(
            pl.col('Cell line') == 'Hep-G2',
            pl.col('nTPM') < expression_threshold
        )
    )['Gene name'].to_list()

    affinity_df= (
        affinity_df
        .with_columns(
            pl.col('PWM_Name').str.split('.').list.get(0).alias('Gene_name'),
            (pl.col('pval_REF')/(pl.col('pval_ALT')+pl.lit(10**-15))).log(2).alias('PWM_Value'),
        )
        .filter(~pl.col('Gene_name').is_in(TF_exclusion_list))
    )

    result= dict()
    i= 0
    for train_chr, test_chr in folds.items() :
        i+= 1
        result[i]= dict()

        affinity_df_train= affinity_df.filter(pl.col(cagi_chromosome_col).is_in(train_chr))
        affinity_df_test= affinity_df.filter(pl.col(cagi_chromosome_col).is_in(test_chr))

        corr_df_motif= (
            affinity_df_train
            .group_by('PWM_Name')
            .agg(
                pl.corr('PWM_Value', cagi_value_col).alias('Pearson'),
                pl.corr('PWM_Value', cagi_value_col).abs().alias('Pearson_abs'),
                pl.corr('PWM_Value', cagi_value_col).sign().alias('Sign'),
                pl.col('ID').len().alias('Occurance')
            )
            .filter(pl.col('Occurance') >= motif_occurance_threshold)
            .sort(by='Pearson_abs', descending=True)
        )
        if (affinity_threshold >= 1): # by rank
            corr_df_motif= corr_df_motif.head(affinity_threshold)
        else: # by correlation
            corr_df_motif= corr_df_motif.filter(pl.col('Pearson_abs') >= affinity_threshold)
        worst_corr= corr_df_motif['Pearson_abs'].to_list()[-1]
        result[i]['corr_df_motif']= corr_df_motif

        affinity_df_train= (
            affinity_df_train
            .join(corr_df_motif, on='PWM_Name')
            .with_columns(pl.col('PWM_Value') * pl.col('Sign'))
        )
        if (method[0] == 'ABS_MAX'):
            affinity_df_train= (
                affinity_df_train
                .group_by(['ID', 'Gene_name', cagi_value_col])
                .agg(pl.col('PWM_Value').sort_by(pl.col('PWM_Value').abs()).last().alias('TF_Value'))
            )
        elif (method[0] == 'AVG'):
            affinity_df_train= (
                affinity_df_train
                .group_by(['ID', 'Gene_name', cagi_value_col])
                .agg(pl.col('PWM_Value').mean().alias('TF_Value'))
            )
        else: #WEIGHTED
            affinity_df_train= (
                affinity_df_train
                .group_by(['ID', 'Gene_name', cagi_value_col])
                .agg(
                    (((pl.col('PWM_Value')*pl.col('Pearson_abs')).sum())/(pl.col('Pearson_abs').sum())).alias('TF_Value')
                )
            )
        corr_df_tf= (
            affinity_df_train
            .group_by('Gene_name')
            .agg(
                pl.corr('TF_Value', cagi_value_col).alias('Pearson'),
                pl.corr('TF_Value', cagi_value_col).abs().alias('Pearson_abs'),
                pl.col('ID').len().alias('Occurance')
            )
            .sort(by='Gene_name', descending=True)
        )
        result[i]['corr_df_tf']= corr_df_tf
        number_of_tfs= corr_df_tf['Gene_name'].len()


        affinity_df_test= (
            affinity_df_test
            .join(corr_df_motif, on='PWM_Name')
            .with_columns(pl.col('PWM_Value') * pl.col('Sign'))
        )
        if (method[0] == 'ABS_MAX'):
            affinity_df_test= (
                affinity_df_test
                .group_by(['ID', 'Gene_name'])
                .agg(pl.col('PWM_Value').sort_by(pl.col('PWM_Value').abs()).last().alias('TF_Value'))
            )
        elif (method[0] == 'AVG'):
            affinity_df_test= (
                affinity_df_test
                .group_by(['ID', 'Gene_name'])
                .agg(pl.col('PWM_Value').mean().alias('TF_Value'))
            )
        else: #WEIGHTED
            affinity_df_test= (
                affinity_df_test
                .group_by(['ID', 'Gene_name'])
                .agg(
                    (((pl.col('PWM_Value')*pl.col('Pearson_abs')).sum())/(pl.col('Pearson_abs').sum())).alias('TF_Value')
                )
            )           

        if (method[1] == 'ABS_MAX'):
            affinity_df_test= (
                affinity_df_test
                .group_by(['ID'])
                .agg(pl.col('TF_Value').sort_by(pl.col('TF_Value').abs()).last().alias('Predict'))
            )
        elif (method[1] == 'AVG'):
            affinity_df_test= (
                affinity_df_test
                .group_by(['ID'])
                .agg(pl.col('TF_Value').mean().alias('Predict'))
            )
        else: #WEIGHTED
            affinity_df_test= (
                affinity_df_test
                .join(corr_df_tf, on='Gene_name')
                .group_by(['ID'])
                .agg(
                    ((pl.col('TF_Value')*pl.col('Pearson_abs')).sum()/(pl.col('Pearson_abs').sum())).alias('Predict')
                )
            )               

        test_predict= (
            cagi_df
            .filter(pl.col(cagi_chromosome_col).is_in(test_chr))
            .join(affinity_df_test, on='ID', how='left')
        )
        null_ratio= test_predict['Predict'].is_null().mean()
        test_predict= test_predict.fill_null(0) #!!!!
        result[i]['prediction']= test_predict       

        metrics= (
            calc_metrics(test_predict, VALUE=cagi_value_col, CONF=cagi_confidence_col, ELE=cagi_element_col, PREDICT='Predict')[0]
            .fill_null(0)
            .fill_nan(0)
            .with_columns(
                pl.lit(null_ratio).alias('Null_Ratio'),
                pl.lit(worst_corr).alias('Corr_Thr'),
                pl.lit(number_of_tfs).alias('Number_of_TFs')
            )
            .sort(by='Element_type')
        )
        result[i]['metrics']= metrics

    metrics= (
        pl.concat([result[l+1]['metrics'] for l in range(i)])
        .group_by('Element_type')
        .agg(pl.all().mean())
        .with_columns(pl.lit(affinity_threshold).alias('Affinity_Threshold'))
        .sort(by='Element_type')
    )
    result['final']= metrics

    return(result)