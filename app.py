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
import folium

# Configuração inicial
st.set_page_config(
    page_title="ECOLÓGICA - Santa Luzia",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuração para deploy
if not os.path.exists('assets'):
    os.makedirs('assets')

# Inicialização robusta do Earth Engine
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

# CSS personalizado super colorido para crianças
st.markdown("""
<style>
    .main-header {
        font-family: 'Comic Sans MS', cursive;
        font-size: 4rem !important;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 0.2rem;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.2);
        background: linear-gradient(45deg, #2E8B57, #32CD32, #90EE90);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: rainbow 2s ease-in-out infinite alternate;
    }
    .sub-header {
        font-family: 'Comic Sans MS', cursive;
        font-size: 2rem !important;
        color: #228B22;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .card {
        background: linear-gradient(135deg, #f8fff8, #e8f5e8);
        border-radius: 25px;
        padding: 25px;
        border: 4px solid #98FB98;
        box-shadow: 0 10px 20px rgba(0,0,0,0.15);
        margin: 15px 0;
        animation: float 3s ease-in-out infinite;
    }
    .stButton>button {
        background: linear-gradient(45deg, #32CD32, #228B22);
        color: white;
        border-radius: 30px;
        border: none;
        padding: 15px 30px;
        font-weight: bold;
        font-size: 18px;
        font-family: 'Comic Sans MS', cursive;
        transition: all 0.3s;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .stButton>button:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 12px rgba(50, 205, 50, 0.4);
    }
    .metric-card {
        background: linear-gradient(135deg, #90EE90, #32CD32);
        color: white;
        padding: 25px;
        border-radius: 25px;
        text-align: center;
        margin: 10px;
        box-shadow: 0 6px 12px rgba(0,0,0,0.2);
        border: 3px solid white;
        transition: transform 0.3s;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .info-box {
        background: linear-gradient(135deg, #e8f5e8, #d4edda);
        border-left: 8px solid #32CD32;
        padding: 25px;
        margin: 15px 0;
        border-radius: 20px;
        font-size: 18px;
        font-family: 'Comic Sans MS', cursive;
    }
    .fun-fact {
        background: linear-gradient(135deg, #fff3cd, #ffeaa7);
        border: 3px dashed #ffd700;
        padding: 20px;
        margin: 15px 0;
        border-radius: 20px;
        text-align: center;
        font-size: 16px;
        font-family: 'Comic Sans MS', cursive;
    }
    .class-card {
        background: white;
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        border: 3px solid;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        text-align: center;
        color: black !important;
    }
    .class-card * {
        color: black !important;
    }
    .screenshot-btn {
        background: linear-gradient(45deg, #FF6B6B, #FF8E53);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 25px;
        font-weight: bold;
        font-size: 16px;
        cursor: pointer;
        transition: all 0.3s;
        margin: 10px 0;
    }
    .screenshot-btn:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(255, 107, 107, 0.4);
    }
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }
    @keyframes rainbow {
        0% { filter: hue-rotate(0deg); }
        100% { filter: hue-rotate(360deg); }
    }
</style>
""", unsafe_allow_html=True)

# Função para capturar screenshot do mapa
def capture_map_screenshot(m, filename="mapa_santa_luzia.png"):
    try:
        # Salvar o mapa temporariamente
        temp_file = "temp_map.html"
        m.to_html(temp_file)
        
        # Usar selenium para capturar screenshot (requer chromedriver)
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        # Configurar Chrome headless
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1200,800")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(f"file://{os.path.abspath(temp_file)}")
        
        # Esperar o mapa carregar
        driver.implicitly_wait(10)
        
        # Tirar screenshot
        driver.save_screenshot(filename)
        driver.quit()
        
        # Limpar arquivo temporário
        os.remove(temp_file)
        
        return filename
    except Exception as e:
        st.warning(f"⚠️ Não foi possível capturar a screenshot automaticamente: {str(e)}")
        return None


        # Oferecer download do HTML do mapa
        with open(temp_html, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        # Botão para baixar HTML do mapa
        st.download_button(
            label="📁 Baixar Mapa (HTML)",
            data=html_content,
            file_name=f"mapa_santa_luzia_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
            mime="text/html",
            help="Baixe o mapa interativo para visualizar offline"
        )
        
        # Limpar arquivo temporário
        os.remove(temp_html)
        
        return True
    except Exception as e:
        st.error(f"❌ Erro ao processar o mapa: {str(e)}")
        return False

# Função para carregar imagens como base64
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
            f'<div style="text-align: center; animation: float 3s ease-in-out infinite;">'
            f'<img src="data:image/png;base64,{eco_logo}" width="290">'
            f'</div>', 
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div style="text-align: center; font-size: 100px; animation: float 3s ease-in-out infinite;">🌱</div>', 
            unsafe_allow_html=True
        )

with col2:
    st.markdown('<h1 class="main-header">ECOLÓGICA</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header"> Ciência, Dados e Sustentabilidade🌟</p>', unsafe_allow_html=True)

with col3:
    logo_umi = get_image_base64("assets/LOGOUMI.png")
    if logo_umi:
        st.markdown(
            f'<div style="text-align: center; animation: float 3s ease-in-out infinite;">'
            f'<img src="data:image/png;base64,{logo_umi}" width="500">'
            f'</div>', 
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div style="text-align: center; font-size: 100px; animation: float 3s ease-in-out infinite;">🔬</div>', 
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

st.markdown(f'<div class="card" style="font-size: 18px; line-height: 1.6; text-align: center;">{descricao_completa}</div>', unsafe_allow_html=True)

# Configuração das classes do MapBiomas (cores originais e nomes técnicos)
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
        st.success("✅ Arquivo GeoJSON carregado com sucesso!")
        
        # Filtrar apenas Santa Luzia
        santa_luzia_features = []
        for feature in geojson_data['features']:
            nome = feature['properties'].get('NM_MUNICIP', '')
            if 'SANTA LUZIA' in nome.upper():
                santa_luzia_features.append(feature)
        
            
except Exception as e:
    st.error(f"❌ Erro ao carregar GeoJSON: {str(e)}")
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

# Carregar imagem MapBiomas
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
    except Exception as e:
        st.error(f"Erro ao carregar MapBiomas: {e}")

# Sidebar interativa
st.sidebar.markdown("## 🎮 **PAINEL DO EXPLORADOR**")

# Seletor de anos com botões específicos
st.sidebar.markdown("### 🗓️ **ESCOLHA O ANO**")
st.sidebar.markdown("**Clique em um ano para explorar:**")

# Anos específicos solicitados
anos_especificos = [1985, 2000, 2010, 2022, 2023]

# Inicializar session state para anos selecionados
if 'selected_years' not in st.session_state:
    st.session_state.selected_years = [2023]  # Ano mais recente como padrão

# Criar botões para os anos específicos
cols = st.sidebar.columns(3)

# Distribuir os 5 botões em 3 colunas
botoes_por_coluna = [2, 2, 1]  # 2 botões na primeira coluna, 2 na segunda, 1 na terceira

botao_idx = 0
for col_idx, num_botoes in enumerate(botoes_por_coluna):
    with cols[col_idx]:
        for _ in range(num_botoes):
            if botao_idx < len(anos_especificos):
                year = anos_especificos[botao_idx]
                # Verificar se o ano está selecionado
                is_selected = year in st.session_state.selected_years
                button_emoji = "✅" if is_selected else "📅"
                button_label = f"{button_emoji} {year}"
                
                if st.button(button_label, key=f"year_{year}", use_container_width=True):
                    # Limpar seleção anterior e selecionar apenas este ano
                    st.session_state.selected_years = [year]
                    st.rerun()
                
                botao_idx += 1

# Mostrar ano selecionado
if st.session_state.selected_years:
    ano_selecionado = st.session_state.selected_years[0]
    st.sidebar.markdown(f"**🌟 Ano selecionado:** **{ano_selecionado}**")
    st.sidebar.markdown(f"<div style='background: linear-gradient(135deg, #90EE90, #32CD32); color: white; padding: 10px; border-radius: 10px; text-align: center;'><strong>🚀 Explorando {ano_selecionado}!</strong></div>", unsafe_allow_html=True)

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
    # Pegar o primeiro município (que deve ser Santa Luzia)
    municipio_nome = list(MUNICIPIOS_MA.keys())[0]
    geometry = ee.Geometry(MUNICIPIOS_MA[municipio_nome])
    area_name = municipio_nome
    st.sidebar.success(f"📍 Área de Estudo: {area_name}")
else:
    st.sidebar.warning("⚠️ Santa Luzia não encontrado nos dados.")

# Usar anos selecionados do session state
selected_years = st.session_state.selected_years

# Layout principal com abas
tab1, tab2, tab3, tab4 = st.tabs(["🎯 VISÃO GERAL", "📊 GRÁFICOS", "🗺️ MAPA", "📋 DADOS"])

# Função para calcular estatísticas
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
                scale=30,
                maxPixels=1e13
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

with tab1:
    st.markdown("## 🎯 **PANORAMA DE SANTA LUZIA**")
    
    if geometry and selected_years:
        df = calculate_statistics(geometry, selected_years, selected_class_codes)
        
        if not df.empty:
            latest_year = selected_years[0]  # Apenas um ano selecionado
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
                    emoji = nome.split()[0]  # Pega o emoji do nome
                    st.markdown(
                        f'<div class="metric-card">'
                        f'<div style="font-size: 3rem;">{emoji}</div>'
                        f'<div style="font-size: 1.3rem; font-weight: bold;">{nome}</div>'
                        f'<div style="font-size: 2rem; margin-top: 15px;">{valor:.0f} km²</div>'
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
                    hovertemplate="<b>%{label}</b><br>%{percent:.1f}%<br>Área: %{value:.2f} km²",
                    marker=dict(line=dict(color='white', width=2))
                )
                pie_fig.update_layout(
                    font=dict(size=14, family='Comic Sans MS'),
                    showlegend=False
                )
                st.plotly_chart(pie_fig, use_container_width=True)
            
            with col2:
                st.markdown("#### 📖 **HISTÓRIA DE CADA LUGAR**")
                for classe in latest_data['Nome da Classe'].unique():
                    color = CLASS_CONFIG['colors'][classe]
                    
                    st.markdown(f"""
                    <div class="class-card" style="border-color: {color}; background: {color}22;">
                        <div style="font-size: 2rem; margin-bottom: 10px;">{classe.split()[0]}</div>
                        <div style="font-weight: bold; font-size: 16px;">{classe}</div>
                        <div style="font-size: 14px; margin-top: 5px;">{CLASS_CONFIG['descriptions'][classe]}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ Nenhum dado encontrado para os parâmetros selecionados.")
    else:
        if not selected_years:
            st.error("⚠️ Selecione um ano na sidebar")
        else:
            st.error("❌ Área de estudo não definida. Verifique o carregamento do município.")

with tab2:
    st.markdown("## 📊 **COMPARAÇÃO DOS ANOS**")
    
    if geometry:
        # Para análise temporal, vamos usar todos os 5 anos para comparação
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
                font=dict(family='Comic Sans MS', size=14),
                xaxis_title="Ano",
                yaxis_title="Área (km²)",
                xaxis={'type': 'category'}
            )
            st.plotly_chart(bar_fig, use_container_width=True)
            
            # Gráfico de linhas simplificado
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
                font=dict(family='Comic Sans MS', size=12),
                xaxis_title="Ano",
                yaxis_title="Área (km²)"
            )
            st.plotly_chart(line_fig, use_container_width=True)

with tab3:
    st.markdown("## 🗺️ **MAPA DA AVENTURA**")
    
    if ee_initialized and geometry and selected_years and remapped_image:
        try:
            # Mapa básico e estável
            m = geemap.Map(center=[-4.5, -45], zoom=8)
            
            # Adicionar camadas básicas
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
            
            # Legenda simplificada
            m.add_legend(
                title="Legenda",
                legend_dict=CLASS_CONFIG['names'],
                position='bottomright'
            )
            
            # Exibir o mapa
            m.to_streamlit(height=500)
            
            # Instruções simples para salvar
            st.markdown("### 📸 **Como salvar o mapa:**")
            st.info("""
            **Para capturar:**
            - 🖥️ **Computador:** Pressione `Print Screen`
            - 📱 **Celular:** Capture a tela
            - 💡 **Dica:** Ajuste o zoom antes!
            """)
            
        except Exception as e:
            st.error("⚠️ Erro na visualização do mapa")
            st.info("💡 Os dados estão carregados - use as outras abas para análise")
    else:
        st.error("❌ Recursos não disponíveis para carregar o mapa")

    # 🔧 CORREÇÃO: Esta parte deve estar FORA do bloco if/try
    st.markdown("### 📖 **INFORMAÇÕES DO MAPA**")
    
    info_col1, info_col2, info_col3 = st.columns(3)
    
    with info_col1:
        st.markdown(
            f'<div class="metric-card" style="background: linear-gradient(135deg, #87CEEB, #4682B4);">'
            f'<div style="font-size: 2.5rem;">🗓️</div>'
            f'<div style="font-size: 1.1rem; font-weight: bold;">Ano</div>'
            f'<div style="font-size: 1.8rem; margin-top: 10px;">{selected_years[0]}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    
    with info_col2:
        st.markdown(
            f'<div class="metric-card" style="background: linear-gradient(135deg, #90EE90, #32CD32);">'
            f'<div style="font-size: 2.5rem;">🌍</div>'
            f'<div style="font-size: 1.1rem; font-weight: bold;">Área</div>'
            f'<div style="font-size: 1.8rem; margin-top: 10px;">Santa Luzia</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    
    with info_col3:
        st.markdown(
            f'<div class="metric-card" style="background: linear-gradient(135deg, #FFB6C1, #FF69B4);">'
            f'<div style="font-size: 2.5rem;">📏</div>'
            f'<div style="font-size: 1.1rem; font-weight: bold;">Escala</div>'
            f'<div style="font-size: 1.8rem; margin-top: 10px;">30 metros</div>'
            f'</div>',
            unsafe_allow_html=True
        )
        
with tab4:
    st.markdown("## 📋 **NOSSO BAÚ DE DADOS**")
    
    if geometry and selected_years:
        df = calculate_statistics(geometry, selected_years, selected_class_codes)
        
        if not df.empty:
            # Tabela de dados
            pivot_table = df.pivot_table(
                index='Ano', 
                columns='Nome da Classe', 
                values='Área (km²)', 
                aggfunc='sum'
            ).round(1)
            
            # Adicionar totais
            pivot_table['TOTAL'] = pivot_table.sum(axis=1)
            
            st.markdown("### 📊 **TABELA DOS EXPLORADORES**")
            st.dataframe(pivot_table, use_container_width=True)
            
            # Botão de download
            st.markdown("---")
            csv_data = df.to_csv(index=False)
            st.download_button(
                label="📥 **BAIXAR NOSSA PESQUISA**",
                data=csv_data,
                file_name=f"aventura_ecologica_santa_luzia_{selected_years[0]}.csv",
                mime="text/csv",
                help="Baixe os dados para análise em outras ferramentas"
            )

# Rodapé super divertido
st.markdown("---")
st.markdown(
    "<div style='text-align: center; background: linear-gradient(135deg, #2E8B57, #32CD32); "
    "color: white; padding: 30px; border-radius: 25px; margin-top: 30px;'>"
    "<h2>🌟 VOCÊ É UM EXPLORADOR DA NATUREZA! 🌟</h2>"
    "<p style='font-size: 18px;'>Cada descoberta nos ajuda a cuidar melhor do nosso planeta!</p>"
    "<p style='font-size: 16px;'>💚 <strong>Explore, aprenda e preserve!</strong> 💚</p>"
    f"<p style='margin-top: 20px;'><small>Aventura atualizada em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}</small></p>"
    "</div>",
    unsafe_allow_html=True
)