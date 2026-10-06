# Proyecto Final 4 - Customer Segmentation

Este proyecto analiza el dataset Online Retail para segmentar clientes mediante RFM, clustering, PCA, t-SNE y un autoencoder, y luego visualiza los resultados con un dashboard de Dash.

## Estructura del proyecto

- [customer_segmentation.ipynb](customer_segmentation.ipynb): notebook principal con el flujo completo del análisis.
- [dashboard.py](dashboard.py): dashboard interactivo para explorar la segmentación.
- [data/Online Retail.xlsx](data/Online%20Retail.xlsx): dataset original.
- [requirements.txt](requirements.txt): dependencias del proyecto con versiones fijadas.
- [documento](documento): informe escrito del proyecto.
- [resultados](resultados): carpeta de salida con CSV e imágenes generadas.

## Requisitos

- Python 3.12 (versión con la que se probó `requirements.txt`)
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
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Para ejecutar el notebook desde Jupyter con este entorno, registra el kernel (el notebook usa el kernel `proyecto_final4`):

```bash
python -m ipykernel install --user --name proyecto_final4 --display-name "Python (.venv)"
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
