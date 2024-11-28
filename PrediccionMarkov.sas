/* Importar la base de datos */
proc import datafile='/home/u63982561/ProyectoPeso/DEXMXUS.csv'
    out=tipos_cambio
    dbms=csv
    replace;
    getnames=yes;
run;

/* Ordenar los datos por fecha */
proc sort data=tipos_cambio;
    by DATE;
run;

/* Crear variables adicionales para análisis más detallado */
data tipos_cambio;
    set tipos_cambio;
    lag_value = lag(DEXMXUS);
    if lag_value ne . then do;
        cambio = DEXMXUS - lag_value;
        cambio_porcentual = (cambio / lag_value) * 100;
        
        /* Estados más granulares basados en la magnitud del cambio */
        if cambio_porcentual <= -1 then estado = -2;      /* Caída fuerte */
        else if -1 < cambio_porcentual <= -0.2 then estado = -1; /* Caída moderada */
        else if -0.2 < cambio_porcentual < 0.2 then estado = 0;  /* Estable */
        else if 0.2 <= cambio_porcentual < 1 then estado = 1;    /* Subida moderada */
        else if cambio_porcentual >= 1 then estado = 2;          /* Subida fuerte */
    end;
    estado_1 = lag(estado);
    
    /* Agregar número de observación */
    obs_num = _N_;
run;

/* Calcular matriz de transición */
proc sql;
    /* Primero calculamos el total de transiciones por estado inicial */
    create table totales as
    select estado_1, 
           count(*) as total_trans
    from tipos_cambio
    where estado_1 is not null
    group by estado_1;

    /* calculamos las probabilidades de transición */
    create table matriz_transicion as
    select a.estado_1, 
           a.estado,
           count(*) as frecuencia,
           count(*) / b.total_trans as probabilidad
    from tipos_cambio a
    inner join totales b on a.estado_1 = b.estado_1
    where a.estado_1 is not null
    group by a.estado_1, a.estado
    order by estado_1, estado;
quit;

/* Predicción */
data predicciones;
    /* Primero, cargar la última observación de tipos_cambio */
    if _N_ = 1 then do;
        declare hash h_trans(dataset: 'matriz_transicion');
        h_trans.defineKey('estado_1', 'estado');
        h_trans.defineData('probabilidad');
        h_trans.defineDone();
        
        /* Obtener el último valor y estado */
        do until (last);
            set tipos_cambio end=last;
        end;
        ultima_fecha = DATE;
        ultimo_valor = DEXMXUS;
        estado_actual = estado;
    end;
    
    /* Realizar simulaciones */
    do simulacion = 1 to 30;
        valor_actual = ultimo_valor;
        estado_sim = estado_actual;
        
        do dia = 1 to 10;
            /* Generar número aleatorio */
            call streaminit(simulacion * 1000 + dia);
            prob = rand('UNIFORM');
            
            /* Determinar siguiente estado */
            prob_acum = 0;
            do estado_posible = -2 to 2;
                if h_trans.find(key: estado_sim, key: estado_posible) = 0 then do;
                    prob_acum + probabilidad;
                    if prob <= prob_acum then do;
                        siguiente_estado = estado_posible;
                        leave;
                    end;
                end;
            end;
            
            /* Si no se encontró estado siguiente, mantener el actual */
            if siguiente_estado = . then siguiente_estado = estado_sim;
            
            /* Calcular cambio basado en estado */
            select (siguiente_estado);
                when (-2) cambio = -0.015 * valor_actual;
                when (-1) cambio = -0.005 * valor_actual;
                when (0)  cambio = 0;
                when (1)  cambio = 0.005 * valor_actual;
                when (2)  cambio = 0.015 * valor_actual;
                otherwise cambio = 0;
            end;
            
            valor_actual = valor_actual + cambio;
            estado_sim = siguiente_estado;
            
            /* Guardar predicción */
            DATE = intnx('day', ultima_fecha, dia);
            DEXMXUS = valor_actual;
            output;
        end;
    end;
    keep DATE DEXMXUS simulacion;
stop;
run;

/* Ordenar las predicciones por fecha */
proc sort data=predicciones;
    by DATE simulacion;
run;

/* Calcular estadísticas de las predicciones */
proc means data=predicciones noprint;
    by DATE;
    var DEXMXUS;
    output out=stats_pred
           mean=DEXMXUS_mean
           p5=DEXMXUS_lower
           p95=DEXMXUS_upper;
run;

/* Ordenar las estadísticas por fecha */
proc sort data=stats_pred;
    by DATE;
run;

/* Gráfica final */
proc sgplot data=stats_pred;
    band x=DATE upper=DEXMXUS_upper lower=DEXMXUS_lower / 
         transparency=0.6 legendlabel="Intervalo de Confianza 90%"
         fillattrs=(color=lightblue);
    series x=DATE y=DEXMXUS_mean / lineattrs=(color=darkblue thickness=2) 
           legendlabel="Predicción Media";
    xaxis label="Fecha" grid;
    yaxis label="Tipo de Cambio (MXN/USD)" grid;
    title "Predicción del Tipo de Cambio MXN/USD a 10 días";
    title2 "Basado en Cadenas de Markov con Intervalos de Confianza";
run;
