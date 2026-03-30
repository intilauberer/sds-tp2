---
title: "SdS_TP2_2026Q1G03CS_Informe"
author:
  - "Grupo 2026Q1G03"
date: "30/03/2026"
lang: es
geometry: margin=2.5cm
fontsize: 11pt
header-includes:
  - \usepackage{float}
  - \usepackage{graphicx}
  - \usepackage{hyperref}
---

**Materia:** Simulación de Sistemas  
**Trabajo Práctico:** TP2 – Autómata Off-Lattice (Vicsek)  
**Comisión:** S  
**Integrantes:** Felipe Mindlin 62774 - Federico Inti García Lauberer 61374 - Matias Sapino 61067

## Resumen

Se implementó el modelo de Vicsek off-lattice en una caja cuadrada con contorno periódico y se estudió su comportamiento en función del ruido angular $\eta$. Se consideraron tres escenarios: sin líder, líder con dirección fija y líder con trayectoria circular. El output primario de la simulación es el estado del sistema en el tiempo, y los observables se calcularon off-line. El observable central fue la polarización $v_a(t)$, a partir de la cual se obtuvo el escalar estacionario $\langle v_a \rangle$ para construir curvas input–output con barras de error. También se incluyó una extensión opcional para densidades $\rho=2$ y $\rho=8$.

## 1. Introducción

Este trabajo busca caracterizar la transición orden–desorden en un sistema de agentes autopropulsados según el modelo de Vicsek [1], y evaluar cómo cambia la dinámica colectiva al introducir una partícula líder de movimiento prescripto.

Se analizaron los tres escenarios pedidos:

1. **Sin líder**.
2. **Líder con dirección fija** (constante en el tiempo, elegida aleatoriamente al inicio).
3. **Líder circular** (radio $R=5$ y velocidad tangencial comparable con la del resto).

## 2. Modelo y definición de observables

### 2.1. Parámetros del sistema

- Lado de la caja: $L=10$.
- Contorno periódico en ambas direcciones.
- Densidad base: $\rho=4$ ($N=\rho L^2=400$).
- Radio de interacción: $r_0=1$.
- Velocidad constante: $v_0=0.03$.
- Ruido angular uniforme de amplitud $\eta$.

### 2.2. Output primario y observables

Siguiendo el enunciado, **el único output primario** es el estado del sistema vs tiempo:

$$
S(t)=\{x_i(t),y_i(t),\theta_i(t)\}_{i=1}^{N}.
$$

Ese estado se guarda en texto y luego se procesa off-line para calcular observables. El observable primario utilizado fue:

$$
v_a(t)=\frac{1}{N v_0}\left|\sum_{i=1}^{N}\vec v_i(t)\right|.
$$

Para cada valor de $\eta$ se define el escalar estacionario:

$$
\langle v_a\rangle=\frac{1}{T_{est}}\sum_{t=t_s}^{t_{max}}v_a(t),
$$

donde $t_s$ es el inicio de la ventana estacionaria.

## 3. Implementación

La implementación quedó separada en módulos:

- Simulación: [vicsek.py](vicsek.py)
- Animación: [animate_vicsek.py](animate_vicsek.py)
- Barrido para ítems (b), (c), (d): [tp2_bcd.py](tp2_bcd.py)
- Extensión opcional de densidades: [tp2_e_extra_densities.py](tp2_e_extra_densities.py)

### 3.1. Pseudocódigo del loop temporal

```text
Inicializar partículas (x_i, y_i, theta_i)
Para t = 0 ... t_max:
    Para cada partícula i:
        Buscar vecinos en radio r0 (con mínimo imagen periódico)
        Calcular dirección promedio local
        Agregar ruido uniforme en [-eta/2, eta/2]
        Guardar nuevo ángulo de i

    Actualizar todos los ángulos
    Mover partículas con velocidad v0
    Aplicar contorno periódico

    Si hay líder externo:
        Forzar su dinámica (fijo o circular)

    Guardar estado del sistema en archivo de texto
Fin
```

### 3.2. Separación simulación/animación

La simulación produce archivos de estado y, en una etapa posterior, el módulo de animación toma esos archivos para construir GIF/MP4. Esta separación evita que la velocidad de visualización dependa del costo de cómputo.

## 4. Resultados

### 4.1. Animaciones características

Se generaron animaciones con vectores velocidad coloreados por ángulo y líder identificado. En PDF no se embebe animación: se incluyen links a los archivos.

- Sin líder: [https://www.youtube.com/shorts/XXkGn0btGuo](https://www.youtube.com/shorts/XXkGn0btGuo)
- Líder fijo: [https://www.youtube.com/shorts/0Son8c38P_s](https://www.youtube.com/shorts/0Son8c38P_s)
- Líder circular: [https://www.youtube.com/shorts/7ZK-rAYKzTA](https://www.youtube.com/shorts/7ZK-rAYKzTA)

### 4.2. Evolución temporal de $v_a(t)$ y criterio estacionario

Se muestran **solo evoluciones temporales características**, suficientes para justificar la definición del observable escalar (evitando redundancia de curvas).

\begin{figure}[H]
\centering
\includegraphics[width=0.75\textwidth]{b/b_evolucion_temporal_va_none.png}
\caption{Evolución temporal de $v_a(t)$ para escenario sin líder, con tres niveles de ruido representativos.}
\end{figure}

Esta gráfica muestra la evolución temporal de la polarización $v_a(t)$ en el escenario sin líder para tres valores representativos de ruido $\eta$. Se observa un transitorio inicial seguido de un estado estacionario, donde valores más altos de ruido conducen a una polarización más baja, indicando pérdida de orden colectivo.

\begin{figure}[H]
\centering
\includegraphics[width=0.75\textwidth]{b/b_evolucion_temporal_va_fixed.png}
\caption{Evolución temporal de $v_a(t)$ para líder fijo.}
\end{figure}

Esta gráfica presenta la evolución temporal de la polarización $v_a(t)$ en el escenario con líder de dirección fija. Se aprecia cómo el sistema alcanza rápidamente un estado ordenado influenciado por el líder, con el ruido afectando la estabilidad del orden colectivo a lo largo del tiempo.

\begin{figure}[H]
\centering
\includegraphics[width=0.75\textwidth]{b/b_evolucion_temporal_va_circular.png}
\caption{Evolución temporal de $v_a(t)$ para líder circular.}
\end{figure}

Esta gráfica ilustra la evolución temporal de la polarización $v_a(t)$ en el escenario con líder en trayectoria circular. Se observa una dinámica oscilante influida por el movimiento del líder, con el ruido introduciendo fluctuaciones que afectan el mantenimiento del orden colectivo.

\begin{figure}[H]
\centering
\includegraphics[width=0.75\textwidth]{b/b_evolucion_temporal_comparacion_eta_0.00.png}
\caption{Comparación temporal característica para $\eta$ = 0.00.}
\end{figure}

Esta gráfica compara la evolución temporal de $v_a(t)$ para los tres escenarios (sin líder, líder fijo y líder circular) con ruido nulo ($\eta = 0.00$). Se ve que en ausencia de ruido, todos los escenarios alcanzan una polarización casi perfecta, con el líder circular mostrando una ligera oscilación debido a su movimiento.

\begin{figure}[H]
\centering
\includegraphics[width=0.75\textwidth]{b/b_evolucion_temporal_comparacion_eta_1.80.png}
\caption{Comparación temporal para $\eta$ = 1.80.}
\end{figure}

Esta gráfica compara la evolución temporal de $v_a(t)$ para los tres escenarios con ruido intermedio ($\eta = 1.80$). Se observa una disminución moderada en la polarización estacionaria, con el escenario sin líder mostrando la mayor variabilidad y los líderes ayudando a mantener un orden relativo.

\begin{figure}[H]
\centering
\includegraphics[width=0.75\textwidth]{b/b_evolucion_temporal_comparacion_eta_3.00.png}
\caption{Comparación temporal para $\eta$ = 3.00.}
\end{figure}

Esta gráfica compara la evolución temporal de $v_a(t)$ para los tres escenarios con alto ruido ($\eta = 3.00$). Se aprecia una caída significativa en el orden colectivo, con polarizaciones estacionarias cercanas a 0.5, indicando una transición hacia el desorden, aunque los líderes aún ejercen una influencia moderada.

Con base en estas curvas se tomó, para el barrido principal ($\rho=4$), ventana estacionaria desde $t_s=175$.

### 4.3. Curvas $\langle v_a\rangle$ vs $\eta$ con barras de error

\begin{figure}[H]
\centering
\includegraphics[width=0.75\textwidth]{c/c_va_vs_eta_none.png}
\caption{Curva input–output para escenario sin líder.}
\end{figure}

Esta gráfica muestra la polarización estacionaria media $\langle v_a \rangle$ en función del ruido $\eta$ para el escenario sin líder, con barras de error. Se observa una transición gradual desde orden perfecto ($\langle v_a \rangle \approx 1$) hacia desorden ($\langle v_a \rangle \approx 0.5$) al aumentar el ruido.

\begin{figure}[H]
\centering
\includegraphics[width=0.75\textwidth]{c/c_va_vs_eta_fixed.png}
\caption{Curva input–output para líder fijo.}
\end{figure}

Esta gráfica presenta la polarización estacionaria media $\langle v_a \rangle$ versus ruido $\eta$ para el líder fijo, incluyendo barras de error. Se ve una caída progresiva del orden al aumentar $\eta$, con el líder ayudando a mantener valores más altos de polarización comparado con el caso sin líder.

\begin{figure}[H]
\centering
\includegraphics[width=0.75\textwidth]{c/c_va_vs_eta_circular.png}
\caption{Curva input–output para líder circular.}
\end{figure}

Esta gráfica ilustra la polarización estacionaria media $\langle v_a \rangle$ en función del ruido $\eta$ para el líder circular, con barras de error. Se observa una disminución del orden colectivo con el ruido, similar a los otros escenarios, pero con el líder circular proporcionando una influencia dinámica que afecta la estabilidad.

### 4.4. Comparación entre los tres escenarios

\begin{figure}[H]
\centering
\includegraphics[width=0.75\textwidth]{d/d_comparacion_escenarios.png}
\caption{Comparación final solicitada en el enunciado (sin líder, líder fijo y líder circular).}
\end{figure}

Esta gráfica compara las curvas de polarización estacionaria $\langle v_a \rangle$ versus $\eta$ para los tres escenarios estudiados. Se aprecia que los líderes (fijo y circular) mantienen un orden ligeramente superior al caso sin líder, especialmente en rangos intermedios de ruido, aunque las diferencias son poco significativas.

Se observa la caída de $\langle v_a\rangle$ al aumentar $\eta$ en los tres casos, con diferencias poco significativas entre escenarios en el rango estudiado.

### 4.5. Extensión opcional: densidades $\rho=2$ y $\rho=8$

\begin{figure}[H]
\centering
\includegraphics[width=0.75\textwidth]{e/rho_2/d_comparacion_escenarios_rho_2.png}
\caption{Curva comparativa (estilo ítem d) para $\rho=2$.}
\end{figure}

Esta gráfica muestra la comparación de $\langle v_a \rangle$ versus $\eta$ para los tres escenarios con densidad baja ($\rho=2$). Se observa una transición más abrupta hacia el desorden al aumentar el ruido, debido a la menor interacción local entre partículas.

\begin{figure}[H]
\centering
\includegraphics[width=0.75\textwidth]{e/rho_8/d_comparacion_escenarios_rho_8.png}
\caption{Curva comparativa (estilo ítem d) para $\rho=8$.}
\end{figure}

Esta gráfica presenta la comparación de $\langle v_a \rangle$ versus $\eta$ para los tres escenarios con densidad alta ($\rho=8$). Se ve que el orden se mantiene por más tiempo al aumentar el ruido, gracias a las interacciones más frecuentes, pero eventualmente cae hacia el desorden.

Animaciones opcionales (máximo dos por densidad):

- $\rho=2$: ruido bajo ($\eta = 0.5$) - [https://www.youtube.com/shorts/FrsD14uzri8](https://www.youtube.com/shorts/FrsD14uzri8)
- $\rho=2$: ruido alto ($\eta = 3.0$) - [https://www.youtube.com/shorts/y4YApFvEP-k](https://www.youtube.com/shorts/y4YApFvEP-k)
- $\rho=8$: ruido bajo ($\eta = 0.5$) - [https://www.youtube.com/shorts/FrsD14uzri8](https://www.youtube.com/shorts/FrsD14uzri8)
- $\rho=8$: ruido alto ($\eta = 3.0$) - [https://www.youtube.com/shorts/y4YApFvEP-k](https://www.youtube.com/shorts/y4YApFvEP-k)

### 4.6. Análisis adicional: ángulo líder–grupo

\begin{figure}[H]
\centering
\includegraphics[width=0.75\textwidth]{f/f_angulo_lider_vs_grupo_fixed.png}
\caption{Evolución angular $\theta_L(t)$ y $\theta_S(t)$ para líder fijo.}
\end{figure}

Esta gráfica muestra la evolución temporal de los ángulos del líder ($\theta_L$) y del grupo ($\theta_S$) para el líder fijo. Se observa cómo el grupo sigue al líder inicialmente, pero el ruido introduce desviaciones que afectan la correlación angular a lo largo del tiempo.

\begin{figure}[H]
\centering
\includegraphics[width=0.75\textwidth]{f/f_correlacion_lider_sistema_fixed.png}
\caption{Correlación angular $C(t)=\cos(\theta_L-\theta_S)$ para líder fijo.}
\end{figure}

Esta gráfica ilustra la correlación angular $C(t)$ entre el líder y el grupo para el líder fijo. Se aprecia cómo la correlación disminuye con el tiempo debido al ruido, indicando una pérdida progresiva de influencia del líder sobre el colectivo.

\begin{figure}[H]
\centering
\includegraphics[width=0.75\textwidth]{f/f_angulo_lider_vs_grupo_circular.png}
\caption{Evolución angular $\theta_L(t)$ y $\theta_S(t)$ para líder circular.}
\end{figure}

Esta gráfica muestra la evolución temporal de los ángulos del líder ($\theta_L$) y del grupo ($\theta_S$) para el líder circular. Se observa el movimiento oscilante del líder y cómo el grupo intenta seguirlo, con el ruido causando fluctuaciones en la alineación colectiva.

\begin{figure}[H]
\centering
\includegraphics[width=0.75\textwidth]{f/f_correlacion_lider_sistema_circular.png}
\caption{Correlación angular $C(t)$ para líder circular.}
\end{figure}

Esta gráfica presenta la correlación angular $C(t)$ entre el líder circular y el grupo. Se ve una correlación que varía con el tiempo debido al movimiento dinámico del líder, con el ruido reduciendo la efectividad de la influencia del líder en el colectivo.

## 5. Conclusiones

1. Se implementó el modelo de Vicsek off-lattice con salida de estado en texto y animación en módulo separado.
2. En los tres escenarios, $\langle v_a\rangle$ decrece al aumentar $\eta$, evidenciando pérdida progresiva de orden colectivo.
3. Para $\rho=4$, las diferencias entre escenarios son visibles pero moderadas en el rango de ruido muestreado, con líderes ayudando a mantener mayor orden.
4. En la extensión opcional, para $\rho=2$ la transición al desorden es más abrupta que para $\rho=4$, mientras que para $\rho=8$ es más gradual.

**Alcance:** estas conclusiones aplican **para la resolución de valores de $\eta$ estudiada** y el número de corridas utilizado. Un barrido más fino alrededor de la zona de transición podría cambiar la estimación precisa del punto crítico.

## 6. Limitaciones y trabajo futuro

- Aumentar cantidad de corridas por cada valor de $\eta$.
- Refinar malla de $\eta$ cerca de la transición.
- Agregar análisis de tamaño finito de forma sistemática.

## 7. Reproducibilidad

Scripts principales:

- [vicsek.py](vicsek.py)
- [animate_vicsek.py](animate_vicsek.py)
- [tp2_bcd.py](tp2_bcd.py)
- [tp2_e_extra_densities.py](tp2_e_extra_densities.py)

Las tablas numéricas principales se incluyen directamente en este informe para que el documento sea autocontenido.

## Referencias

[1] T. Vicsek, A. Czirók, E. Ben-Jacob, I. Cohen, O. Shochet, *Novel Type of Phase Transition in a System of Self-Driven Particles*, Physical Review Letters 75, 1226–1229 (1995).
