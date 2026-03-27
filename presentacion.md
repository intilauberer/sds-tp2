---
title: "Autómatas Celulares (Modelo de Vicsek)"
subtitle: "Trabajo Práctico Nro. 2"
author: "Grupo 2026Q1G03"
date: "30/03/2026"
theme: "Warsaw"
outertheme: "miniframes"
---

## Introducción / Sistema Real / Fundamentos

## 1. Introducción y Modelo

:::: {.columns}
::: {.column width="50%"}
- Caracterización de transición orden-desorden en agentes autopropulsados.
- Tres escenarios: sin líder, líder fijo y líder circular.
- Contorno periódico en ambas direcciones.
- Lado de la caja $L = 1 \times 10^1$.
:::
::: {.column width="50%"}
- Densidad base $\rho = 4 \times 10^0$.
- Cantidad de partículas $N = 4 \times 10^2$.
- Radio de interacción $r_0 = 1 \times 10^0$.
- Velocidad constante $v_0 = 3 \times 10^{-2}$.
- Ruido angular uniforme de amplitud $\eta$.
:::
::::

## Resultados

## 2.1 Animación: Sin líder

:::: {.columns}
::: {.column width="40%"}
- Escenario: Sin partícula líder.
- Parámetros fijos: $\rho = 4 \times 10^0$, $N = 4 \times 10^2$.
- Se evalúa la dinámica colectiva base.
- Vectores velocidad coloreados según ángulo.
:::
::: {.column width="60%"}
[Espacio para video: a/vicsek_no_leader_no_legend.gif]
:::
::::

## 2.2 Animación: Líder con dirección fija

:::: {.columns}
::: {.column width="40%"}
- Escenario: Líder con dirección constante en el tiempo.
- Dirección inicial elegida aleatoriamente.
- Parámetros fijos: $\rho = 4 \times 10^0$, $N = 4 \times 10^2$.
- Partícula líder identificada visualmente.
:::
::: {.column width="60%"}
[Espacio para video: a/vicsek_line_fixed_slope.gif]
:::
::::

## 2.3 Animación: Líder circular

:::: {.columns}
::: {.column width="40%"}
- Escenario: Líder con trayectoria circular.
- Radio de giro $R = 5 \times 10^0$.
- Velocidad tangencial comparable a $v_0$.
- Parámetros fijos: $\rho = 4 \times 10^0$, $N = 4 \times 10^2$.
:::
::: {.column width="60%"}
[Espacio para video: a/vicsek_anim.gif]
:::
::::

## 3.1 Evolución temporal: Sin líder

:::: {.columns}
::: {.column width="40%"}
- Observable: $v_a(t) = \frac{1}{N v_0}\left|\sum_{i=1}^{N}\mathbf{v}_i(t)\right|$.
- Escenario: Sin líder.
- Muestra transiente inicial y estabilización.
- Inicio de ventana estacionaria $t_s = 1.75 \times 10^2$.
:::
::: {.column width="60%"}
![](b/b_evolucion_temporal_va_none.png)
:::
::::

## 3.2 Evolución temporal: Líder con dirección fija

:::: {.columns}
::: {.column width="40%"}
- Observable: $v_a(t)$.
- Escenario: Líder con dirección fija.
- El ruido angular $\eta$ afecta la polarización final.
- Se calcula escalar estacionario $\langle v_a \rangle$.
:::
::: {.column width="60%"}
![](b/b_evolucion_temporal_va_fixed.png)
:::
::::

## 3.3 Evolución temporal: Líder circular

:::: {.columns}
::: {.column width="40%"}
- Observable: $v_a(t)$.
- Escenario: Líder circular.
- $\langle v_a\rangle = \frac{1}{T_{est}}\sum_{t=t_s}^{t_{max}}v_a(t)$.
- $t_s = 1.75 \times 10^2$ establecido a partir de estas curvas.
:::
::: {.column width="60%"}
![](b/b_evolucion_temporal_va_circular.png)
:::
::::

## 3.4 Comparación ruido: $\eta = 0.00$

:::: {.columns}
::: {.column width="40%"}
- Observable: $v_a(t)$.
- Ruido nulo: $\eta = 0 \times 10^0$.
- Polarización estacionaria $\langle v_a \rangle \approx 1 \times 10^0$ para los tres escenarios.
- Sistema altamente ordenado.
:::
::: {.column width="60%"}
![](b/b_evolucion_temporal_comparacion_eta_0.00.png)
:::
::::

## 3.5 Comparación ruido: $\eta = 1.80$

:::: {.columns}
::: {.column width="40%"}
- Observable: $v_a(t)$.
- Ruido intermedio: $\eta = 1.8 \times 10^0$.
- Descenso moderado de la polarización $\langle v_a \rangle \approx 8.2 \times 10^{-1}$.
- Comportamiento similar entre escenarios.
:::
::: {.column width="60%"}
![](b/b_evolucion_temporal_comparacion_eta_1.80.png)
:::
::::

## 3.6 Comparación ruido: $\eta = 3.00$

:::: {.columns}
::: {.column width="40%"}
- Observable: $v_a(t)$.
- Ruido alto: $\eta = 3 \times 10^0$.
- Caída significativa en el orden.
- Valores estacionarios cercanos a $5 \times 10^{-1}$.
:::
::: {.column width="60%"}
![](b/b_evolucion_temporal_comparacion_eta_3.00.png)
:::
::::

## 4.1 Curva $\langle v_a\rangle$ vs $\eta$: Sin líder

:::: {.columns}
::: {.column width="40%"}
- Observable estacionario $\langle v_a \rangle$ vs ruido $\eta$.
- Escenario: Sin líder.
- Parámetros fijos: $\rho = 4 \times 10^0$.
- Muestra barras de error asociadas a la media estacionaria.
:::
::: {.column width="60%"}
![](c/c_va_vs_eta_none.png)
:::
::::

## 4.2 Curva $\langle v_a\rangle$ vs $\eta$: Líder con dirección fija

:::: {.columns}
::: {.column width="40%"}
- Observable estacionario $\langle v_a \rangle$ vs ruido $\eta$.
- Escenario: Líder con dirección fija.
- Parámetros fijos: $\rho = 4 \times 10^0$.
- Transición gradual hacia el desorden.
:::
::: {.column width="60%"}
![](c/c_va_vs_eta_fixed.png)
:::
::::

## 4.3 Curva $\langle v_a\rangle$ vs $\eta$: Líder circular

:::: {.columns}
::: {.column width="40%"}
- Observable estacionario $\langle v_a \rangle$ vs ruido $\eta$.
- Escenario: Líder circular con $R = 5 \times 10^0$.
- Parámetros fijos: $\rho = 4 \times 10^0$.
- Caída de $\langle v_a\rangle$ al aumentar $\eta$.
:::
::: {.column width="60%"}
![](c/c_va_vs_eta_circular.png)
:::
::::

## 5. Comparación de Escenarios

:::: {.columns}
::: {.column width="40%"}
- Comparativa de $\langle v_a \rangle$ para los tres casos.
- Parámetros fijos: $\rho = 4 \times 10^0$.
- Decrecimiento progresivo del orden colectivo.
- Diferencias visibles pero moderadas entre escenarios en el rango estudiado.
:::
::: {.column width="60%"}
![](d/d_comparacion_escenarios.png)
:::
::::

## 6.1 Extensión Opcional: Animaciones $\rho = 2$

:::: {.columns}
::: {.column width="40%"}
- Densidad baja: $\rho = 2 \times 10^0$.
- Animaciones para $\eta = 5 \times 10^{-1}$ y $\eta = 3 \times 10^0$.
- Se evalúa impacto del ruido con menor interacción local.
:::
::: {.column width="60%"}
[Espacio para video: e/rho_2/animations/rho_2_eta_0p5.gif]

[Espacio para video: e/rho_2/animations/rho_2_eta_3.gif]
:::
::::

## 6.2 Extensión Opcional: Gráfico $\rho = 2$

:::: {.columns}
::: {.column width="40%"}
- Densidad $\rho = 2 \times 10^0$.
- Comparación de escenarios.
- Polarización estacionaria cae drásticamente a altos $\eta$ ($\approx 6 \times 10^{-2}$ para $\eta=6$).
:::
::: {.column width="60%"}
![](e/rho_2/d_comparacion_escenarios_rho_2.png)
:::
::::

## 6.3 Extensión Opcional: Animaciones $\rho = 8$

:::: {.columns}
::: {.column width="40%"}
- Densidad alta: $\rho = 8 \times 10^0$.
- Animaciones para $\eta = 5 \times 10^{-1}$ y $\eta = 3 \times 10^0$.
- Mayor densidad implica mayor conectividad entre agentes.
:::
::: {.column width="60%"}
[Espacio para video: e/rho_8/animations/rho_8_eta_0p5.gif]

[Espacio para video: e/rho_8/animations/rho_8_eta_3.gif]
:::
::::

## 6.4 Extensión Opcional: Gráfico $\rho = 8$

:::: {.columns}
::: {.column width="40%"}
- Densidad $\rho = 8 \times 10^0$.
- Comparación de escenarios.
- Al aumentar la densidad, la caída de $\langle v_a\rangle$ se vuelve más abrupta.
:::
::: {.column width="60%"}
![](e/rho_8/d_comparacion_escenarios_rho_8.png)
:::
::::

## 7.1 Análisis del Líder: Ángulos (Líder Fijo)

:::: {.columns}
::: {.column width="40%"}
- Evolución angular $\theta_L(t)$ vs $\theta_S(t)$.
- Escenario: Líder con dirección fija.
- Ángulo del líder se mantiene constante.
- Ángulo promedio del sistema trata de alinearse.
:::
::: {.column width="60%"}
![](f/f_angulo_lider_vs_grupo_fixed.png)
:::
::::

## 7.2 Análisis del Líder: Ángulos (Líder Circular)

:::: {.columns}
::: {.column width="40%"}
- Evolución angular $\theta_L(t)$ vs $\theta_S(t)$.
- Escenario: Líder circular.
- Ángulo del líder varía linealmente en el tiempo.
- El grupo sigue la oscilación del líder.
:::
::: {.column width="60%"}
![](f/f_angulo_lider_vs_grupo_circular.png)
:::
::::

## 7.3 Análisis del Líder: Correlación (Líder Fijo)

:::: {.columns}
::: {.column width="40%"}
- Correlación angular $C(t) = \cos(\theta_L - \theta_S)$.
- Escenario: Líder con dirección fija.
- Evalúa el acoplamiento direccional.
:::
::: {.column width="60%"}
![](f/f_correlacion_lider_sistema_fixed.png)
:::
::::

## 7.4 Análisis del Líder: Correlación (Líder Circular)

:::: {.columns}
::: {.column width="40%"}
- Correlación angular $C(t) = \cos(\theta_L - \theta_S)$.
- Escenario: Líder circular.
- Permite ver desfasaje entre el sistema y la rotación impuesta.
:::
::: {.column width="60%"}
![](f/f_correlacion_lider_sistema_circular.png)
:::
::::

## Conclusiones

## 8. Conclusiones

- En los tres escenarios, $\langle v_a\rangle$ decrece al aumentar $\eta$, evidenciando pérdida progresiva de orden colectivo.
- Para la densidad base de $\rho = 4 \times 10^0$, las diferencias entre escenarios (sin líder, líder fijo, líder circular) son visibles pero moderadas en el rango muestreado.
- En la extensión opcional, se observó que al aumentar la densidad poblacional, la caída de la polarización estacionaria $\langle v_a\rangle$ se vuelve más abrupta.
- Las observaciones aplican estrictamente para la resolución de valores de $\eta$ y repeticiones estudiadas.

## 

\begin{center}
\Huge Muchas Gracias
\end{center}