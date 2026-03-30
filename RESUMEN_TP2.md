---
title: "Resumen TP2 – Modelo de Vicsek Off-Lattice"
author: "Grupo 2026Q1G03"
date: "30/03/2026"
---

# Resumen Ejecutivo

## Objetivo
Caracterizar la transición orden–desorden en un sistema de agentes autopropulsados mediante el modelo de Vicsek, evaluando cómo cambia la dinámica colectiva al introducir un líder con movimiento prescripto.

## Sistema y Parámetros

**Configuración base:**
- Caja cuadrada de lado $L=10$ con contorno periódico
- Densidad: $\rho=4$ (400 partículas)
- Radio de interacción: $r_0=1$
- Velocidad constante: $v_0=0.03$
- Ruido angular uniforme: $\eta$ (parámetro de control)

**Tres escenarios estudiados:**
1. Sin líder
2. Líder con dirección fija
3. Líder circular ($R=5$)

## Observable Principal

$$v_a(t) = \frac{1}{N v_0}\left|\sum_{i=1}^{N}\mathbf{v}_i(t)\right|$$

Escalar estacionario:
$$\langle v_a\rangle = \frac{1}{T_{est}}\sum_{t=t_s}^{t_{max}}v_a(t)$$

**Interpretación:** $v_a$ mide polarización instantánea (orden colectivo). Valores cercanos a 1 indican partículas alineadas; cercanos a 0 indican desorden.

## Metodología

### Implementación
- Motor de simulación modular (Python)
- Salida primaria: estado del sistema en tiempo vs texto
- Observables procesados off-line
- Animaciones en módulo separado

### Ventana estacionaria
- Simulación: $t_{max} = 500$ pasos
- Transiente ignorado: primeros 175 pasos
- Promedio estacionario: $t \in [175, 500]$
- Repeticiones: 2 corridas independientes por punto

## Resultados Principales

### 1. Evolución Temporal ($\rho=4$)

Para todos los escenarios se observa:
- **Transitorio inicial:** sistema alcanza estado estacionario
- **Efecto del ruido:** aumentar $\eta$ reduce $v_a(t)$ estacionario
- **Influencia de líderes:** mantienen orden ligeramente superior

### 2. Curvas Input-Output: $\langle v_a\rangle$ vs $\eta$

| Escenario | Comportamiento |
|-----------|----------------|
| Sin líder | Caída progresiva desde ~1 a ~0.5 |
| Líder fijo | Caída similar, valores levemente superiores |
| Líder circular | Caída con oscilaciones dinámicas |

**Conclusión:** Los líderes ayudan a mantener orden, pero diferencias son moderadas en rango estudiado.

### 3. Extensión de Densidades

**$\rho=2$ (baja densidad):**
- Transición más abrupta al desorden
- Menor interacción local → orden frágil

**$\rho=8$ (alta densidad):**
- Transición más gradual
- Mayor interacción → orden más robusto

## Análisis Adicional: Correlación Líder-Grupo

Para líderes (fijo y circular):
- Ángulos del líder ($\theta_L$) vs grupo ($\theta_S$)
- Correlación: $C(t) = \cos(\theta_L - \theta_S)$
- **Observación:** Correlación disminuye con tiempo al aumentar $\eta$ → pérdida de influencia del líder

## Conclusiones

1. **Implementación exitosa:** Modelo modular, separación clara simulación/animación
2. **Transición orden-desorden:** Confirmada en todos escenarios; ruido es mecanismo clave
3. **Rol del líder:** Mantiene orden colectivo pero efecto moderado en rango estudiado
4. **Efecto de densidad:** Crítico para robustez de orden colectivo
5. **Ventana estacionaria:** $t_s=175$ suficiente para convergencia

## Limitaciones y Extensiones

**Limitaciones:**
- Solo 2 corridas por punto (estadística limitada)
- Malla gruesa de $\eta$ (pasos de 0.6)
- No hay análisis de tamaño finito

**Trabajo futuro:**
- Aumentar corridas (estadística)
- Refinar malla cerca de transición
- Análisis de punto crítico
- Estudiar otros observables (aglomeración, velocidades locales)

## Archivos Entregables

- `vicsek.py`: Motor de simulación
- `animate_vicsek.py`: Animaciones
- `tp2_bcd.py`: Barrido principal
- `tp2_e_extra_densities.py`: Extensión densidades
- `presentacion.pdf`: Slides para exposición
- `SdS_TP2_2026Q1G03CS_Informe.pdf`: Informe completo con gráficos

## Puntos Clave para la Exposición Oral

1. **Motivación:** Transiciones de fase en sistemas de partículas autopropulsadas
2. **Modelo:** Regla local (promedio de vecinos) → comportamiento colectivo emergente
3. **Hallazgo principal:** Ruido destruye orden; densidad lo protege
4. **Innovación:** Análisis de influencia de líder en sistema colectivo
5. **Relevancia:** Aplicación a bandadas, enjambres, células motiles

---

**Grupo:** Felipe Mindlin (62774), Federico Inti García Lauberer (61374), Matias Sapino (61067)  
**Materia:** Simulación de Sistemas | **Fecha:** 30/03/2026
