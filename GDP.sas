/* Importar la base de datos */
proc import datafile='/home/u63982561/ProyectoPeso/RGDP.csv'
    out=rgdp_mx
    dbms=csv
    replace;
    getnames=yes;
run;

/* Calcular estadísticos descriptivos básicos */
proc means data=rgdp_mx n mean median mode min max range std skewness kurtosis;
    var NGDPRSAXDCMXQ;
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
proc sgplot data=rgdp_mx;
    histogram NGDPRSAXDCMXQ / binwidth=500000;
    xaxis label="PIB Real Ajustado (Millones de MXN)";
    yaxis label="Frecuencia";
    title "Distribución del PIB Real Ajustado en México";
run;


/* Análisis de tendencias temporales */
proc sgplot data=rgdp_mx;
    series x=observation_date y=NGDPRSAXDCMXQ;
    xaxis label="Fecha";
    yaxis label="PIB Real Ajustado (Millones de MXN)";
    title "Tendencia Temporal del PIB Real Ajustado en México";
run;
