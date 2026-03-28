# SdS_TP2_2026Q1GXXCSS_Presentación (texto final para copiar y pegar en PPT)

> Formato recomendado: 17 slides / 13 minutos.
> 
> Criterio aplicado: foco cuantitativo, pocas series temporales, observables bien definidos y conclusiones con alcance explícito.

---

## Slide 1 — Portada

**Texto:**

- TP2 – Autómata Off-Lattice (Vicsek) con partícula líder
- Simulación de Sistemas
- Grupo: 2026Q1GXX
- Comisión: SS
- Integrantes: [completar]
- Fecha: 30/03/2026

**Imagen:** no obligatoria (fondo neutro).

---

## Slide 2 — Agenda

**Texto:**

- Objetivo y modelo
- Implementación
- Resultados: (a), (b), (c), (d)
- Extensión opcional: (e)
- Conclusiones

**Imagen:** no obligatoria.

---

## Slide 3 — Motivación

**Texto:**

- Sistemas de agentes autopropulsados presentan transición orden–desorden.
- Se modela ese fenómeno en un sistema off-lattice.
- Caso de estudio: modelo de Vicsek con y sin líder.

**Imagen sugerida:** una imagen general de comportamiento colectivo (opcional).

---

## Slide 4 — Objetivo del trabajo

**Texto:**

- Implementar el modelo de Vicsek off-lattice.
- Estudiar el efecto del ruido angular η.
- Comparar tres escenarios:
  1. sin líder,
  2. líder fijo,
  3. líder circular.
- (Opcional) estudiar densidades ρ=2 y ρ=8.

---

## Slide 5 — Modelo y parámetros

**Texto:**

- Caja cuadrada: L=10.
- Contorno periódico.
- Densidad base: ρ=4 (N=ρ·L²=400).
- Radio de interacción: r0=1.
- Velocidad: v0=0.03.
- Ruido angular: η.

**Ecuación (texto):**

va(t) = (1 / (N·v0)) · |Σ vi(t)|

---

## Slide 6 — Escenarios simulados

**Texto:**

- **A) Sin líder:** dinámica estándar.
- **B) Líder fijo:** dirección constante (aleatoria al inicio).
- **C) Líder circular:** trayectoria circular prefijada, R=5.
- El líder influye al resto y no se actualiza por vecinos.

---

## Slide 7 — Observable y criterio de medición

**Texto:**

- Output primario: estado del sistema vs tiempo.
- Observables calculados off-line a partir del estado.
- Escalar estacionario:

<va> = (1 / Test) · Σ_{t=ts..tmax} va(t)

---

## Slide 8 — Implementación (arquitectura)

**Texto:**

- Simulación y análisis separados.
- Simulación: genera estado en texto.
- Post-proceso: calcula observables.
- Animación: módulo independiente (no embebida en PDF).

**Imagen sugerida:** diagrama simple de flujo (Simulación → TXT → Observables/Animación).

---

## Slide 9 — Pseudocódigo del loop temporal

**Texto (bloque breve):**

1. Buscar vecinos en r0.
2. Calcular dirección promedio local.
3. Agregar ruido en [-η/2, η/2].
4. Actualizar ángulos.
5. Mover partículas y aplicar contorno periódico.
6. Forzar dinámica de líder (si aplica).
7. Guardar estado.

---

## Slide 10 — (a) Animaciones características

**Texto:**

- Se muestran ejemplos cualitativos representativos.
- En el PDF final: links explícitos (sin animación embebida).

**Paths (usar capturas de estos GIF):**

- `a/vicsek_no_leader_no_legend.gif`
- `a/vicsek_line_fixed_slope.gif`
- `a/vicsek_anim.gif` (opcional)

---

## Slide 11 — (b) Evolución temporal característica

**Texto:**

- Se muestran solo curvas necesarias para definir el criterio estacionario.
- Ventana usada en el caso base: ts=175.
- Evitamos mostrar todas las series para no redundar.

**Imagen recomendada (1 sola):**

- `b/b_evolucion_temporal_va_none.png`

**Opcional (si entra bien):**

- `b/b_evolucion_temporal_va_fixed.png`
- `b/b_evolucion_temporal_va_circular.png`

---

## Slide 12 — (c) Curva <va> vs η (sin líder)

**Texto:**

- Al aumentar η, disminuye <va>.
- Se observa pérdida progresiva del orden colectivo.

**Imagen:**

- `c/c_va_vs_eta_none.png`

---

## Slide 13 — (c) Curva <va> vs η (líder fijo y circular)

**Texto:**

- Misma tendencia general en ambos escenarios.
- Diferencias presentes pero moderadas en este rango.

**Imágenes:**

- `c/c_va_vs_eta_fixed.png`
- `c/c_va_vs_eta_circular.png`

---

## Slide 14 — Tabla cuantitativa principal (ρ=4)

**Texto + tabla:**

| η | Sin líder | Líder fijo | Líder circular |
|---:|---:|---:|---:|
| 0.0 | 0.999992 | 0.993404 | 0.990745 |
| 0.6 | 0.980571 | 0.979298 | 0.974920 |
| 1.2 | 0.919554 | 0.917214 | 0.907833 |
| 1.8 | 0.823698 | 0.825872 | 0.819484 |
| 2.4 | 0.699765 | 0.691493 | 0.684623 |
| 3.0 | 0.547909 | 0.503566 | 0.537780 |

Frase final: “Resultados presentados en forma cuantitativa”.

---

## Slide 15 — (d) Comparación final entre escenarios

**Texto:**

- Comparación directa de los tres escenarios en una única figura.
- Las tres curvas decrecen con η.

**Imagen:**

- `d/d_comparacion_escenarios.png`

---

## Slide 16 — (e) Extensión opcional por densidad

**Texto:**

- Se repitió la comparación final para ρ=2 y ρ=8.
- La transición se vuelve más abrupta para mayor densidad.

**Imágenes:**

- `e/rho_2/d_comparacion_escenarios_rho_2.png`
- `e/rho_8/d_comparacion_escenarios_rho_8.png`

---

## Slide 17 — Análisis adicional (f): ángulo líder vs grupo

**Texto:**

- Se analiza la alineación entre la dirección del líder y la dirección promedio del sistema.
- Se reporta también la correlación angular temporal.
- Slide opcional para discusión (si hay tiempo).

**Imágenes (carpeta f):**

- `f/f_angulo_lider_vs_grupo_fixed.png`
- `f/f_correlacion_lider_sistema_fixed.png`
- `f/f_angulo_lider_vs_grupo_circular.png`
- `f/f_correlacion_lider_sistema_circular.png`

---

## Slide 18 — Conclusiones y cierre

**Texto:**

1. Se implementó el modelo de Vicsek off-lattice con análisis off-line.
2. <va> disminuye al aumentar η en los tres escenarios.
3. Las diferencias entre escenarios son cuantificables en el rango estudiado.
4. La densidad modifica la forma de la transición (extensión opcional).

**Línea de alcance (obligatoria):**

“Estas conclusiones valen para la resolución de valores de η estudiada.”

**Cierre:** Muchas gracias.

---

## Checklist final antes de exportar PDF

- Numeración visible en todas las diapositivas.
- Tamaños de fuente homogéneos (texto y figuras).
- Sin animaciones embebidas; usar links explícitos.
- Priorizar figuras y tablas por sobre texto descriptivo.
- Si una figura tiene paneles, describirlos en el caption general.
