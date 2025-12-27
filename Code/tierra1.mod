
#Conjunto de tareas de cada tierra

set TAREAS_1 ordered;

#Nombres de las variedades plantadas
set VARIEDADES_1;

#Numero de mesetas
set MESETAS;

#Horas disponibles para realizar el pedido

set HORAS;


#Horario disponible(cuando se les llama) del grupo de trabajo de cada tarea
set HORARIOS_1{TAREAS_1} within HORAS;


#Numero maximo de mesetas que puede realizar un grupo de trabajo
#de la tierra 1 en una hora


param maxmesetas1{TAREAS_1};

#Numero de mesetas donde se realizan las tareas de los grupos

#de trabajo de la tierra 1

param mesetasdisponibles; 

#Numero de personal total de cada tarea de la tierra 1


param personal1{TAREAS_1};

#Horas de trabajo de separacion (sacada del dato de dias) para quitar el riego
param crecimientovariedades{VARIEDADES_1};

set DISTRIBUCIONMESETAS_1{VARIEDADES_1} within MESETAS;

#Variable para linealizar

var delta1{i in TAREAS_1, k in MESETAS, l in HORARIOS_1[i]} binary;

#Variable que indica si el grupo de trabajo de la tarea i trabaja sobrea la meseta k
# en la hora l

var x1{i in TAREAS_1, k in MESETAS, l in HORARIOS_1[i]} binary;

#Variable que indica si el grupo de trabajo de la tarea i de la tierra 1 tiene alguna meseta todavia por 

#realizar(aunque no se pueda hacer en esa hora) en la hora l


var w1{i in TAREAS_1,l in HORARIOS_1[i]} binary;

# Funcion objetivo(minimizar las horas improductivas)

minimize horasimproductivas: 
    sum{i in TAREAS_1, l in HORARIOS_1[i]} 
        personal1[i]*(maxmesetas1[i]*w1[i,l] - sum{k in MESETAS} delta1[i,k,l])/ maxmesetas1[i];


# Restricciones de linealidad

s.t. lin1{i in TAREAS_1, k in MESETAS, l in HORARIOS_1[i]}: delta1[i,k,l]<= x1[i,k,l];

s.t. lin2{i in TAREAS_1, k in MESETAS, l in HORARIOS_1[i]}: delta1[i,k,l]<= w1[i,l];

s.t. lin3{i in TAREAS_1, k in MESETAS, l in HORARIOS_1[i]}: delta1[i,k,l]>= x1[i,k,l]+w1[i,l]-1;


# No se puede asignar en una hora mas mesetas de las posibles por el equipo de trabajo

s.t. asignacion_mesetas1{i in TAREAS_1, l in HORARIOS_1[i]}: sum{k in MESETAS} x1[i,k,l] <= maxmesetas1[i];

# Un equipo de trabajo actua una sola vez sobre una meseta

s.t. unica_asignacion1{i in TAREAS_1, k in MESETAS}: sum{l in HORARIOS_1[i]} x1[i,k,l]=1;

# Saber si un equipo de trabajo tiene labor restante
    
s.t. fin_contrato1{i in TAREAS_1, l in HORARIOS_1[i]}:
    (mesetasdisponibles-sum{h in HORARIOS_1[i], k in MESETAS: h < l} x1[i,k,h])/mesetasdisponibles <=w1[i,l]; 
    
    
# Las tareas respetan un orden
    
s.t. precedencia_entre_tareas1{i in TAREAS_1, k in MESETAS, l in HORARIOS_1[i]: i != first(TAREAS_1)}:
    x1[i,k,l] <= sum{h in HORARIOS_1[prev(i)]: h < l} x1[prev(i),k,h];
    

# Tenemos que tener el riego x horas desde que se puso para 

# poder quitarlo despues del crecimiento de la variedad (en la primera tierra lo determina quitar la malla, 

# y la segunda quitar el riego)
    
 s.t. crecimiento_variedades {q in VARIEDADES_1, k in DISTRIBUCIONMESETAS_1[q], l in HORARIOS_1['quitarmalla1']}:
    x1['quitarmalla1',k,l] <= 
        sum {h in HORARIOS_1['ponerriego1']: h <= l - crecimientovariedades[q]} x1['ponerriego1',k,h];


        
 
        
        