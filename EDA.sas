/* Importar la base de datos */
proc import datafile='/home/u63982561/ProyectoPeso/DEXMXUS.csv'
    out=tipos_cambio
    dbms=csv
    replace;
    getnames=yes;
run;

/* Calcular estadísticos descriptivos básicos */
proc means data=tipos_cambio n mean median mode min max range std skewness kurtosis;
    var DEXMXUS;
    output out=estadisticos
        mean=Media
        median=Mediana
        mode=Moda
        min=Minimo
        max=Maximo
        range=Rango
        std=DesviacionEstandar
        skewness=Sesgo
        kurtosis=Curtosis;
run;

/* Generar un histograma para visualizar la distribución */
proc sgplot data=tipos_cambio;
    histogram DEXMXUS / binwidth=0.5;
    xaxis label="Tipo de Cambio (MXN/USD)";
    yaxis label="Frecuencia";
    title "Distribución del Tipo de Cambio";
run;



/* Análisis de tendencias temporales */
proc sgplot data=tipos_cambio;
    series x=DATE y=DEXMXUS;
    xaxis label="Fecha";
    yaxis label="Tipo de Cambio (MXN/USD)";
    title "Tendencia Temporal del Tipo de Cambio";
run;
