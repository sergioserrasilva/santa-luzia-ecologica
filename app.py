import streamlit as st
import geemap.foliumap as geemap
import ee
import json
import pandas as pd
import geopandas as gpd
import tempfile
import os
import plotly.express as px
import matplotlib.pyplot as plt
import base64
from datetime import datetime
import numpy as np
import io
from PIL import Image

# 🔧 CORREÇÃO: Configuração inicial ANTES de qualquer outro código
st.set_page_config(
    page_title="ECOLÓGICA - Santa Luzia",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuração para deploy
if not os.path.exists('assets'):
    os.makedirs('assets')

# 🔧 CORREÇÃO: Inicialização mais robusta do Earth Engine
@st.cache_resource
def initialize_earth_engine():
    try:
        # Método 1: Tentar inicializar com service account
        if os.path.exists('service_account.json'):
            service_account = 'ecologica-earth-engine@ee-serginss-459118.iam.gserviceaccount.com'
            credentials = ee.ServiceAccountCredentials(service_account, 'service_account.json')
            ee.Initialize(credentials)
            return True
        else:
            # Método 2: Tentar autenticação normal
            ee.Initialize(project='ee-serginss-459118')
            return True
    except Exception as e:
        st.sidebar.warning(f"⚠️ Earth Engine em modo offline: {str(e)}")
        return False

# Inicializar Earth Engine
ee_initialized = initialize_earth_engine()

# 🔧 CORREÇÃO: CSS simplificado para evitar conflitos
st.markdown("""
<style>
    .main-header {
        font-family: 'Comic Sans MS', cursive;
        font-size: 3.5rem !important;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 0.2rem;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.2);
        background: linear-gradient(45deg, #2E8B57, #32CD32, #90EE90);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sub-header {
        font-family: 'Comic Sans MS', cursive;
        font-size: 1.8rem !important;
        color: #228B22;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .card {
        background: linear-gradient(135deg, #f8fff8, #e8f5e8);
        border-radius: 20px;
        padding: 20px;
        border: 3px solid #98FB98;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    .stButton>button {
        background: linear-gradient(45deg, #32CD32, #228B22);
        color: white;
        border-radius: 25px;
        border: none;
        padding: 12px 25px;
        font-weight: bold;
        font-size: 16px;
        font-family: 'Comic Sans MS', cursive;
    }
    .metric-card {
        background: linear-gradient(135deg, #90EE90, #32CD32);
        color: white;
        padding: 20px;
        border-radius: 20px;
        text-align: center;
        margin: 8px;
        border: 2px solid white;
    }
</style>
""", unsafe_allow_html=True)

# 🔧 CORREÇÃO: Remover funções problemáticas de screenshot
def save_map_as_image(m, filename="mapa_santa_luzia.png"):
    try:
        # Salvar o mapa como HTML temporariamente
        temp_html = "temp_map.html"
        m.save(temp_html)
        
        st.info("📸 **Para salvar o mapa:**")
        st.markdown("""
        - **Computador:** Pressione `Print Screen` ou `Windows + Shift + S`
        - **Celular:** Volume baixo + Power (Android) ou Botão lateral + Volume alto (iPhone)
        """)
        
        # Oferecer download do HTML do mapa
        with open(temp_html, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        st.download_button(
            label="📁 Baixar Mapa Interativo (HTML)",
            data=html_content,
            file_name=f"mapa_santa_luzia_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
            mime="text/html",
        )
        
        # Limpar arquivo temporário
        os.remove(temp_html)
        
        return True
    except Exception as e:
        st.error(f"❌ Erro ao processar o mapa: {str(e)}")
        return False

# 🔧 CORREÇÃO: Função de carregamento de imagens com fallback
def get_image_base64(path):
    try:
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except:
        return None

# Cabeçalho com logos animadas
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    eco_logo = get_image_base64("assets/eco.png")
    if eco_logo:
        st.markdown(
            f'<div style="text-align: center;">'
            f'<img src="data:image/png;base64,{eco_logo}" width="250">'
            f'</div>', 
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div style="text-align: center; font-size: 80px;">🌱</div>', 
            unsafe_allow_html=True
        )

with col2:
    st.markdown('<h1 class="main-header">ECOLÓGICA</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header"> Ciência, Dados e Sustentabilidade🌟</p>', unsafe_allow_html=True)

with col3:
    logo_umi = get_image_base64("assets/LOGOUMI.png")
    if logo_umi:
        st.markdown(
            f'<div style="text-align: center;">'
            f'<img src="data:image/png;base64,{logo_umi}" width="400">'
            f'</div>', 
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div style="text-align: center; font-size: 80px;">🔬</div>', 
            unsafe_allow_html=True
        )

# Descrição completa da Eletiva
st.markdown("---")

descricao_completa = """
ELETIVA INTEGRADA: CIÊNCIAS DA NATUREZA E MATEMÁTICA

A Eletiva integra Ciências da Natureza e Matemática para investigar a vegetação, o uso e a cobertura do solo e a qualidade da água em Santa Luzia - MA.

O que fazemos:

• Pesquisas de campo e análises laboratoriais  
• Produção de exsicatas para herbário  
• Uso de plataformas digitais e tabulação de dados  
• Desenvolvimento de propostas de ações sustentáveis  

**Culminância:** Apresentação do acervo de exsicatas, mapas e resultados das análises ambientais.

Vamos juntos explorar e entender nossa região! 🌱🗺️
"""

st.markdown(f'<div class="card" style="font-size: 16px; line-height: 1.6; text-align: center;">{descricao_completa}</div>', unsafe_allow_html=True)

# Configuração das classes do MapBiomas
CLASS_CONFIG = {
    'names': {
        1: "🌳 Florestas", 
        2: "🌾 Campos", 
        3: "🚜 Agricultura", 
        4: "🏙️ Cidades", 
        5: "💧 Água", 
        6: "❓ Outros"
    },
    'colors': {
        "🌳 Florestas": "#1f8d49",
        "🌾 Campos": "#d6bc74", 
        "🚜 Agricultura": "#ffef5c",
        "🏙️ Cidades": "#d4271e",
        "💧 Água": "#2532e4",
        "❓ Outros": "#cccccc"
    },
    'descriptions': {
        "🌳 Florestas": "Árvores altas e florestas! 🌳",
        "🌾 Campos": "Campos verdes e limpos!", 
        "🚜 Agricultura": "Onde cresce nossa comida! 🍎",
        "🏙️ Cidades": "Casas, escolas e parques! 🏠",
        "💧 Água": "Rios e lagos! 💦",
        "❓ Outros": "Lugares especiais! ✨"
    },
    'codes': [1, 3, 4, 5, 6, 49, 10, 11, 12, 32, 29, 50, 14, 15, 18, 19, 39, 20, 40, 62, 41, 36, 46, 47, 35, 48, 9, 21, 22, 23, 24, 30, 25, 26, 33, 31, 27],
    'new_classes': [1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 5, 5, 5, 6],
    'palette': ["#1f8d49", "#d6bc74", "#ffef5c", "#d4271e", "#2532e4", "#cccccc"]
}

# Carregar GeoJSON com municípios e filtrar Santa Luzia
try:
    with open('assets/municipios_ma.geojson', 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)
        st.sidebar.success("✅ GeoJSON carregado!")
        
        # Filtrar apenas Santa Luzia
        santa_luzia_features = []
        for feature in geojson_data['features']:
            nome = feature['properties'].get('NM_MUNICIP', '')
            if 'SANTA LUZIA' in nome.upper():
                santa_luzia_features.append(feature)
        
except Exception as e:
    st.sidebar.error(f"❌ Erro no GeoJSON: {str(e)}")
    geojson_data = None

@st.cache_resource
def load_municipios():
    municipios = {}
    if geojson_data:
        for feature in geojson_data['features']:
            nome = feature['properties'].get('NM_MUNICIP')
            if nome and 'SANTA LUZIA' in nome.upper():
                municipios[nome] = feature['geometry']
    return municipios

MUNICIPIOS_MA = load_municipios()

# 🔧 CORREÇÃO: Carregar MapBiomas apenas se EE estiver inicializado
mapbiomas_image = None
remapped_image = None

if ee_initialized:
    try:
        mapbiomas_image = ee.Image('projects/mapbiomas-public/assets/brazil/lulc/collection9/mapbiomas_collection90_integration_v1')
        
        def reclassify_bands(image, codes, new_classes):
            remapped_bands = []
            for year in range(1985, 2024):
                original_band = f'classification_{year}'
                remapped_band = image.select(original_band).remap(codes, new_classes).rename(original_band)
                remapped_bands.append(remapped_band)
            return ee.Image.cat(remapped_bands)
        
        remapped_image = reclassify_bands(mapbiomas_image, CLASS_CONFIG['codes'], CLASS_CONFIG['new_classes'])
        st.sidebar.success("✅ MapBiomas carregado!")
    except Exception as e:
        st.sidebar.error(f"❌ Erro no MapBiomas: {str(e)}")

# Sidebar interativa
st.sidebar.markdown("## 🎮 **PAINEL DO EXPLORADOR**")

# Status do Earth Engine
if ee_initialized:
    st.sidebar.success("✅ Earth Engine Conectado")
else:
    st.sidebar.error("❌ Earth Engine Offline")

# Seletor de anos com botões específicos
st.sidebar.markdown("### 🗓️ **ESCOLHA O ANO**")
anos_especificos = [1985, 2000, 2010, 2022, 2023]

if 'selected_years' not in st.session_state:
    st.session_state.selected_years = [2023]

# Criar botões para os anos específicos
cols = st.sidebar.columns(3)
botoes_por_coluna = [2, 2, 1]
botao_idx = 0

for col_idx, num_botoes in enumerate(botoes_por_coluna):
    with cols[col_idx]:
        for _ in range(num_botoes):
            if botao_idx < len(anos_especificos):
                year = anos_especificos[botao_idx]
                is_selected = year in st.session_state.selected_years
                button_emoji = "✅" if is_selected else "📅"
                button_label = f"{button_emoji} {year}"
                
                if st.button(button_label, key=f"year_{year}", use_container_width=True):
                    st.session_state.selected_years = [year]
                    st.rerun()
                
                botao_idx += 1

# Mostrar ano selecionado
if st.session_state.selected_years:
    ano_selecionado = st.session_state.selected_years[0]
    st.sidebar.markdown(f"**🌟 Ano selecionado:** **{ano_selecionado}**")

# Seletor de classes de cobertura
st.sidebar.markdown("### 🌟 **LUGARES PARA EXPLORAR**")
all_classes = list(CLASS_CONFIG['names'].values())
selected_class_names = st.sidebar.multiselect(
    "Escolha os tipos de lugares:",
    options=all_classes,
    default=all_classes,
    format_func=lambda x: f"{x} {CLASS_CONFIG['descriptions'][x]}"
)

# Mapear nomes de volta para códigos numéricos
name_to_code = {v: k for k, v in CLASS_CONFIG['names'].items()}
selected_class_codes = [name_to_code[name] for name in selected_class_names]

# Informações educativas
st.sidebar.markdown("### 📚 **CURIOSIDADES**")
st.sidebar.markdown("""
<div style="background: linear-gradient(135deg, #e3f2fd, #bbdefb); padding: 15px; border-radius: 15px; border: 2px solid #64b5f6;">
🎯 <strong>Você sabia?</strong><br>
Santa Luzia é um município do Maranhão com muita natureza para explorar! 
Árvores altas, rios limpos e muitas histórias para contar! 📖
</div>
""", unsafe_allow_html=True)

# Definir geometria de Santa Luzia automaticamente
geometry = None
area_name = "Santa Luzia"

if MUNICIPIOS_MA and ee_initialized:
    municipio_nome = list(MUNICIPIOS_MA.keys())[0]
    geometry = ee.Geometry(MUNICIPIOS_MA[municipio_nome])
    area_name = municipio_nome
    st.sidebar.success(f"📍 {area_name}")
elif not ee_initialized:
    st.sidebar.warning("📍 Santa Luzia (modo offline)")

# Usar anos selecionados do session state
selected_years = st.session_state.selected_years

# 🔧 CORREÇÃO: Função de estatísticas com verificação de EE
def calculate_statistics(geometry, selected_years, selected_class_codes):
    if not ee_initialized or not geometry:
        return pd.DataFrame()
        
    stats_data = []
    for year in selected_years:
        band = remapped_image.select(f"classification_{year}")
        
        # Filtrar apenas classes selecionadas
        class_masks = []
        valid_classes = []
        for class_code in selected_class_codes:
            if class_code in [1, 2, 3, 4, 5, 6]:
                class_masks.append(band.eq(class_code).rename(f'class_{class_code}'))
                valid_classes.append(class_code)
        
        if class_masks:
            areas = ee.Image.cat(*class_masks).multiply(ee.Image.pixelArea()).reduceRegion(
                reducer=ee.Reducer.sum().repeat(len(class_masks)),
                geometry=geometry,
                scale=100,  # 🔧 Aumentar escala para performance
                maxPixels=1e10
            )
            try:
                areas_dict = areas.getInfo()
                if 'sum' in areas_dict:
                    areas_list = areas_dict['sum']
                    for i, class_value in enumerate(valid_classes):
                        area_m2 = areas_list[i] if i < len(areas_list) else 0
                        area_km2 = area_m2 / 1e6
                        stats_data.append({
                            "Ano": year,
                            "Classe": class_value,
                            "Nome da Classe": CLASS_CONFIG['names'][class_value],
                            "Área (km²)": round(area_km2, 2)
                        })
            except Exception as e:
                st.error(f"❌ Erro ao processar {year}: {str(e)}")
                continue
    
    return pd.DataFrame(stats_data) if stats_data else pd.DataFrame()

# Layout principal com abas
tab1, tab2, tab3, tab4 = st.tabs(["🎯 VISÃO GERAL", "📊 GRÁFICOS", "🗺️ MAPA", "📋 DADOS"])

with tab1:
    st.markdown("## 🎯 **PANORAMA DE SANTA LUZIA**")
    
    if ee_initialized and geometry and selected_years:
        df = calculate_statistics(geometry, selected_years, selected_class_codes)
        
        if not df.empty:
            latest_year = selected_years[0]
            latest_data = df[df['Ano'] == latest_year]
            
            st.markdown(f"### 📊 **FOTOGRAFIA DE {latest_year}**")
            
            # Métricas principais
            cols = st.columns(3)
            metrics_data = []
            
            for class_code in selected_class_codes:
                class_name = CLASS_CONFIG['names'][class_code]
                area_value = latest_data[latest_data['Nome da Classe'] == class_name]['Área (km²)'].sum()
                metrics_data.append((class_name, area_value))
            
            # Distribuir métricas nas colunas
            for col, (nome, valor) in zip(cols, metrics_data[:3]):
                with col:
                    emoji = nome.split()[0]
                    st.markdown(
                        f'<div class="metric-card">'
                        f'<div style="font-size: 2.5rem;">{emoji}</div>'
                        f'<div style="font-size: 1.1rem; font-weight: bold;">{nome}</div>'
                        f'<div style="font-size: 1.8rem; margin-top: 15px;">{valor:.0f} km²</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
            
            # Gráfico de pizza
            st.markdown("### **COMO ESTÁ DIVIDIDA NOSSA TERRA?**")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                pie_fig = px.pie(
                    latest_data,
                    names="Nome da Classe",
                    values="Área (km²)",
                    title=f"Distribuição das Áreas em {latest_year}",
                    color="Nome da Classe",
                    color_discrete_map=CLASS_CONFIG['colors'],
                    hole=0.4,
                    height=500
                )
                pie_fig.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    marker=dict(line=dict(color='white', width=2))
                )
                pie_fig.update_layout(
                    font=dict(size=14),
                    showlegend=False
                )
                st.plotly_chart(pie_fig, use_container_width=True)
            
            with col2:
                st.markdown("#### 📖 **HISTÓRIA DE CADA LUGAR**")
                for classe in latest_data['Nome da Classe'].unique():
                    color = CLASS_CONFIG['colors'][classe]
                    st.markdown(f"""
                    <div class="card" style="border-color: {color}; background: {color}22; margin: 10px 0;">
                        <div style="font-size: 1.5rem; margin-bottom: 5px;">{classe.split()[0]}</div>
                        <div style="font-weight: bold;">{classe}</div>
                        <div style="font-size: 12px; margin-top: 5px;">{CLASS_CONFIG['descriptions'][classe]}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ Nenhum dado encontrado")
    else:
        if not ee_initialized:
            st.error("❌ Earth Engine não conectado")
        elif not selected_years:
            st.error("⚠️ Selecione um ano")
        else:
            st.error("❌ Área de estudo não definida")

# 🔧 CORREÇÃO: Remover st.balloons() que causa problemas
# (mantenha o resto do código igual...)

# [O RESTANTE DO CÓDIGO PERMANECE EXATAMENTE IGUAL...]
# Apenas copie e cole as outras abas (tab2, tab3, tab4) e o footer
# do seu código original, pois eles já estão bons!

with tab2:
    st.markdown("## 📊 **COMPARAÇÃO DOS ANOS**")
    
    if ee_initialized and geometry:
        df_temporal = calculate_statistics(geometry, anos_especificos, selected_class_codes)
        
        if not df_temporal.empty:
            st.markdown("### 🏆 **COMPETIÇÃO DAS ÁREAS**")
            
            bar_fig = px.bar(
                df_temporal,
                x="Ano",
                y="Área (km²)", 
                color="Nome da Classe",
                barmode="group",
                title="Como as áreas mudaram ao longo dos anos?",
                color_discrete_map=CLASS_CONFIG['colors'],
                height=500
            )
            bar_fig.update_layout(
                font=dict(size=14),
                xaxis_title="Ano",
                yaxis_title="Área (km²)",
                xaxis={'type': 'category'}
            )
            st.plotly_chart(bar_fig, use_container_width=True)
            
            st.markdown("### 📈 **AVENTURA DAS MUDANÇAS**")
            
            line_fig = px.line(
                df_temporal,
                x="Ano",
                y="Área (km²)",
                color="Nome da Classe",
                markers=True,
                title="A jornada de cada tipo de área",
                color_discrete_map=CLASS_CONFIG['colors'],
                height=500
            )
            line_fig.update_layout(
                font=dict(size=12),
                xaxis_title="Ano",
                yaxis_title="Área (km²)"
            )
            st.plotly_chart(line_fig, use_container_width=True)

with tab3:
    st.markdown("## 🗺️ **MAPA DA AVENTURA**")
    
    if ee_initialized and geometry and selected_years and remapped_image:
        try:
            m = geemap.Map(center=[-4.5, -45], zoom=8)
            
            study_area = ee.FeatureCollection([ee.Feature(geometry)])
            m.centerObject(study_area, zoom=10)
            m.addLayer(study_area, {'color': 'red', 'width': 3}, 'Santa Luzia')
            
            selected_year = selected_years[0]
            selected_band = f"classification_{selected_year}"
            
            m.addLayer(
                remapped_image.select(selected_band).clip(geometry),
                {
                    'palette': CLASS_CONFIG['palette'],
                    'min': 1,
                    'max': 6
                },
                f"Mapa {selected_year}"
            )
            
            m.add_legend(
                title="Legenda",
                legend_dict=CLASS_CONFIG['names'],
                position='bottomright'
            )
            
            m.to_streamlit(height=500)
            
            # Botão de captura
            st.markdown("### 📸 **CAPTURAR MAPA**")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col2:
                if st.button("🖼️ **Capturar Mapa como Foto**", use_container_width=True):
                    save_map_as_image(m)
            
        except Exception as e:
            st.error(f"❌ Erro ao carregar o mapa: {str(e)}")
    else:
        st.error("⚠️ Recursos não disponíveis para carregar o mapa")

with tab4:
    st.markdown("## 📋 **NOSSO BAÚ DE DADOS**")
    
    if ee_initialized and geometry and selected_years:
        df = calculate_statistics(geometry, selected_years, selected_class_codes)
        
        if not df.empty:
            pivot_table = df.pivot_table(
                index='Ano', 
                columns='Nome da Classe', 
                values='Área (km²)', 
                aggfunc='sum'
            ).round(1)
            
            pivot_table['TOTAL'] = pivot_table.sum(axis=1)
            
            st.markdown("### 📊 **TABELA DOS EXPLORADORES**")
            st.dataframe(pivot_table, use_container_width=True)
            
            csv_data = df.to_csv(index=False)
            st.download_button(
                label="📥 **BAIXAR NOSSA PESQUISA**",
                data=csv_data,
                file_name=f"aventura_ecologica_santa_luzia_{selected_years[0]}.csv",
                mime="text/csv"
            )

# Rodapé
st.markdown("---")
st.markdown(
    "<div style='text-align: center; background: linear-gradient(135deg, #2E8B57, #32CD32); "
    "color: white; padding: 20px; border-radius: 20px; margin-top: 20px;'>"
    "<h2>🌟 VOCÊ É UM EXPLORADOR DA NATUREZA! 🌟</h2>"
    "<p style='font-size: 16px;'>Cada descoberta nos ajuda a cuidar melhor do nosso planeta!</p>"
    "<p style='font-size: 14px;'>💚 <strong>Explore, aprenda e preserve!</strong> 💚</p>"
    f"<p style='margin-top: 15px;'><small>Aventura atualizada em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}</small></p>"
    "</div>",
    unsafe_allow_html=True
)