"""
=============================================================
 Dashboard Interactivo — Segmentación Avanzada de Clientes
 Online Retail Dataset
 Tecnología: Dash + Plotly
=============================================================
"""

import warnings
warnings.filterwarnings('ignore')

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc

# ──────────────────────────────────────────────────────────────
# CONSTANTES Y PALETA
# ──────────────────────────────────────────────────────────────
SEGMENT_COLORS = {
    'VIP / Champions':               '#e74c3c',
    'Clientes Activos Leales':       '#2ecc71',
    'Clientes Nuevos / Esporádicos': '#3498db',
    'Clientes en Riesgo / Dormidos': '#f39c12',
}

SEGMENT_ICONS = {
    'VIP / Champions':               '💎',
    'Clientes Activos Leales':       '🔄',
    'Clientes Nuevos / Esporádicos': '🌱',
    'Clientes en Riesgo / Dormidos': '⚠️',
}

MARKETING_TIPS = {
    'VIP / Champions': [
        '🎯 Programa de fidelización exclusivo (membresía Gold/Platinum)',
        '🎁 Acceso anticipado a nuevos productos y ventas privadas',
        '📞 Atención personalizada y soporte prioritario',
        '💎 Descuentos por volumen y recompensas acumulativas',
    ],
    'Clientes Activos Leales': [
        '📧 Campañas de email personalizadas con recomendaciones',
        '🔄 Programas de puntos y cashback',
        '🆙 Estrategias de upselling y cross-selling',
        '🎉 Ofertas por cumpleaños y aniversario de cliente',
    ],
    'Clientes en Riesgo / Dormidos': [
        '🔔 Campañas de reactivación ("Te echamos de menos")',
        '💰 Descuentos agresivos de retención (15-30%)',
        '📊 Encuestas de satisfacción para identificar problemas',
        '🎁 Ofertas personalizadas basadas en historial previo',
    ],
    'Clientes Nuevos / Esporádicos': [
        '👋 Secuencia de bienvenida y onboarding automatizado',
        '🏷️ Descuento en segunda compra para fomentar recurrencia',
        '📱 Retargeting en redes sociales',
        '📦 Envío gratis o muestra en próxima compra',
    ],
}

# ──────────────────────────────────────────────────────────────
# CARGA DE DATOS
# ──────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / 'resultados'

rfm_path = RESULTS_DIR / 'rfm_segmented.csv'
metrics_path = RESULTS_DIR / 'cluster_metrics.csv'

if not rfm_path.exists():
    raise FileNotFoundError(f'No se encontró el dataset segmentado en: {rfm_path}')
if not metrics_path.exists():
    raise FileNotFoundError(f'No se encontró la métrica de clusters en: {metrics_path}')

df = pd.read_csv(rfm_path)
metrics_df = pd.read_csv(metrics_path)

segments_all = sorted(df['Segmento'].unique())
countries_all = sorted(df['Country'].dropna().unique())

# Tope del slider de gasto: percentil 99 para que los extremos no aplasten la escala.
# El extremo superior del slider significa "sin límite" (incluye a los clientes por encima).
MONETARY_SLIDER_MAX = int(df['Monetary'].quantile(0.99))

# ──────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────
def kpi_card(title: str, value: str, subtitle: str = '', color: str = '#3498db') -> dbc.Card:
    return dbc.Card(
        dbc.CardBody([
            html.P(title, className='text-muted mb-1', style={'fontSize': '0.8rem', 'fontWeight': '600', 'textTransform': 'uppercase', 'letterSpacing': '0.05em'}),
            html.H3(value, style={'color': color, 'fontWeight': '700', 'marginBottom': '2px'}),
            html.P(subtitle, className='text-muted mb-0', style={'fontSize': '0.75rem'}),
        ]),
        style={'borderLeft': f'4px solid {color}', 'borderRadius': '8px', 'boxShadow': '0 2px 8px rgba(0,0,0,0.08)'},
    )


def badge_segment(seg: str) -> html.Span:
    color = SEGMENT_COLORS.get(seg, '#888')
    icon  = SEGMENT_ICONS.get(seg, '◉')
    return html.Span(
        f'{icon} {seg}',
        style={
            'background': color, 'color': 'white', 'borderRadius': '12px',
            'padding': '3px 10px', 'fontSize': '0.78rem', 'fontWeight': '600',
        }
    )

# ──────────────────────────────────────────────────────────────
# LAYOUT PRINCIPAL
# ──────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY, dbc.icons.FONT_AWESOME],
    title='Customer Segmentation Dashboard',
    suppress_callback_exceptions=True,
)

# ---- Sidebar filtros ----
sidebar = dbc.Card([
    html.H5('🎛️ Filtros', className='card-title mb-3', style={'fontWeight': '700'}),
    html.Label('Segmento', className='fw-semibold small'),
    dcc.Dropdown(
        id='filter-segment',
        options=[{'label': f'{SEGMENT_ICONS.get(s,"")} {s}', 'value': s} for s in segments_all],
        multi=True,
        placeholder='Todos los segmentos',
        className='mb-3',
    ),
    html.Label('País', className='fw-semibold small'),
    dcc.Dropdown(
        id='filter-country',
        options=[{'label': c, 'value': c} for c in countries_all],
        multi=True,
        placeholder='Todos los países',
        className='mb-3',
    ),
    html.Label('Rango de Gasto (Monetary £)', className='fw-semibold small'),
    dcc.RangeSlider(
        id='filter-monetary',
        min=0, max=MONETARY_SLIDER_MAX,
        step=100,
        value=[0, MONETARY_SLIDER_MAX],
        marks={0: '£0', MONETARY_SLIDER_MAX: f'£{MONETARY_SLIDER_MAX:,}+'},
        tooltip={'placement': 'bottom', 'always_visible': False},
        className='mb-3',
    ),
    html.Label('Técnica de Visualización', className='fw-semibold small'),
    dcc.RadioItems(
        id='viz-technique',
        options=[
            {'label': ' PCA', 'value': 'PCA'},
            {'label': ' t-SNE', 'value': 'TSNE'},
        ],
        value='PCA',
        inline=True,
        className='mb-3',
        inputStyle={'marginRight': '4px'},
        labelStyle={'marginRight': '15px'},
    ),
    html.Hr(),
    html.P('Dataset: Online Retail (UCI/Kaggle)', className='text-muted small mb-0'),
    html.P('Modelo: K-Means + Autoencoder', className='text-muted small mb-0'),
], body=True, style={'borderRadius': '10px', 'boxShadow': '0 2px 12px rgba(0,0,0,0.07)', 'height': '100%'})

# ---- KPI Row ----
kpi_row = dbc.Row(id='kpi-row', className='mb-4 g-3')

# ---- Tabs ----
tabs = dbc.Tabs([
    dbc.Tab(label='📊 Visión General', tab_id='overview'),
    dbc.Tab(label='🗺️ Mapa de Clusters', tab_id='clusters'),
    dbc.Tab(label='👤 Perfilamiento', tab_id='profiling'),
    dbc.Tab(label='📈 Métricas', tab_id='metrics'),
    dbc.Tab(label='💡 Recomendaciones', tab_id='recommendations'),
], id='main-tabs', active_tab='overview', className='mb-3')

content = html.Div(id='tab-content')

# ---- Full layout ----
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H2('🛍️ Dashboard de Segmentación de Clientes', style={'fontWeight': '800', 'color': '#2c3e50'}),
            html.P('Online Retail Dataset · RFM · K-Means · Autoencoder · PCA · t-SNE',
                   className='text-muted'),
        ])
    ], className='my-4'),

    dbc.Row([
        # Sidebar
        dbc.Col(sidebar, md=3),
        # Main
        dbc.Col([
            kpi_row,
            tabs,
            content,
        ], md=9),
    ]),
], fluid=True, style={'backgroundColor': '#f8f9fa', 'minHeight': '100vh', 'paddingBottom': '40px'})


# ──────────────────────────────────────────────────────────────
# CALLBACKS
# ──────────────────────────────────────────────────────────────

def filter_data(segments, countries, monetary_range):
    """Aplica filtros al dataframe."""
    dff = df.copy()
    if segments:
        dff = dff[dff['Segmento'].isin(segments)]
    if countries:
        dff = dff[dff['Country'].isin(countries)]
    if monetary_range:
        low, high = monetary_range
        dff = dff[dff['Monetary'] >= low]
        if high < MONETARY_SLIDER_MAX:
            dff = dff[dff['Monetary'] <= high]
    return dff


@app.callback(
    Output('kpi-row', 'children'),
    [Input('filter-segment', 'value'),
     Input('filter-country', 'value'),
     Input('filter-monetary', 'value')],
)
def update_kpis(segments, countries, monetary_range):
    dff = filter_data(segments, countries, monetary_range)
    total_clients   = len(dff)
    total_revenue   = dff['Monetary'].sum()
    avg_frequency   = dff['Frequency'].mean()
    avg_recency     = dff['Recency'].mean()
    top_seg         = dff['Segmento'].value_counts().idxmax() if len(dff) > 0 else '—'
    top_seg_pct     = 100 * dff['Segmento'].value_counts().iloc[0] / max(total_clients, 1) if len(dff) > 0 else 0

    cards = [
        dbc.Col(kpi_card('Clientes Analizados', f'{total_clients:,}', 'en los filtros seleccionados', '#3498db'), md=3),
        dbc.Col(kpi_card('Ingreso Total', f'£{total_revenue:,.0f}', 'suma Monetary RFM', '#2ecc71'), md=3),
        dbc.Col(kpi_card('Frecuencia Media', f'{avg_frequency:.1f}', 'pedidos por cliente', '#9b59b6'), md=3),
        dbc.Col(kpi_card('Recency Media', f'{avg_recency:.0f} días', 'desde última compra', '#e67e22'), md=3),
    ]
    return cards


@app.callback(
    Output('tab-content', 'children'),
    [Input('main-tabs', 'active_tab'),
     Input('filter-segment', 'value'),
     Input('filter-country', 'value'),
     Input('filter-monetary', 'value'),
     Input('viz-technique', 'value')],
)
def render_tab(active_tab, segments, countries, monetary_range, viz_technique):
    dff = filter_data(segments, countries, monetary_range)

    # ─────────── OVERVIEW ───────────
    if active_tab == 'overview':
        # Pie de distribución de segmentos
        seg_counts = dff['Segmento'].value_counts().reset_index()
        seg_counts.columns = ['Segmento', 'Clientes']
        pie_colors = [SEGMENT_COLORS.get(s, '#888') for s in seg_counts['Segmento']]

        fig_pie = px.pie(
            seg_counts, values='Clientes', names='Segmento',
            title='Distribución de Segmentos', hole=0.45,
            color='Segmento', color_discrete_map=SEGMENT_COLORS,
        )
        fig_pie.update_traces(textinfo='percent+label', pull=[0.03]*len(seg_counts))
        fig_pie.update_layout(showlegend=False, margin=dict(t=50, b=20))

        # Bar chart Monetary por segmento
        seg_mon = dff.groupby('Segmento')['Monetary'].mean().reset_index()
        fig_bar = px.bar(
            seg_mon.sort_values('Monetary', ascending=True),
            x='Monetary', y='Segmento', orientation='h',
            title='Gasto Medio (Monetary) por Segmento',
            color='Segmento', color_discrete_map=SEGMENT_COLORS,
            labels={'Monetary': '£ Gasto Medio'},
            text_auto='.0f',
        )
        fig_bar.update_layout(showlegend=False, margin=dict(t=50, b=20))

        # Scatter Recency vs Monetary
        fig_scatter = px.scatter(
            dff.sample(min(2000, len(dff)), random_state=42),
            x='Recency', y='Monetary', color='Segmento',
            size='Frequency', hover_data=['CustomerID', 'Frequency'],
            title='Recency vs Monetary (tamaño = Frequency)',
            color_discrete_map=SEGMENT_COLORS,
            labels={'Recency': 'Días desde última compra', 'Monetary': '£ Gasto Total'},
            opacity=0.7,
        )
        fig_scatter.update_layout(margin=dict(t=50, b=20))

        # Top países
        top_c = dff.groupby('Country')['Monetary'].sum().nlargest(10).reset_index()
        fig_countries = px.bar(
            top_c.sort_values('Monetary'),
            x='Monetary', y='Country', orientation='h',
            title='Top 10 Países por Gasto Total',
            color='Monetary', color_continuous_scale='Blues',
            labels={'Monetary': '£ Gasto Total'},
            text_auto='.0f',
        )
        fig_countries.update_layout(showlegend=False, margin=dict(t=50, b=20), coloraxis_showscale=False)

        return dbc.Row([
            dbc.Col(dcc.Graph(figure=fig_pie, config={'displayModeBar': False}), md=6),
            dbc.Col(dcc.Graph(figure=fig_bar, config={'displayModeBar': False}), md=6),
            dbc.Col(dcc.Graph(figure=fig_scatter, config={'displayModeBar': False}), md=6),
            dbc.Col(dcc.Graph(figure=fig_countries, config={'displayModeBar': False}), md=6),
        ], className='g-3')

    # ─────────── CLUSTERS (PCA / tSNE) ───────────
    elif active_tab == 'clusters':
        if viz_technique == 'PCA':
            x_col, y_col = 'PCA_1', 'PCA_2'
            x_lbl, y_lbl = 'PC1', 'PC2'
            title_extra = 'Proyección PCA 2D'
        else:
            dff_tsne = dff.dropna(subset=['TSNE_1', 'TSNE_2'])
            x_col, y_col = 'TSNE_1', 'TSNE_2'
            x_lbl, y_lbl = 't-SNE 1', 't-SNE 2'
            title_extra = 'Proyección t-SNE 2D (muestra)'
            dff = dff_tsne

        fig_scatter2d = px.scatter(
            dff.sample(min(3000, len(dff)), random_state=42) if len(dff) > 3000 else dff,
            x=x_col, y=y_col, color='Segmento',
            hover_data=['CustomerID', 'Recency', 'Frequency', 'Monetary'],
            title=f'Mapa de Clusters — {title_extra}',
            labels={x_col: x_lbl, y_col: y_lbl},
            color_discrete_map=SEGMENT_COLORS,
            opacity=0.7,
        )
        fig_scatter2d.update_traces(marker_size=5)
        fig_scatter2d.update_layout(legend_title='Segmento', height=520, margin=dict(t=60))

        # Distribución de RFM por cluster en boxplots
        fig_box = make_subplots(rows=1, cols=3, subplot_titles=['Recency', 'Frequency', 'Monetary'])
        for var, col in [('Recency', 1), ('Frequency', 2), ('Monetary', 3)]:
            for seg in segments_all:
                sub = dff[dff['Segmento'] == seg][var]
                fig_box.add_trace(
                    go.Box(y=sub, name=seg, marker_color=SEGMENT_COLORS.get(seg, '#888'),
                           showlegend=(col == 1), legendgroup=seg),
                    row=1, col=col
                )
        fig_box.update_layout(title='Distribución RFM por Segmento', height=420, boxmode='group',
                               margin=dict(t=60), legend_title='Segmento')

        return html.Div([
            dcc.Graph(figure=fig_scatter2d, config={'displayModeBar': True}),
            dcc.Graph(figure=fig_box, config={'displayModeBar': False}),
        ])

    # ─────────── PROFILING ───────────
    elif active_tab == 'profiling':
        profile = dff.groupby('Segmento').agg(
            Clientes    = ('CustomerID', 'count'),
            Recency_med = ('Recency', 'median'),
            Recency_mean= ('Recency', 'mean'),
            Freq_med    = ('Frequency', 'median'),
            Freq_mean   = ('Frequency', 'mean'),
            Mon_med     = ('Monetary', 'median'),
            Mon_mean    = ('Monetary', 'mean'),
            Mon_total   = ('Monetary', 'sum'),
        ).reset_index().round(2)

        # Radar chart
        categories = ['Recency<br>(inv.)', 'Frequency', 'Monetary']
        fig_radar = go.Figure()

        for _, row in profile.iterrows():
            r_norm = 1 - (row['Recency_med'] - profile['Recency_med'].min()) / \
                         (profile['Recency_med'].max() - profile['Recency_med'].min() + 1)
            f_norm = (row['Freq_med'] - profile['Freq_med'].min()) / \
                     (profile['Freq_med'].max() - profile['Freq_med'].min() + 1)
            m_norm = (row['Mon_med'] - profile['Mon_med'].min()) / \
                     (profile['Mon_med'].max() - profile['Mon_med'].min() + 1)
            vals = [r_norm, f_norm, m_norm, r_norm]
            cats = categories + [categories[0]]
            fig_radar.add_trace(go.Scatterpolar(
                r=vals, theta=cats, fill='toself', name=row['Segmento'],
                line_color=SEGMENT_COLORS.get(row['Segmento'], '#888'),
                fillcolor=SEGMENT_COLORS.get(row['Segmento'], '#888'),
                opacity=0.35,
            ))

        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            title='Perfil Normalizado por Segmento (Radar)',
            showlegend=True, height=420, margin=dict(t=60),
        )

        # Tabla de perfil
        table_header = [
            html.Thead(html.Tr([
                html.Th('Segmento'), html.Th('Clientes'), html.Th('% Total'),
                html.Th('Recency Median'), html.Th('Frequency Median'),
                html.Th('Monetary Median £'), html.Th('Monetary Total £'),
            ]))
        ]
        table_rows = []
        total = profile['Clientes'].sum()
        for _, r in profile.iterrows():
            seg = r['Segmento']
            table_rows.append(html.Tr([
                html.Td(badge_segment(seg)),
                html.Td(f'{r["Clientes"]:,.0f}'),
                html.Td(f'{100*r["Clientes"]/total:.1f}%'),
                html.Td(f'{r["Recency_med"]:.0f} días'),
                html.Td(f'{r["Freq_med"]:.0f} pedidos'),
                html.Td(f'£{r["Mon_med"]:,.0f}'),
                html.Td(f'£{r["Mon_total"]:,.0f}'),
            ]))
        table = dbc.Table(table_header + [html.Tbody(table_rows)],
                          bordered=True, hover=True, responsive=True, striped=True,
                          className='small')

        # Revenue share pie
        fig_rev = px.pie(
            profile, values='Mon_total', names='Segmento',
            title='Participación en Ingreso Total por Segmento',
            color='Segmento', color_discrete_map=SEGMENT_COLORS, hole=0.4,
        )
        fig_rev.update_traces(textinfo='percent+label')
        fig_rev.update_layout(showlegend=False, margin=dict(t=60))

        return html.Div([
            dbc.Row([
                dbc.Col(dcc.Graph(figure=fig_radar, config={'displayModeBar': False}), md=6),
                dbc.Col(dcc.Graph(figure=fig_rev, config={'displayModeBar': False}), md=6),
            ], className='g-3 mb-3'),
            html.H5('📋 Tabla de Perfiles', className='fw-bold mb-2'),
            table,
        ])

    # ─────────── MÉTRICAS ───────────
    elif active_tab == 'metrics':
        metrics_df2 = metrics_df.rename(columns={'Unnamed: 0': 'Modelo'}).set_index('Modelo')
        best_model = metrics_df2['Silhouette ↑'].idxmax()

        fig_sil = px.bar(
            metrics_df2.reset_index(), x='Modelo', y='Silhouette ↑',
            title='Silhouette Score (mayor = mejor)',
            color='Modelo', text_auto='.4f',
            color_discrete_sequence=['#3498db', '#e74c3c', '#2ecc71', '#9b59b6'],
        )
        fig_sil.update_layout(showlegend=False, yaxis_range=[0, 1], margin=dict(t=60))

        fig_db = px.bar(
            metrics_df2.reset_index(), x='Modelo', y='Davies-Bouldin ↓',
            title='Davies-Bouldin Index (menor = mejor)',
            color='Modelo', text_auto='.4f',
            color_discrete_sequence=['#3498db', '#e74c3c', '#2ecc71', '#9b59b6'],
        )
        fig_db.update_layout(showlegend=False, margin=dict(t=60))

        fig_ch = px.bar(
            metrics_df2.reset_index(), x='Modelo', y='Calinski-Harabasz ↑',
            title='Calinski-Harabasz Score (mayor = mejor)',
            color='Modelo', text_auto='.0f',
            color_discrete_sequence=['#3498db', '#e74c3c', '#2ecc71', '#9b59b6'],
        )
        fig_ch.update_layout(showlegend=False, margin=dict(t=60))

        # Tabla de métricas
        rows_m = [html.Tr([
            html.Td(html.Strong(row['Modelo'])),
            html.Td(f'{row["Silhouette ↑"]:.4f}', style={'color': '#2ecc71' if row['Silhouette ↑'] == metrics_df2['Silhouette ↑'].max() else ''}),
            html.Td(f'{row["Davies-Bouldin ↓"]:.4f}', style={'color': '#2ecc71' if row['Davies-Bouldin ↓'] == metrics_df2['Davies-Bouldin ↓'].min() else ''}),
            html.Td(f'{row["Calinski-Harabasz ↑"]:.2f}', style={'color': '#2ecc71' if row['Calinski-Harabasz ↑'] == metrics_df2['Calinski-Harabasz ↑'].max() else ''}),
        ]) for _, row in metrics_df2.reset_index().iterrows()]

        tbl_m = dbc.Table(
            [html.Thead(html.Tr([html.Th('Modelo'), html.Th('Silhouette ↑'), html.Th('Davies-Bouldin ↓'), html.Th('Calinski-Harabasz ↑')])),
             html.Tbody(rows_m)],
            bordered=True, hover=True, striped=True, responsive=True, className='small',
        )

        return html.Div([
            dbc.Row([
                dbc.Col(dcc.Graph(figure=fig_sil, config={'displayModeBar': False}), md=4),
                dbc.Col(dcc.Graph(figure=fig_db,  config={'displayModeBar': False}), md=4),
                dbc.Col(dcc.Graph(figure=fig_ch,  config={'displayModeBar': False}), md=4),
            ], className='g-3 mb-3'),
            html.H5('📋 Resumen de Métricas', className='fw-bold mb-2'),
            tbl_m,
            dbc.Alert([
                html.Strong(f'🏆 Mejor modelo según Silhouette: {best_model} '),
                f'con Silhouette Score de {metrics_df2.loc[best_model, "Silhouette ↑"]:.4f}.'
            ], color='success', className='mt-3'),
        ])

    # ─────────── RECOMENDACIONES ───────────
    elif active_tab == 'recommendations':
        segs_to_show = segments if segments else list(MARKETING_TIPS.keys())
        cards = []
        for seg in segs_to_show:
            if seg not in MARKETING_TIPS:
                continue
            tips = MARKETING_TIPS[seg]
            color = SEGMENT_COLORS.get(seg, '#888')
            icon  = SEGMENT_ICONS.get(seg, '◉')
            # Stats
            seg_data = df[df['Segmento'] == seg]
            n = len(seg_data)
            mon = seg_data['Monetary'].mean()
            freq = seg_data['Frequency'].mean()
            rec  = seg_data['Recency'].mean()

            card = dbc.Card([
                dbc.CardHeader(
                    html.H5(f'{icon} {seg}', className='mb-0', style={'color': color, 'fontWeight': '700'}),
                    style={'borderLeft': f'5px solid {color}', 'backgroundColor': '#fff'}
                ),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col(html.Div([
                            html.Span('Clientes', className='text-muted small d-block'),
                            html.Strong(f'{n:,}', style={'fontSize': '1.2rem', 'color': color}),
                        ]), md=3),
                        dbc.Col(html.Div([
                            html.Span('Gasto Medio', className='text-muted small d-block'),
                            html.Strong(f'£{mon:,.0f}', style={'fontSize': '1.2rem', 'color': color}),
                        ]), md=3),
                        dbc.Col(html.Div([
                            html.Span('Frecuencia Media', className='text-muted small d-block'),
                            html.Strong(f'{freq:.1f} pedidos', style={'fontSize': '1.2rem', 'color': color}),
                        ]), md=3),
                        dbc.Col(html.Div([
                            html.Span('Recency Media', className='text-muted small d-block'),
                            html.Strong(f'{rec:.0f} días', style={'fontSize': '1.2rem', 'color': color}),
                        ]), md=3),
                    ], className='mb-3'),
                    html.Hr(),
                    html.H6('💡 Estrategias de Marketing Recomendadas:', className='fw-bold mb-2'),
                    html.Ul([html.Li(tip, className='mb-1') for tip in tips]),
                ])
            ], className='mb-3', style={'borderRadius': '10px', 'boxShadow': '0 2px 10px rgba(0,0,0,0.06)'})
            cards.append(card)

        return html.Div(cards if cards else [
            dbc.Alert('Selecciona al menos un segmento en los filtros para ver las recomendaciones.', color='info')
        ])

    return html.Div('Contenido no encontrado.')


# ──────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=8050)
