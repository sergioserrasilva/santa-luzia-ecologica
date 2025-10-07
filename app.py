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

# 🔧 CORREÇÃO: Configuração CORRETA das classes do MapBiomas Collection 10
CLASS_CONFIG = {
    # Mapeamento das classes principais do MapBiomas para classes simplificadas
    'class_mapping': {
        # Floresta (1)
        1: 1,    # Floresta
        3: 1,    # Formação Florestal
        4: 1,    # Formação Savânica
        5: 1,    # Mangue
        6: 1,    # Floresta Alagável
        # Formação Natural (2)
        10: 2,   # Formação Campestre
        11: 2,   # Campo Alagado
        12: 2,   # Estepe
        32: 2,   # Apicum
        29: 2,   # Afloramento Rochoso
        13: 2,   # Outra Formação Natural
        # Agropecuária (3)
        14: 3,   # Pastagem
        15: 3,   # Agricultura
        18: 3,   # Agricultura Perene
        19: 3,   # Soja
        39: 3,   # Soja Milho
        20: 3,   # Cana
        40: 3,   # Cana Soja
        62: 3,   # Café
        41: 3,   # Outras Lavouras Temporárias
        36: 3,   # Lavoura Perene
        46: 3,   # Mosaico de Agricultura e Pastagem
        # Área Urbana (4)
        21: 4,   # Área Urbana
        23: 4,   # Outra Área Não Vegetada
        24: 4,   # Mineração
        30: 4,   # Praia e Duna
        25: 4,   # Infraestrutura Urbana
        # Água (5)
        26: 5,   # Rio, Lago e Oceano
        33: 5,   # Aquicultura
        31: 5,   # Corpo D'água
        # Outros (6) - classes restantes
        27: 6,   # Não Observado
        34: 6,   # Outros
    },
    
    'names': {
        1: "🌳 Floresta", 
        2: "🌾 Formação Natural", 
        3: "🚜 Agropecuária", 
        4: "🏙️ Área Urbana", 
        5: "💧 Água", 
        6: "❓ Outros"
    },
    
    # 🔧 CORREÇÃO: Cores oficiais do MapBiomas para as classes principais
    'colors': {
        "🌳 Floresta": "#1f8d49",        # Verde floresta
        "🌾 Formação Natural": "#d6bc74", # Amarelo campo
        "🚜 Agropecuária": "#ffef5c",    # Amarelo agricultura
        "🏙️ Área Urbana": "#d4271e",     # Vermelho urbano
        "💧 Água": "#2532e4",            # Azul água
        "❓ Outros": "#cccccc"           # Cinza outros
    },
    
    'descriptions': {
        "🌳 Floresta": "Florestas naturais e matas! 🌳",
        "🌾 Formação Natural": "Campos naturais e vegetação rasteira!", 
        "🚜 Agropecuária": "Áreas de agricultura e pastagem! 🚜",
        "🏙️ Área Urbana": "Cidades, estradas e construções! 🏠",
        "💧 Água": "Rios, lagos e oceanos! 💦",
        "❓ Outros": "Áreas não mapeadas ou sem informação! ✨"
    },
    
    # 🔧 CORREÇÃO: Paleta de cores OFICIAL do MapBiomas para visualização
    'mapbiomas_palette': [
        "#129912",  # 1 - Floresta
        "#1f8d49",  # 3 - Formação Florestal  
        "#006400",  # 4 - Formação Savânica
        "#00ff00",  # 5 - Mangue
        "#687537",  # 6 - Floresta Alagável
        "#45c2a5",  # 10 - Formação Campestre
        "#b8af4f",  # 11 - Campo Alagado
        "#bbfcac",  # 12 - Estepe
        "#b8ffeb",  # 32 - Apicum
        "#caa5af",  # 29 - Afloramento Rochoso
        "#fffc99",  # 13 - Outra Formação Natural
        "#ffd966",  # 14 - Pastagem
        "#ffef5c",  # 15 - Agricultura
        "#e974ed",  # 18 - Agricultura Perene
        "#e4ff4f",  # 19 - Soja
        "#ffff4c",  # 39 - Soja Milho
        "#d4271e",  # 20 - Cana
        "#ea6666",  # 40 - Cana Soja
        "#a5b88c",  # 62 - Café
        "#ffffb2",  # 41 - Outras Lavouras Temporárias
        "#af8e19",  # 36 - Lavoura Perene
        "#fff3b2",  # 46 - Mosaico Agricultura e Pastagem
        "#ff0000",  # 21 - Área Urbana
        "#555555",  # 23 - Outra Área Não Vegetada
        "#888888",  # 24 - Mineração
        "#ffffbe",  # 30 - Praia e Duna
        "#c00000",  # 25 - Infraestrutura Urbana
        "#0000ff",  # 26 - Rio, Lago e Oceano
        "#a59bcc",  # 33 - Aquicultura
        "#66a3ff",  # 31 - Corpo D'água
        "#ffffff",  # 27 - Não Observado
        "#cccccc"   # 34 - Outros
    ]
}

# 🔧 CORREÇÃO: Carregamento robusto do GeoJSON com tratamento de encoding
@st.cache_data
def load_geojson():
    """Carrega o GeoJSON com tratamento robusto de encoding"""
    try:
        # Tentar diferentes encodings
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open('assets/municipios_ma.geojson', 'r', encoding=encoding) as f:
                    geojson_data = json.load(f)
                
                # Verificar se encontrou Santa Luzia
                santa_luzia_features = []
                for feature in geojson_data['features']:
                    nome = feature['properties'].get('NM_MUNICIP', '') or feature['properties'].get('nome', '')
                    if nome and 'SANTA LUZIA' in nome.upper():
                        santa_luzia_features.append(feature)
                
                if santa_luzia_features:
                    st.success(f"✅ GeoJSON carregado com encoding {encoding}! Santa Luzia encontrada.")
                    return geojson_data, santa_luzia_features
                    
            except UnicodeDecodeError:
                continue
            except Exception as e:
                continue
        
        # Se nenhum encoding funcionou, tentar modo binário
        try:
            with open('assets/municipios_ma.geojson', 'rb') as f:
                content = f.read().decode('utf-8', errors='ignore')
                geojson_data = json.loads(content)
                
                santa_luzia_features = []
                for feature in geojson_data['features']:
                    nome = feature['properties'].get('NM_MUNICIP', '') or feature['properties'].get('nome', '')
                    if nome and 'SANTA LUZIA' in nome.upper():
                        santa_luzia_features.append(feature)
                
                if santa_luzia_features:
                    st.success("✅ GeoJSON carregado com tratamento de erros! Santa Luzia encontrada.")
                    return geojson_data, santa_luzia_features
                    
        except Exception as e:
            st.error(f"❌ Erro crítico ao carregar GeoJSON: {str(e)}")
            
        return None, []
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar GeoJSON: {str(e)}")
        return None, []

# Carregar GeoJSON
geojson_data, santa_luzia_features = load_geojson()

# 🔧 CORREÇÃO: Função simplificada para criar geometria de Santa Luzia
def get_santa_luzia_geometry():
    """Obtém a geometria de Santa Luzia de forma robusta"""
    if not santa_luzia_features:
        # Se não encontrou no GeoJSON, usar coordenadas aproximadas
        st.warning("⚠️ Usando coordenadas aproximadas de Santa Luzia")
        return ee.Geometry.Rectangle([-45.8, -4.3, -45.2, -3.9])
    
    try:
        # Usar a primeira feature de Santa Luzia encontrada
        geometry = santa_luzia_features[0]['geometry']
        return ee.Geometry(geometry)
    except Exception as e:
        st.warning(f"⚠️ Erro na geometria, usando fallback: {str(e)}")
        return ee.Geometry.Rectangle([-45.8, -4.3, -45.2, -3.9])

# 🔧 CORREÇÃO: Carregar MapBiomas Collection 10 (CORRETO)
mapbiomas_image = None
if ee_initialized:
    try:
        # Usar a Collection 10 que você forneceu
        mapbiomas_image = ee.Image('projects/mapbiomas-public/assets/brazil/lulc/collection10/mapbiomas_brazil_collection10_integration_v2')
        st.sidebar.success("✅ MapBiomas Collection 10 carregado!")
        
        # Verificar as bandas disponíveis
        bandas = mapbiomas_image.bandNames().getInfo()
        st.sidebar.info(f"📊 Bandas disponíveis: {len(bandas)} anos (1985-2023)")
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar MapBiomas Collection 10: {str(e)}")
        st.info("💡 Verifique se o asset está correto e acessível")

# Sidebar interativa
st.sidebar.markdown("## 🎮 **PAINEL DO EXPLORADOR**")

# Seletor de anos com botões específicos
st.sidebar.markdown("### 🗓️ **ESCOLHA O ANO**")
st.sidebar.markdown("**Clique em um ano para explorar:**")

# Anos específicos solicitados
anos_especificos = [1985, 2000, 2010, 2022, 2023]

# Inicializar session state para anos selecionados
if 'selected_years' not in st.session_state:
    st.session_state.selected_years = [2023]

# Criar botões para os anos específicos
cols = st.sidebar.columns(3)

botao_idx = 0
for col_idx in range(3):
    with cols[col_idx]:
        for _ in range(2 if col_idx < 2 else 1):
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
    st.sidebar.markdown(f"<div style='background: linear-gradient(135deg, #90EE90, #32CD32); color: white; padding: 10px; border-radius: 10px; text-align: center;'><strong>🚀 Explorando {ano_selecionado}!</strong></div>", unsafe_allow_html=True)

# Seletor de classes de cobertura
st.sidebar.markdown("### 🌟 **LUGARES PARA EXPLORAR**")
all_classes = list(CLASS_CONFIG['names'].values())
selected_class_names = st.sidebar.multiselect(
    "Escolha os tipos de lugares:",
    options=all_classes,
    default=all_classes,
    format_func=lambda x: f"{x}"
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

# Obter geometria de Santa Luzia
geometry = get_santa_luzia_geometry()

# Usar anos selecionados do session state
selected_years = st.session_state.selected_years

# 🔧 CORREÇÃO: Função para reclassificar imagem do MapBiomas
def reclassify_mapbiomas(image, year):
    """Reclassifica a imagem do MapBiomas para classes simplificadas"""
    try:
        band_name = f'classification_{year}'
        original_band = image.select(band_name)
        
        # Criar lista de códigos originais e novos códigos
        from_codes = []
        to_codes = []
        
        for orig_code, new_code in CLASS_CONFIG['class_mapping'].items():
            from_codes.append(orig_code)
            to_codes.append(new_code)
        
        # Aplicar reclassificação
        reclassified = original_band.remap(from_codes, to_codes)
        return reclassified.rename(band_name)
    
    except Exception as e:
        st.error(f"Erro na reclassificação: {e}")
        return None

# 🔧 CORREÇÃO COMPLETA: Função robusta para cálculo de estatísticas
# 🔧 CORREÇÃO COMPLETA: Função robusta para cálculo de estatísticas
def calculate_statistics(_geometry, _selected_years, _selected_class_codes):
    """Calcula estatísticas de forma robusta usando MapBiomas Collection 10"""
    if not ee_initialized or not _geometry or mapbiomas_image is None:
        st.error("❌ Earth Engine não inicializado ou geometria não disponível")
        return pd.DataFrame()
        
    stats_data = []
    
    for year in _selected_years:
        try:
            st.info(f"🔄 Processando ano {year}...")
            
            # 🔧 CORREÇÃO: Usar a banda específica do ano diretamente
            band_name = f'classification_{year}'
            
            # Verificar se a banda existe
            bandas_disponiveis = mapbiomas_image.bandNames().getInfo()
            if band_name not in bandas_disponiveis:
                st.warning(f"⚠️ Banda {band_name} não disponível. Bandas: {bandas_disponiveis}")
                continue
            
            # Obter a banda original
            original_band = mapbiomas_image.select(band_name).clip(_geometry)
            
            # 🔧 CORREÇÃO: Calcular área total da geometria primeiro
            area_total_pixels = ee.Image.pixelArea().clip(_geometry).reduceRegion(
                reducer=ee.Reducer.sum(),
                geometry=_geometry,
                scale=100,
                maxPixels=1e11,
                bestEffort=True
            ).getInfo()
            
            area_total_m2 = area_total_pixels.get('area', 0)
            area_total_km2 = area_total_m2 / 1e6
            
            st.info(f"📐 Área total de Santa Luzia: {area_total_km2:.2f} km²")
            
            # 🔧 CORREÇÃO: Calcular área para cada classe
            for class_code in _selected_class_codes:
                try:
                    # 🔧 CORREÇÃO: Mapear classe simplificada para classes MapBiomas originais
                    classes_originais = [orig_code for orig_code, simpl_code in CLASS_CONFIG['class_mapping'].items() 
                                       if simpl_code == class_code]
                    
                    if not classes_originais:
                        st.warning(f"⚠️ Nenhuma classe original encontrada para {class_code}")
                        continue
                    
                    # Criar máscara para todas as classes originais que mapeiam para esta classe simplificada
                    class_mask = original_band.eq(classes_originais[0])
                    for class_orig in classes_originais[1:]:
                        class_mask = class_mask.Or(original_band.eq(class_orig))
                    
                    # Calcular área em metros quadrados
                    area_image = ee.Image.pixelArea().updateMask(class_mask)
                    
                    # Reduzir região para obter a área total
                    area_result = area_image.reduceRegion(
                        reducer=ee.Reducer.sum(),
                        geometry=_geometry,
                        scale=100,
                        maxPixels=1e11,
                        bestEffort=True
                    )
                    
                    # Obter o valor da área
                    area_info = area_result.getInfo()
                    area_m2 = area_info.get('area', 0) if area_info else 0
                    area_km2 = area_m2 / 1e6
                    
                    # 🔧 CORREÇÃO: Verificar se a área é válida (não pode ser maior que área total)
                    if area_km2 > area_total_km2 * 1.1:  # 10% de tolerância
                        st.warning(f"⚠️ Área suspeita para {CLASS_CONFIG['names'][class_code]}: {area_km2:.2f} km² (ajustando)")
                        area_km2 = min(area_km2, area_total_km2)
                    
                    # 🔧 CORREÇÃO: Calcular porcentagem
                    porcentagem = (area_km2 / area_total_km2 * 100) if area_total_km2 > 0 else 0
                    
                    stats_data.append({
                        "Ano": year,
                        "Classe": class_code,
                        "Nome da Classe": CLASS_CONFIG['names'][class_code],
                        "Área (km²)": round(area_km2, 2),
                        "Porcentagem (%)": round(porcentagem, 1)
                    })
                    
                    st.success(f"✅ {year} - {CLASS_CONFIG['names'][class_code]}: {area_km2:.2f} km² ({porcentagem:.1f}%)")
                    
                except Exception as class_error:
                    st.error(f"❌ Erro na classe {class_code} - {year}: {str(class_error)}")
                    # Adicionar valor zero em caso de erro
                    stats_data.append({
                        "Ano": year,
                        "Classe": class_code,
                        "Nome da Classe": CLASS_CONFIG['names'][class_code],
                        "Área (km²)": 0.0,
                        "Porcentagem (%)": 0.0
                    })
                
        except Exception as e:
            st.error(f"❌ Erro ao processar {year}: {str(e)}")
            # Adicionar dados zerados para não quebrar a interface
            for class_code in _selected_class_codes:
                stats_data.append({
                    "Ano": year,
                    "Classe": class_code,
                    "Nome da Classe": CLASS_CONFIG['names'][class_code],
                    "Área (km²)": 0.0,
                    "Porcentagem (%)": 0.0
                })
            continue
    
    df = pd.DataFrame(stats_data)
    
    # 🔧 CORREÇÃO: Verificar se os dados fazem sentido
    if not df.empty:
        total_area_calculada = df['Área (km²)'].sum()
        if total_area_calculada == 0:
            st.warning("⚠️ Todas as áreas calculadas são zero. Verifique a geometria e os dados.")
        else:
            st.success(f"✅ Cálculos concluídos! Área total calculada: {total_area_calculada:.2f} km²")
    
    return df

# 🔧 CORREÇÃO COMPLETA: Função robusta para cálculo de estatísticas
def calculate_statistics(_geometry, _selected_years, _selected_class_codes):
    """Calcula estatísticas de forma robusta usando MapBiomas Collection 10"""
    if not ee_initialized or not _geometry or mapbiomas_image is None:
        st.error("❌ Earth Engine não inicializado ou geometria não disponível")
        return pd.DataFrame()
        
    stats_data = []
    
    for year in _selected_years:
        try:
            # 🔧 CORREÇÃO: Removida mensagem de processamento individual
            band_name = f'classification_{year}'
            
            # Verificar se a banda existe
            bandas_disponiveis = mapbiomas_image.bandNames().getInfo()
            if band_name not in bandas_disponiveis:
                st.warning(f"⚠️ Banda {band_name} não disponível. Bandas: {bandas_disponiveis}")
                continue
            
            # Obter a banda original
            original_band = mapbiomas_image.select(band_name).clip(_geometry)
            
            # 🔧 CORREÇÃO: Calcular área total da geometria primeiro
            area_total_pixels = ee.Image.pixelArea().clip(_geometry).reduceRegion(
                reducer=ee.Reducer.sum(),
                geometry=_geometry,
                scale=100,
                maxPixels=1e11,
                bestEffort=True
            ).getInfo()
            
            area_total_m2 = area_total_pixels.get('area', 0)
            area_total_km2 = area_total_m2 / 1e6
            
            # 🔧 CORREÇÃO: Calcular área para cada classe
            for class_code in _selected_class_codes:
                try:
                    # 🔧 CORREÇÃO: Mapear classe simplificada para classes MapBiomas originais
                    classes_originais = [orig_code for orig_code, simpl_code in CLASS_CONFIG['class_mapping'].items() 
                                       if simpl_code == class_code]
                    
                    if not classes_originais:
                        continue
                    
                    # Criar máscara para todas as classes originais que mapeiam para esta classe simplificada
                    class_mask = original_band.eq(classes_originais[0])
                    for class_orig in classes_originais[1:]:
                        class_mask = class_mask.Or(original_band.eq(class_orig))
                    
                    # Calcular área em metros quadrados
                    area_image = ee.Image.pixelArea().updateMask(class_mask)
                    
                    # Reduzir região para obter a área total
                    area_result = area_image.reduceRegion(
                        reducer=ee.Reducer.sum(),
                        geometry=_geometry,
                        scale=100,
                        maxPixels=1e11,
                        bestEffort=True
                    )
                    
                    # Obter o valor da área
                    area_info = area_result.getInfo()
                    area_m2 = area_info.get('area', 0) if area_info else 0
                    area_km2 = area_m2 / 1e6
                    
                    # 🔧 CORREÇÃO: Verificar se a área é válida (não pode ser maior que área total)
                    if area_km2 > area_total_km2 * 1.1:  # 10% de tolerância
                        area_km2 = min(area_km2, area_total_km2)
                    
                    # 🔧 CORREÇÃO: Calcular porcentagem
                    porcentagem = (area_km2 / area_total_km2 * 100) if area_total_km2 > 0 else 0
                    
                    stats_data.append({
                        "Ano": year,
                        "Classe": class_code,
                        "Nome da Classe": CLASS_CONFIG['names'][class_code],
                        "Área (km²)": round(area_km2, 2),
                        "Porcentagem (%)": round(porcentagem, 1)
                    })
                    
                    # 🔧 CORREÇÃO: Removida mensagem individual de sucesso
                    
                except Exception as class_error:
                    # Adicionar valor zero em caso de erro
                    stats_data.append({
                        "Ano": year,
                        "Classe": class_code,
                        "Nome da Classe": CLASS_CONFIG['names'][class_code],
                        "Área (km²)": 0.0,
                        "Porcentagem (%)": 0.0
                    })
                
        except Exception as e:
            # Adicionar dados zerados para não quebrar a interface
            for class_code in _selected_class_codes:
                stats_data.append({
                    "Ano": year,
                    "Classe": class_code,
                    "Nome da Classe": CLASS_CONFIG['names'][class_code],
                    "Área (km²)": 0.0,
                    "Porcentagem (%)": 0.0
                })
            continue
    
    df = pd.DataFrame(stats_data)
    
    # 🔧 CORREÇÃO: Removida mensagem de conclusão que causava duplicação
    return df

# 🔧 CORREÇÃO: Função para visualização do mapa com Santa Luzia POR CIMA
# 🔧 CORREÇÃO: Função para visualização do mapa com Santa Luzia POR CIMA
def create_map_safe(year, geometry):
    """Cria mapa de forma segura usando MapBiomas Collection 10 com Santa Luzia destacada"""
    try:
        # Criar mapa
        m = geemap.Map(center=[-4.1, -45.5], zoom=10)
        
        # 🔧 CORREÇÃO: Usar a imagem ORIGINAL do MapBiomas com paleta oficial
        band_name = f'classification_{year}'
        original_image = mapbiomas_image.select(band_name).clip(geometry)
        
        # Adicionar camada do MapBiomas com paleta OFICIAL (PRIMEIRA camada)
        m.addLayer(
            original_image,
            {
                'min': 1,
                'max': 34,  # Máximo de classes no MapBiomas
                'palette': CLASS_CONFIG['mapbiomas_palette']
            },
            f"MapBiomas {year} (Cores Oficiais)"
        )
        
        # 🔧 CORREÇÃO: Adicionar contorno de Santa Luzia POR CIMA (SEGUNDA camada)
        outline = ee.FeatureCollection([ee.Feature(geometry)])
        m.addLayer(
            outline, 
            {
                'color': '#FF0000',  # Vermelho vivo
                'width': 4,          # Linha mais grossa
                'fillColor': '00000000'  # Transparente por dentro
            }, 
            '📍 Santa Luzia'
        )
        
        # 🔧 CORREÇÃO: Adicionar camada reclassificada para análise (opcional)
        reclassified_image = reclassify_mapbiomas(mapbiomas_image, year)
        if reclassified_image is not None:
            reclassified_clipped = reclassified_image.clip(geometry)
            m.addLayer(
                reclassified_clipped,
                {
                    'min': 1,
                    'max': 6,
                    'palette': ["#1f8d49", "#d6bc74", "#ffef5c", "#d4271e", "#2532e4", "#cccccc"]
                },
                f"Classes Simplificadas {year}",
                False  # Inicialmente desativada
            )
        
        # 🔧 CORREÇÃO: Legenda customizada sem usar template
        legend_html = """
        <div style="position: fixed; 
                    bottom: 50px; 
                    right: 50px; 
                    background-color: white; 
                    border: 2px solid grey; 
                    border-radius: 10px; 
                    padding: 10px; 
                    z-index: 1000;
                    font-family: 'Comic Sans MS', cursive;">
            <h4 style="margin: 0 0 10px 0; text-align: center;">🌱 Tipos de Cobertura</h4>
        """
        
        # Adicionar itens da legenda
        for code, name in CLASS_CONFIG['names'].items():
            color = CLASS_CONFIG['colors'][name]
            legend_html += f"""
            <div style="display: flex; align-items: center; margin: 5px 0;">
                <div style="width: 20px; height: 20px; background-color: {color}; border: 1px solid black; margin-right: 8px;"></div>
                <span style="font-size: 12px;">{name}</span>
            </div>
            """
        
        legend_html += "</div>"
        
        # Adicionar legenda ao mapa
        m.add_child(folium.Element(legend_html))
        
        return m
        
    except Exception as e:
        st.error(f"❌ Erro ao criar mapa: {str(e)}")
        # Retornar mapa básico mesmo com erro
        m = geemap.Map(center=[-4.1, -45.5], zoom=10)
        outline = ee.FeatureCollection([ee.Feature(geometry)])
        m.addLayer(outline, {'color': 'red', 'width': 4}, 'Santa Luzia')
        return m

# 🆕 NOVA FUNÇÃO: Função idêntica para exibir o panorama
# 🆕 FUNÇÃO MELHORADA: Função para exibir o panorama com dados mais robustos
def display_panorama_tab(geometry, selected_years, selected_class_codes):
    """Exibe o panorama de Santa Luzia de forma idêntica ao solicitado"""
    st.markdown("## 🎯 **PANORAMA DE SANTA LUZIA**")
    
    if geometry and selected_years:
        # 🔧 CORREÇÃO: Removido spinner duplicado - o cálculo já tem seu próprio feedback
        df = calculate_statistics(geometry, selected_years, selected_class_codes)
        
        if not df.empty and df['Área (km²)'].sum() > 0:
            latest_year = selected_years[0]  # Apenas um ano selecionado
            latest_data = df[df['Ano'] == latest_year]
            
            st.markdown(f"### 📊 **FOTOGRAFIA DE {latest_year}**")
            
            # Métricas principais
            cols = st.columns(3)
            
            # Ordenar por área para mostrar as maiores primeiro
            latest_data_sorted = latest_data.sort_values('Área (km²)', ascending=False)
            
            # Mostrar as 3 maiores áreas
            for col, (idx, row) in zip(cols, latest_data_sorted.head(3).iterrows()):
                with col:
                    nome = row['Nome da Classe']
                    valor = row['Área (km²)']
                    porcentagem = row['Porcentagem (%)']
                    emoji = nome.split()[0]  # Pega o emoji do nome
                    
                    st.markdown(
                        f'<div class="metric-card">'
                        f'<div style="font-size: 3rem;">{emoji}</div>'
                        f'<div style="font-size: 1.3rem; font-weight: bold;">{nome}</div>'
                        f'<div style="font-size: 2rem; margin-top: 15px;">{valor:.0f} km²</div>'
                        f'<div style="font-size: 1.2rem; margin-top: 10px;">{porcentagem}% do total</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
            
            # Gráfico de pizza
            st.markdown("### **COMO ESTÁ DIVIDIDA NOSSA TERRA?**")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Filtrar classes com área > 0 para o gráfico
                data_for_chart = latest_data[latest_data['Área (km²)'] > 0]
                
                if not data_for_chart.empty:
                    pie_fig = px.pie(
                        data_for_chart,
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
                else:
                    st.warning("📊 Nenhuma área significativa encontrada para exibir no gráfico")
            
            with col2:
                st.markdown("#### 📖 **HISTÓRIA DE CADA LUGAR**")
                
                # Ordenar por área para uma melhor visualização
                for _, row in latest_data_sorted.iterrows():
                    classe = row['Nome da Classe']
                    area = row['Área (km²)']
                    porcentagem = row['Porcentagem (%)']
                    color = CLASS_CONFIG['colors'][classe]
                    
                    st.markdown(f"""
                    <div class="class-card" style="border-color: {color}; background: {color}22;">
                        <div style="font-size: 2rem; margin-bottom: 10px;">{classe.split()[0]}</div>
                        <div style="font-weight: bold; font-size: 16px;">{classe}</div>
                        <div style="font-size: 14px; margin-top: 5px;">{CLASS_CONFIG['descriptions'][classe]}</div>
                        <div style="font-size: 12px; margin-top: 8px; background: {color}44; padding: 5px; border-radius: 10px;">
                            📏 <strong>{area:.1f} km²</strong> ({porcentagem}%)
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # 🔧 CORREÇÃO: Adicionar resumo estatístico
            st.markdown("### 📈 **RESUMO ESTATÍSTICO**")
            
            total_area = latest_data['Área (km²)'].sum()
            maior_classe = latest_data_sorted.iloc[0]
            menor_classe = latest_data_sorted[latest_data_sorted['Área (km²)'] > 0].iloc[-1]
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(
                    f'<div class="info-box">'
                    f'<h4>🌍 Área Total</h4>'
                    f'<p style="font-size: 24px; font-weight: bold; color: #2E8B57;">{total_area:.2f} km²</p>'
                    f'<p>Superfície total mapeada</p>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            
            with col2:
                st.markdown(
                    f'<div class="info-box">'
                    f'<h4>👑 Maior Área</h4>'
                    f'<p style="font-size: 20px; font-weight: bold; color: #2E8B57;">{maior_classe["Nome da Classe"]}</p>'
                    f'<p>{maior_classe["Área (km²)"]:.1f} km² ({maior_classe["Porcentagem (%)"]}%)</p>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            
            with col3:
                if len(latest_data_sorted[latest_data_sorted['Área (km²)'] > 0]) > 1:
                    st.markdown(
                        f'<div class="info-box">'
                        f'<h4>🔍 Menor Área</h4>'
                        f'<p style="font-size: 20px; font-weight: bold; color: #2E8B57;">{menor_classe["Nome da Classe"]}</p>'
                        f'<p>{menor_classe["Área (km²)"]:.1f} km² ({menor_classe["Porcentagem (%)"]}%)</p>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f'<div class="info-box">'
                        f'<h4>🔍 Dados</h4>'
                        f'<p style="font-size: 20px; font-weight: bold; color: #2E8B57;">{len(latest_data)} classes</p>'
                        f'<p>diferentes encontradas</p>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                    
        else:
            st.warning("""
            ⚠️ **Nenhum dado significativo encontrado!**
            
            Isso pode acontecer por vários motivos:
            - O Earth Engine pode estar offline
            - A geometria de Santa Luzia não foi carregada corretamente
            - O MapBiomas pode não ter dados para esta área/ano
            - As classes selecionadas não existem na área
            
            **💡 Dicas para resolver:**
            1. Verifique se o Earth Engine está inicializado
            2. Confirme que o arquivo GeoJSON foi carregado
            3. Tente selecionar diferentes anos ou classes
            4. Recarregue a página
            """)
    else:
        if not selected_years:
            st.error("⚠️ Selecione um ano na sidebar para ver o panorama")
        else:
            st.error("❌ Área de estudo não definida. Verifique o carregamento do município.")

# Layout principal com abas
tab1, tab2, tab3, tab4 = st.tabs(["🎯 VISÃO GERAL", "📊 GRÁFICOS", "🗺️ MAPA", "📋 DADOS"])

with tab1:
    # 🔧 USANDO A NOVA FUNÇÃO
    display_panorama_tab(geometry, selected_years, selected_class_codes)

with tab2:
    st.markdown("## 📊 **COMPARAÇÃO DOS ANOS**")
    
    if geometry:
        # Para análise temporal, vamos usar todos os 5 anos para comparação
        with st.spinner("🔄 Calculando dados temporais..."):
            df_temporal = calculate_statistics(geometry, anos_especificos, selected_class_codes)
        
        if not df_temporal.empty and df_temporal['Área (km²)'].sum() > 0:
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
        else:
            st.warning("⚠️ Nenhum dado disponível para comparação temporal")

with tab3:
    st.markdown("## 🗺️ **MAPA DA AVENTURA**")
    
    if ee_initialized and geometry and selected_years:
        try:
            selected_year = selected_years[0]
            
            with st.spinner("🔄 Carregando mapa..."):
                m = create_map_safe(selected_year, geometry)
            
            if m:
                m.to_streamlit(height=600)
                st.success(f"✅ Mapa de Santa Luzia carregado para {selected_year}!")
                
                # Instruções sobre as cores
                st.markdown("### 🎨 **SOBRE AS CORES DO MAPA:**")
                st.info("""
                **🌊 Azul:** Rios, lagos e oceanos  
                **🌳 Verde:** Florestas e matas  
                **🟡 Amarelo:** Campos naturais e agricultura  
                **🔴 Vermelho:** Cidades e áreas urbanas  
                **⚪ Cinza:** Outras áreas
                
                💡 **Dica:** A linha **vermelha grossa** mostra os limites de Santa Luzia!
                """)
                
            else:
                st.error("❌ Não foi possível criar o mapa")
                
        except Exception as e:
            st.error(f"❌ Erro no mapa: {str(e)}")
            st.info("💡 Tente recarregar a página")
    else:
        st.error("❌ Earth Engine não disponível para o mapa")

    # Informações do mapa (sempre visíveis)
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
            f'<div style="font-size: 1.8rem; margin-top: 10px;">100 metros</div>'
            f'</div>',
            unsafe_allow_html=True
        )
        
with tab4:
    st.markdown("## 📋 **NOSSO BAÚ DE DADOS**")
    
    if geometry and selected_years:
        df = calculate_statistics(geometry, selected_years, selected_class_codes)
        
        if not df.empty and df['Área (km²)'].sum() > 0:
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
        else:
            st.warning("⚠️ Nenhum dado disponível para download")
    else:
        st.error("❌ Dados não disponíveis para exportação")

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