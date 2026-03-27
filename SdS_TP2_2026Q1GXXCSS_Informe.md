---
title: "Simulación de Sistemas TP2 Informe"
author:
  - "Grupo 2026Q1G03"
date: "30/03/2026"
lang: es
geometry: margin=2.5cm
fontsize: 11pt
header-includes: |
  \usepackage{float}
  \floatplacement{figure}{H}
---

**Materia:** Simulación de Sistemas  
**Trabajo Práctico:** TP2 – Autómata Off-Lattice (Vicsek)  
**Comisión:** S  
**Integrantes:**  Federico Inti Garcia Lauberer, Felipe Mindlin, Matias Sapino

## Resumen

Se implementó el modelo de Vicsek off-lattice en una caja cuadrada con contorno periódico y se estudió su comportamiento en función del ruido angular $\eta$. Se consideraron tres escenarios: sin líder, líder con dirección fija y líder con trayectoria circular. El output primario de la simulación es el estado del sistema en el tiempo, y los observables se calcularon off-line. El observable central fue la polarización $v_a(t)$, a partir de la cual se obtuvo el escalar estacionario $\langle v_a \rangle$ para construir curvas input–output con barras de error. También se incluyó una extensión opcional para densidades $\rho=2$ y $\rho=8$.

## 1. Introducción

Este trabajo busca caracterizar la transición orden–desorden en un sistema de agentes autopropulsados según el modelo de Vicsek [1], y evaluar cómo cambia la dinámica colectiva al introducir una partícula líder de movimiento prescripto.

Se analizaron los tres escenarios pedidos:

1. **A) Sin líder**.
2. **B) Líder con dirección fija** (constante en el tiempo, elegida aleatoriamente al inicio).
3. **C) Líder circular** (radio $R=5$ y velocidad tangencial comparable con la del resto).

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

### 4.1. (a) Animaciones características

Se generaron animaciones con vectores velocidad coloreados por ángulo y líder identificado.

- Sin líder: [a/vicsek_no_leader_no_legend.gif](a/vicsek_no_leader_no_legend.gif)
- Líder fijo: [a/vicsek_line_fixed_slope.gif](a/vicsek_line_fixed_slope.gif)
- Líder circular: [a/vicsek_anim.gif](a/vicsek_anim.gif)

### 4.2. (b) Evolución temporal de $v_a(t)$ y criterio estacionario

Se muestran **solo evoluciones temporales características**, suficientes para justificar la definición del observable escalar (evitando redundancia de curvas).

![Evolución temporal de $v_a(t)$ para escenario sin líder, con tres niveles de ruido.](b/b_evolucion_temporal_va_none.png)

![Evolución temporal de $v_a(t)$ para líder fijo, con tres niveles de ruido.](b/b_evolucion_temporal_va_fixed.png)

![Evolución temporal de $v_a(t)$ para líder circular, con tres niveles de ruido.](b/b_evolucion_temporal_va_circular.png)

Con base en estas curvas se tomó, para el barrido principal ($\rho=4$), ventana estacionaria desde $t_s=175$.

### 4.3. (c) Curvas $\langle v_a\rangle$ vs $\eta$ con barras de error

![Curva $\langle v_a\rangle$ vs $\eta$ para escenario sin líder.](c/c_va_vs_eta_none.png)

![Curva $\langle v_a\rangle$ vs $\eta$ para líder fijo.](c/c_va_vs_eta_fixed.png)

![Curva $\langle v_a\rangle$ vs $\eta$ para líder circular.](c/c_va_vs_eta_circular.png)

Tabla resumen (media estacionaria para $\rho=4$):

| $\eta$ | Sin líder | Líder fijo | Líder circular |
|---:|---:|---:|---:|
| 0.0 | 0.999992 | 0.993404 | 0.990745 |
| 0.6 | 0.980571 | 0.979298 | 0.974920 |
| 1.2 | 0.919554 | 0.917214 | 0.907833 |
| 1.8 | 0.823698 | 0.825872 | 0.819484 |
| 2.4 | 0.699765 | 0.691493 | 0.684623 |
| 3.0 | 0.547909 | 0.503566 | 0.537780 |

### 4.4. (d) Comparación entre los tres escenarios

![Comparación de $\langle v_a\rangle$ vs $\eta$ para los tres escenarios.](d/d_comparacion_escenarios.png)

Se observa la caída de $\langle v_a\rangle$ al aumentar $\eta$ en los tres casos, con diferencias moderadas entre escenarios en el rango estudiado.

### 4.5. (e) Extensión opcional: densidades $\rho=2$ y $\rho=8$

![Comparación de escenarios para $\rho=2$.](e/rho_2/d_comparacion_escenarios_rho_2.png)

![Comparación de escenarios para $\rho=8$.](e/rho_8/d_comparacion_escenarios_rho_8.png)

Tabla resumen para $\rho=2$ (media estacionaria):

| $\eta$ | Sin líder | Líder fijo | Líder circular |
|---:|---:|---:|---:|
| 0.0 | 0.998449 | 0.989526 | 0.973122 |
| 1.0 | 0.922300 | 0.904556 | 0.878453 |
| 2.0 | 0.699049 | 0.726926 | 0.723140 |
| 3.0 | 0.360621 | 0.402488 | 0.408894 |
| 4.0 | 0.122653 | 0.144425 | 0.146293 |
| 5.0 | 0.070730 | 0.071998 | 0.071380 |
| 6.0 | 0.064133 | 0.064287 | 0.059829 |

Tabla resumen para $\rho=8$ (media estacionaria):

| $\eta$ | Sin líder | Líder fijo | Líder circular |
|---:|---:|---:|---:|
| 0.0 | 1.000000 | 0.998207 | 0.998568 |
| 1.0 | 0.953172 | 0.951430 | 0.949893 |
| 2.0 | 0.819063 | 0.818305 | 0.806503 |
| 3.0 | 0.611249 | 0.599599 | 0.613283 |
| 4.0 | 0.365345 | 0.329206 | 0.356612 |
| 5.0 | 0.060128 | 0.058080 | 0.056134 |
| 6.0 | 0.031996 | 0.032418 | 0.032480 |

Animaciones opcionales (máximo dos por densidad):

- $\rho=2$: [e/rho_2/animations/rho_2_eta_0p5.gif](e/rho_2/animations/rho_2_eta_0p5.gif), [e/rho_2/animations/rho_2_eta_3.gif](e/rho_2/animations/rho_2_eta_3.gif)
- $\rho=8$: [e/rho_8/animations/rho_8_eta_0p5.gif](e/rho_8/animations/rho_8_eta_0p5.gif), [e/rho_8/animations/rho_8_eta_3.gif](e/rho_8/animations/rho_8_eta_3.gif)

### 4.6. Análisis adicional: ángulo líder–grupo

![Evolución angular $\theta_L(t)$ y $\theta_S(t)$ para líder fijo.](f/f_angulo_lider_vs_grupo_fixed.png)

![Correlación angular $C(t)=\cos(\theta_L-\theta_S)$ para líder fijo.](f/f_correlacion_lider_sistema_fixed.png)

![Evolución angular $\theta_L(t)$ y $\theta_S(t)$ para líder circular.](f/f_angulo_lider_vs_grupo_circular.png)

![Correlación angular $C(t)$ para líder circular.](f/f_correlacion_lider_sistema_circular.png)

## 5. Conclusiones

1. Se implementó el modelo de Vicsek off-lattice con salida de estado en texto y animación en módulo separado.
2. En los tres escenarios, $\langle v_a\rangle$ decrece al aumentar $\eta$, evidenciando pérdida progresiva de orden colectivo.
3. Para $\rho=4$, las diferencias entre escenarios son visibles pero moderadas en el rango de ruido muestreado.
4. En la extensión opcional, al aumentar la densidad la caída de $\langle v_a\rangle$ se vuelve más abrupta.

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
