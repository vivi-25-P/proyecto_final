# Guía del Dashboard de Segmentación de Clientes

Esta guía explica cómo funciona `dashboard.py`, qué muestra cada pestaña y cómo interpretar los resultados actuales del proyecto.

> Las cifras de esta guía corresponden a la última ejecución del notebook (`resultados/rfm_segmented.csv` y `resultados/cluster_metrics.csv`). Si vuelves a ejecutar el notebook, las métricas del Autoencoder pueden variar (ver la pestaña [Métricas](#4-pestaña--métricas)).

---

## Índice

1. [Cómo iniciar el dashboard](#cómo-iniciar-el-dashboard)
2. [Conceptos clave: RFM y segmentos](#conceptos-clave-rfm-y-segmentos)
3. [Barra lateral de filtros](#barra-lateral-de-filtros)
4. [Indicadores principales (KPIs)](#indicadores-principales-kpis)
5. [Pestaña 📊 Visión General](#1-pestaña--visión-general)
6. [Pestaña 🗺️ Mapa de Clusters](#2-pestaña-️-mapa-de-clusters)
7. [Pestaña 👤 Perfilamiento](#3-pestaña--perfilamiento)
8. [Pestaña 📈 Métricas](#4-pestaña--métricas)
9. [Pestaña 💡 Recomendaciones](#5-pestaña--recomendaciones)
10. [Qué filtros afectan a cada pestaña](#qué-filtros-afectan-a-cada-pestaña)
11. [Limitaciones a tener en cuenta](#limitaciones-a-tener-en-cuenta)

---

## Cómo iniciar el dashboard

1. Ejecuta primero el notebook `customer_segmentation.ipynb`; genera los archivos que el dashboard necesita:
   - `resultados/rfm_segmented.csv` — un registro por cliente con sus variables RFM, clusters, coordenadas PCA/t-SNE, segmento y país.
   - `resultados/cluster_metrics.csv` — métricas de validación de los 4 modelos de clustering.
2. Desde la raíz del proyecto:

   ```powershell
   .\.venv\Scripts\python.exe dashboard.py
   ```

3. Abre `http://127.0.0.1:8050` en el navegador.

> Dash carga los datos y el código **una sola vez al arrancar**. Si cambias `dashboard.py` o vuelves a ejecutar el notebook, detén el servidor (`Ctrl + C`) y lánzalo de nuevo.

---

## Conceptos clave: RFM y segmentos

Cada cliente se describe con tres variables:

| Variable | Significado | Interpretación |
|---|---|---|
| **Recency** | Días desde su última compra | Menor = cliente más reciente (mejor) |
| **Frequency** | Número de facturas distintas | Mayor = compra más a menudo (mejor) |
| **Monetary** | Gasto total en libras (£) | Mayor = más valioso (mejor) |

Con estas variables, **K-Means (k = 4)** agrupa a los 4.338 clientes en 4 clusters, a los que el notebook asigna una etiqueta de negocio:

| Segmento | Color | Clientes | % clientes | % ingreso |
|---|---|---|---|---|
| 💎 VIP / Champions | Rojo | 5 | 0,1 % | 11,8 % |
| 🔄 Clientes Activos Leales | Verde | 23 | 0,5 % | 15,6 % |
| 🌱 Clientes Nuevos / Esporádicos | Azul | 268 | 6,2 % | 27,4 % |
| ⚠️ Clientes en Riesgo / Dormidos | Naranja | 4.042 | 93,2 % | 45,2 % |

**Lectura rápida:** apenas 296 clientes (6,8 %) generan el 54,8 % del ingreso, un comportamiento tipo Pareto.

---

## Barra lateral de filtros

| Control | Qué hace | Valor por defecto |
|---|---|---|
| **Segmento** | Muestra solo los segmentos elegidos (selección múltiple). | Vacío = todos |
| **País** | Muestra solo clientes de los países elegidos (37 países disponibles). El país es el de la última compra del cliente. | Vacío = todos |
| **Rango de Gasto (Monetary £)** | Filtra clientes por gasto total. El tope del slider es el percentil 99 (£19.780); la posición final, marcada **£19,780+**, significa *sin límite superior*. | £0 – £19,780+ (todos) |
| **Técnica de Visualización** | Elige PCA o t-SNE para el mapa de clusters. **Solo afecta a la pestaña Mapa de Clusters.** | PCA |

> **Importante sobre el slider:** todos los *VIP* (gasto mínimo £143.711) y todos los *Activos Leales* (gasto mínimo £33.053) gastan más que el tope del slider (£19.780). Por eso, en cuanto mueves el extremo derecho y deja de estar en **£19,780+**, esos dos segmentos desaparecen por completo, y también algunos *Nuevos / Esporádicos* (su gasto llega hasta £33.643).

---

## Indicadores principales (KPIs)

Las 4 tarjetas superiores se recalculan con **todos los filtros** (segmento, país y gasto). Valores sin filtros:

| Tarjeta | Valor | Cómo se calcula |
|---|---|---|
| **Clientes Analizados** | 4.338 | Número de clientes tras aplicar filtros |
| **Ingreso Total** | £8.887.209 | Suma de `Monetary` |
| **Frecuencia Media** | 4,3 pedidos | Media de `Frequency` |
| **Recency Media** | 93 días | Media de `Recency` |

Los 4.338 clientes coinciden con los clientes únicos tras la limpieza del notebook (392.692 registros de transacciones).

---

## 1. Pestaña 📊 Visión General

Resumen del negocio en 4 gráficos. Responde a todos los filtros excepto "Técnica de Visualización".

### Distribución de Segmentos (donut)
Porcentaje de clientes en cada segmento. Sin filtros, el donut está dominado por *En Riesgo / Dormidos* (93,2 %); los VIP (0,1 %) y Activos Leales (0,5 %) son casi invisibles.

### Gasto Medio (Monetary) por Segmento (barras horizontales)
Gasto promedio por cliente en cada segmento:

| Segmento | Gasto medio |
|---|---|
| VIP / Champions | £209.288 |
| Activos Leales | £60.341 |
| Nuevos / Esporádicos | £9.085 |
| En Riesgo / Dormidos | £994 |

Un cliente VIP gasta en promedio unas **210 veces** más que uno en riesgo.

### Recency vs Monetary (dispersión)
- Eje X: días desde la última compra. Eje Y: gasto total. Tamaño del punto: frecuencia. Color: segmento.
- Muestra hasta **2.000 clientes** aleatorios (semilla fija) para que el gráfico sea fluido.
- Los clientes valiosos aparecen arriba a la izquierda (recientes y con alto gasto); los dormidos se extienden hacia la derecha con gasto bajo.
- Al pasar el ratón se ve el `CustomerID` y la frecuencia.

### Top 10 Países por Gasto Total (barras)

| País | Gasto total |
|---|---|
| United Kingdom | £7.285.025 |
| Netherlands | £285.446 |
| EIRE (Irlanda) | £265.262 |
| Germany | £228.678 |
| France | £208.934 |
| Australia | £139.844 |
| Spain | £62.821 |
| Switzerland | £54.056 |
| Belgium | £40.279 |
| Sweden | £38.368 |

Reino Unido concentra el **82 %** del ingreso: es una tienda esencialmente británica. Filtrar por un país permite comparar mercados.

---

## 2. Pestaña 🗺️ Mapa de Clusters

Muestra cómo se separan los clusters. Es la **única pestaña que usa el selector PCA / t-SNE**.

### Mapa de Clusters (dispersión 2D)

| Técnica | Qué es | Clientes mostrados |
|---|---|---|
| **PCA** | Proyección lineal de las 3 variables RFM a 2 dimensiones; conserva las distancias globales. | Todos (se submuestrean 3.000 si hay más) |
| **t-SNE** | Proyección no lineal que agrupa a los clientes parecidos; resalta la estructura local. | Solo los 3.000 de la muestra en que se calculó t-SNE en el notebook |

- **Con PCA:** la mayoría de clientes forma una nube compacta cerca del origen (*En Riesgo*), y los clientes de alto valor se alejan hacia valores altos de PC1 (hasta ~205). Esto refleja que los clusters pequeños están formados por clientes extremos.
- **Con t-SNE:** los grupos se ven más separados visualmente, pero solo aparecen los clientes de la muestra: 4 de 5 VIP, 16 de 23 Activos Leales, 187 de 268 Nuevos y 2.793 de 4.042 En Riesgo. Por eso el título dice "(muestra)".
- La barra de herramientas del gráfico permite hacer zoom, que es útil para separar la nube central.

### Distribución RFM por Segmento (boxplots)
Tres paneles (Recency, Frequency, Monetary) con un boxplot por segmento: la línea central es la mediana, la caja el 50 % central de los clientes, y los puntos sueltos los valores atípicos. Permite ver no solo el promedio de cada segmento, sino qué tan dispersos son sus clientes.

---

## 3. Pestaña 👤 Perfilamiento

Describe a cada segmento. Responde a los filtros de segmento, país y gasto.

### Perfil Normalizado por Segmento (radar)
Cada eje se escala de 0 a 1 usando las **medianas** de los segmentos visibles. Recency está **invertida** (1 = compra más reciente), de modo que en los tres ejes "más grande es mejor". Valores sin filtros (aproximados):

| Segmento | Recency (inv.) | Frequency | Monetary |
|---|---|---|---|
| VIP / Champions | 1,00 | 0,98 | 1,00 |
| Activos Leales | 0,95 | 0,73 | 0,29 |
| Nuevos / Esporádicos | 0,86 | 0,22 | 0,03 |
| En Riesgo / Dormidos | 0,02 | 0,00 | 0,00 |

El área del VIP cubre casi todo el radar; la de *En Riesgo* casi desaparece.

> El radar es **relativo**: si filtras segmentos, la escala se recalcula con los que quedan visibles.

### Participación en Ingreso Total por Segmento (donut)
Porcentaje del ingreso que aporta cada segmento: En Riesgo 45,2 %, Nuevos 27,4 %, Activos Leales 15,6 %, VIP 11,8 %. Comparado con el donut de clientes de Visión General, muestra que los segmentos pequeños pesan mucho más en ingreso que en número.

### Tabla de Perfiles

| Segmento | Clientes | % Total | Recency mediana | Frequency mediana | Monetary mediana | Monetary total |
|---|---|---|---|---|---|---|
| 💎 VIP / Champions | 5 | 0,1 % | 1 día | 60 pedidos | £194.391 | £1.046.438 |
| 🔄 Activos Leales | 23 | 0,5 % | 4 días | 45 pedidos | £56.253 | £1.387.839 |
| 🌱 Nuevos / Esporádicos | 268 | 6,2 % | 9 días | 15 pedidos | £7.052 | £2.434.746 |
| ⚠️ En Riesgo / Dormidos | 4.042 | 93,2 % | 57 días | 2 pedidos | £610 | £4.018.185 |

Se usa la **mediana** porque los datos tienen valores extremos que distorsionan la media.

---

## 4. Pestaña 📈 Métricas

Compara los 4 modelos de clustering con métricas de validación interna. **No responde a ningún filtro**: muestra siempre los valores calculados en el notebook.

| Modelo | Silhouette ↑ | Davies-Bouldin ↓ | Calinski-Harabasz ↑ |
|---|---|---|---|
| K-Means | 0,7451 | 0,6131 | 7.921,33 |
| DBSCAN | 0,6027 | **0,3452** | 125,38 |
| GMM | 0,2845 | 1,2210 | 817,44 |
| AE + K-Means | **0,9546** | 0,5192 | 4.381,41 |

En la tabla del dashboard, el mejor valor de cada métrica aparece en verde.

**Cómo leer cada métrica:**

- **Silhouette (−1 a 1, mayor es mejor):** qué tan cerca está cada cliente de su propio cluster comparado con el cluster vecino. Gana **AE + K-Means** (0,9546).
- **Davies-Bouldin (≥ 0, menor es mejor):** relación entre la dispersión interna de los clusters y la distancia entre ellos. Gana **DBSCAN** (0,3452), pero DBSCAN descarta como "ruido" a los clientes que no encajan, y las métricas se calculan sin ellos, lo que lo favorece.
- **Calinski-Harabasz (≥ 0, mayor es mejor):** relación entre la separación entre clusters y la compacidad dentro de ellos. Gana **K-Means** (7.921).

El aviso verde inferior indica el **mejor modelo según Silhouette**, calculado automáticamente desde el CSV (actualmente *AE + K-Means*).

> **Ojo:**
> - Ninguna métrica gana en los tres criterios; no existe un "mejor modelo" absoluto.
> - Los segmentos del dashboard provienen de **K-Means**, no del Autoencoder.
> - Las métricas de AE + K-Means **cambian entre ejecuciones** del notebook (Silhouette de 0,69 a 0,95 en ejecuciones recientes) porque el entrenamiento de TensorFlow no es totalmente determinista.

---

## 5. Pestaña 💡 Recomendaciones

Una tarjeta por segmento con sus estadísticas medias y 4 estrategias de marketing sugeridas.

| Segmento | Clientes | Gasto medio | Frecuencia media | Recency media | Enfoque de las estrategias |
|---|---|---|---|---|---|
| 💎 VIP / Champions | 5 | £209.288 | 76,4 pedidos | 3 días | Retener y premiar: membresía exclusiva, acceso anticipado, atención prioritaria |
| 🔄 Activos Leales | 23 | £60.341 | 49,5 pedidos | 40 días | Aumentar el valor: email personalizado, puntos/cashback, upselling y cross-selling |
| 🌱 Nuevos / Esporádicos | 268 | £9.085 | 17,6 pedidos | 19 días | Generar recurrencia: onboarding, descuento en segunda compra, retargeting |
| ⚠️ En Riesgo / Dormidos | 4.042 | £994 | 3,0 pedidos | 98 días | Reactivar: campañas "te echamos de menos", descuentos de retención, encuestas |

**Comportamiento de los filtros en esta pestaña:**

- Solo usa el filtro de **Segmento**: si eliges segmentos, solo aparecen sus tarjetas; si no eliges ninguno, aparecen los 4.
- Las estadísticas de cada tarjeta se calculan **siempre sobre todos los clientes del segmento**, ignorando los filtros de país y gasto.

---

## Qué filtros afectan a cada pestaña

| Elemento | Segmento | País | Gasto | PCA / t-SNE |
|---|:---:|:---:|:---:|:---:|
| KPIs superiores | ✅ | ✅ | ✅ | — |
| 📊 Visión General | ✅ | ✅ | ✅ | — |
| 🗺️ Mapa de Clusters | ✅ | ✅ | ✅ | ✅ |
| 👤 Perfilamiento | ✅ | ✅ | ✅ | — |
| 📈 Métricas | — | — | — | — |
| 💡 Recomendaciones | ✅ (solo qué tarjetas se ven) | — | — | — |

---

## Limitaciones a tener en cuenta

1. **Segmentos muy desbalanceados.** K-Means se aplica sobre RFM sin transformación logarítmica, por lo que los clientes extremos forman clusters propios (5 y 23 clientes) y el 93 % queda en un solo grupo.
2. **Etiquetas a revisar.** El segmento *En Riesgo / Dormidos* agrupa al 93 % de los clientes con una recency mediana de 57 días, incluidos clientes que compraron hace muy poco. Y *Nuevos / Esporádicos* tiene en realidad una frecuencia mediana de 15 pedidos, más propia de clientes recurrentes de valor medio. Las etiquetas describen el cluster en conjunto, no a cada cliente.
3. **t-SNE es una muestra.** Solo 3.000 de los 4.338 clientes tienen coordenadas t-SNE.
4. **Métricas del Autoencoder inestables.** Varían entre ejecuciones del notebook hasta que se fije el determinismo de TensorFlow.
5. **País = último país de compra.** Un cliente que compró desde varios países se asigna solo al de su compra más reciente.
