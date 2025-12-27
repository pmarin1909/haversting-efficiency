
#Conjunto de tareas de cada tierra

set TAREAS_2 ordered;

#Nombres de las variedades plantadas
set VARIEDADES_2;

#Numero de mesetas
set MESETAS;

#Horas disponibles para realizar el pedido

set HORAS;

#Horario disponible(cuando se les llama) del grupo de trabajo de cada tarea
set HORARIOS_2{TAREAS_2} within HORAS;


#Numero maximo de mesetas que puede realizar un grupo de trabajo
#de la tierra 2 en 1 hora


param maxmesetas2{TAREAS_2};

#Numero de mesetas donde se realizan las tareas de los grupos

#de trabajo de la tierra 2

param mesetasdisponibles; 

#Numero de personal total de cada tarea de la tierra 2


param personal2{TAREAS_2};

#Horas de trabajo de separacion (sacada del dato de dias) para quitar el riego
param crecimientovariedades{VARIEDADES_2};
set DISTRIBUCIONMESETAS_2{VARIEDADES_2} within MESETAS;

#Variable para linealizar

var delta2{i in TAREAS_2, k in MESETAS, l in HORARIOS_2[i]} binary;

#Variable que indica si el grupo de trabajo de la tarea i trabaja sobrea la meseta k
# en la hora l



var x2{i in TAREAS_2, k in MESETAS, l in HORARIOS_2[i]} binary;

#Variable que indica si el grupo de trabajo de la tarea i de la tierra 2 tiene alguna meseta todavia por 

#realizar(aunque no se pueda hacer en esa hora) en la hora l


var w2{i in TAREAS_2,l in HORARIOS_2[i]} binary;

# Funcion objetivo(minimizar las horas improductivas)

minimize horasimproductivas: 
    sum{i in TAREAS_2, l in HORARIOS_2[i]} 
        personal2[i]*(maxmesetas2[i]*w2[i,l] - sum{k in MESETAS} delta2[i,k,l])/ maxmesetas2[i];


#Restricciones para linealidad

s.t. lin1{i in TAREAS_2, k in MESETAS, l in HORARIOS_2[i]}: delta2[i,k,l]<= x2[i,k,l];

s.t. lin2{i in TAREAS_2, k in MESETAS, l in HORARIOS_2[i]}: delta2[i,k,l]<= w2[i,l];

s.t. lin3{i in TAREAS_2, k in MESETAS, l in HORARIOS_2[i]}: delta2[i,k,l]>= x2[i,k,l]+w2[i,l]-1;




# No se puede asignar en una hora mas mesetas de las posibles por el equipo de trabajo

s.t. asignacion_mesetas2{i in TAREAS_2, l in HORARIOS_2[i]}: sum{k in MESETAS} x2[i,k,l] <= maxmesetas2[i];

# Un equipo de trabajo actua una sola vez sobre una meseta

s.t. unica_asignacion2{i in TAREAS_2, k in MESETAS}: sum{l in HORARIOS_2[i]} x2[i,k,l]=1;

# Saber si un equipo de trabajo tiene labor restante
    
s.t. fin_contrato2{i in TAREAS_2, l in HORARIOS_2[i]}:
    (mesetasdisponibles-sum{h in HORARIOS_2[i], k in MESETAS: h < l} x2[i,k,h])/mesetasdisponibles <=w2[i,l]; 
    
    
# Las tareas respetan un orden
    
s.t. precedencia_entre_tareas2{i in TAREAS_2, k in MESETAS, l in HORARIOS_2[i]: i != first(TAREAS_2)}:
    x2[i,k,l] <= sum{h in HORARIOS_2[prev(i)]: h < l} x2[prev(i),k,h];
    

# Tenemos que tener el riego x horas desde que se puso para 

# poder quitarlo despues del crecimiento de la variedad (en la primera tierra lo determina quitar la malla, 

# y la segunda quitar el riego)
    
 s.t. crecimiento_variedades {q in VARIEDADES_2, k in DISTRIBUCIONMESETAS_2[q], l in HORARIOS_2['quitarriego2']}:
    x2['quitarriego2',k,l] <=
        sum {h in HORARIOS_2['ponerriego2']: h <= l - crecimientovariedades[q]} x2['ponerriego2',k,h];

            
        
        