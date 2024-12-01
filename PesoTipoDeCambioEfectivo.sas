/* Importar la base de datos del tipo de cambio real efectivo */
data rbmx;
    infile '/home/u63982561/ProyectoPeso/RBMXBIS.csv' delimiter=',' firstobs=2;
    input observation_date :yymmdd10. RBMXBIS;
    format observation_date date9.;
run;

/* Importar la base de datos del tipo de cambio peso-dólar */
data dexmx;
    infile '/home/u63982561/ProyectoPeso/DEXMXUS.csv' delimiter=',' firstobs=2;
    input DATE :yymmdd10. DEXMXUS;
    format DATE date9.;
run;

/* Crear un formato mensual para la fecha del tipo de cambio peso-dólar */
data dexmx_monthly;
    set dexmx;
    month_date = intnx('month', DATE, 0, 'b');
    format month_date date9.;
    keep month_date DEXMXUS;
run;

/* Calcular el promedio mensual del tipo de cambio peso-dólar */
proc means data=dexmx_monthly noprint;
    class month_date;
    var DEXMXUS;
    output out=dexmx_avg mean=DEXMXUS_avg;
run;

/* Limpiar el dataset de promedios mensuales */
data dexmx_final;
    set dexmx_avg;
    if _type_ = 0 then delete;
    drop _type_ _freq_;
    rename month_date=observation_date DEXMXUS_avg=DEXMXUS;
run;

/* Combinar ambas bases de datos por fecha */
proc sort data=rbmx;
    by observation_date;
run;

proc sort data=dexmx_final;
    by observation_date;
run;

data combined_data;
    merge rbmx(in=a) dexmx_final(in=b);
    by observation_date;
    if a and b;
    /* Crear variables de variación mensual */
    retain prev_RBMXBIS prev_DEXMXUS;
    var_RBMXBIS = ((RBMXBIS - prev_RBMXBIS)/prev_RBMXBIS)*100;
    var_DEXMXUS = ((DEXMXUS - prev_DEXMXUS)/prev_DEXMXUS)*100;
    prev_RBMXBIS = RBMXBIS;
    prev_DEXMXUS = DEXMXUS;
    if _n_ = 1 then do;
        var_RBMXBIS = .;
        var_DEXMXUS = .;
    end;
    label 
        RBMXBIS = 'Tipo de Cambio Real Efectivo'
        DEXMXUS = 'Tipo de Cambio Peso-Dólar'
        var_RBMXBIS = 'Variación % TCRE'
        var_DEXMXUS = 'Variación % TC Peso-Dólar';
run;

/* 1. Estadísticas descriptivas clave */
proc means data=combined_data n mean std min max;
    title 'Estadísticas Descriptivas Principales';
    var RBMXBIS DEXMXUS var_RBMXBIS var_DEXMXUS;
run;

/* 2. Análisis de correlación con visualización */
proc corr data=combined_data pearson plots=scatter(nvar=all);
    title 'Análisis de Correlación';
    var RBMXBIS DEXMXUS;
run;

/* 3. Series de tiempo en un solo gráfico */
proc sgplot data=combined_data;
    title 'Evolución Temporal de Tipos de Cambio';
    series x=observation_date y=RBMXBIS / lineattrs=(color=blue) legendlabel='TCRE';
    series x=observation_date y=DEXMXUS / y2axis lineattrs=(color=red) legendlabel='TC Peso-Dólar';
    yaxis label='Tipo de Cambio Real Efectivo';
    y2axis label='Tipo de Cambio Peso-Dólar';
    xaxis label='Fecha';
    keylegend / title='Variables:';
run;

/* 4. Análisis de regresión simple */
proc reg data=combined_data plots(only)=(fit residuals);
    title 'Relación entre TCRE y TC Peso-Dólar';
    model RBMXBIS = DEXMXUS / clb;
quit;

/* 5. Resumen mensual de variaciones */
proc means data=combined_data maxdec=2;
    title 'Resumen de Variaciones Mensuales';
    var var_RBMXBIS var_DEXMXUS;
    output out=volatility_summary 
           mean= std= min= max= / autoname;
run;