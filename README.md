# Proyecto Final 4 - Customer Segmentation

Este proyecto analiza el dataset Online Retail para segmentar clientes mediante RFM, clustering, PCA, t-SNE y un autoencoder, y luego visualiza los resultados con un dashboard de Dash.

## Estructura del proyecto

- [customer_segmentation.ipynb](customer_segmentation.ipynb): notebook principal con el flujo completo del análisis.
- [dashboard.py](dashboard.py): dashboard interactivo para explorar la segmentación.
- [data/Online Retail.xlsx](data/Online%20Retail.xlsx): dataset original.
- [resultados](resultados): carpeta de salida con CSV e imágenes generadas.

## Requisitos

- Python 3.10 o superior
- Windows, macOS o Linux
- Conexión a internet para instalar dependencias

## 1) Crear entorno virtual

```bash
python -m venv .venv
```

Activar el entorno:

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

## 2) Instalar dependencias

```bash
pip install --upgrade pip
pip install pandas numpy matplotlib seaborn scikit-learn plotly dash dash-bootstrap-components openpyxl jupyter nbformat ipykernel tensorflow
```

## 3) Ejecutar el notebook

Desde la raíz del proyecto:

```bash
python -m jupyter nbconvert --to notebook --execute customer_segmentation.ipynb --inplace --ExecutePreprocessor.timeout=1800
```

También puedes abrir el notebook en Jupyter y ejecutarlo manualmente.

> El notebook está configurado para leer el dataset desde [data/Online Retail.xlsx](data/Online%20Retail.xlsx) y exportar los resultados a [resultados](resultados).

## 4) Ejecutar el dashboard

```bash
python dashboard.py
```

Luego abre esta URL en el navegador:

```text
http://127.0.0.1:8050
```

## 5) Archivos generados

Al ejecutar el notebook, se generarán archivos como:

- [resultados/rfm_segmented.csv](resultados/rfm_segmented.csv)
- [resultados/cluster_metrics.csv](resultados/cluster_metrics.csv)
- [resultados/figuras](resultados/figuras)

## 6) Solución de problemas comunes

### Error de rutas absolutas

Si el notebook fue copiado desde otro equipo, verifica que las rutas usen la carpeta del proyecto actual. Para este repositorio, la base debería ser la raíz del workspace y el dataset debe apuntar a:

```python
DATA_PATH = str(Path.cwd() / 'data' / 'Online Retail.xlsx')
```

### Error con matplotlib

En algunas versiones de Matplotlib, `cm.get_cmap()` puede fallar. Se recomienda usar:

```python
plt.get_cmap('tab10')
```

### El dashboard dice que no encuentra el CSV

Verifica que exista la carpeta [resultados](resultados) y que los archivos estén presentes antes de arrancar el dashboard.

## 7) Comando de validación rápida

```bash
python -c "from pathlib import Path; root=Path('.'); print((root/'resultados'/'rfm_segmented.csv').exists()); print((root/'resultados'/'cluster_metrics.csv').exists())"
```

Si ambos valores devuelven `True`, los datos están listos para el dashboard.


cd "C:\Users\USUARIO\Documents\ESPECIALIZACIÓN\proyecto_final4"
python -m jupyter notebook