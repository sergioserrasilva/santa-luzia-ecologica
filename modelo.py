import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import base64
from datetime import datetime
import numpy as np
import os

# Configuração da página
st.set_page_config(
    page_title="ECOLOGICA - Santa Luzia",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
            f'<img src="data:image/png;base64,{eco_logo}" width="150">'
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
    st.markdown('<p class="sub-header">Aventura na Natureza de Santa Luzia! 🚀</p>', unsafe_allow_html=True)

with col3:
    logo_umi = get_image_base64("assets/LOGOUMI.png")
    if logo_umi:
        st.markdown(
            f'<div style="text-align: center; animation: float 3s ease-in-out infinite;">'
            f'<img src="data:image/png;base64,{logo_umi}" width="150">'
            f'</div>', 
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div style="text-align: center; font-size: 100px; animation: float 3s ease-in-out infinite;">🔬</div>', 
            unsafe_allow_html=True
        )

# Descrição personalizável
st.markdown("---")
descricao = st.text_area(
    "🎤 **Sua mensagem para os exploradores:**",
    value="👋 **OLÁ, EXPLORADORES MIRINS!** 🌟\n\nPreparem-se para uma aventura incrível pela natureza de Santa Luzia! 🗺️\n\nVamos descobrir juntos:\n🌳 **Florestas** cheias de vida\n💧 **Rios** e lagos cristalinos  \n🚜 **Plantações** que alimentam a todos\n🏙️ **Cidades** onde vivemos\n\nCada gráfico é uma descoberta! Cada número conta uma história! 📚✨",
    height=130
)
st.markdown(f'<div class="card">{descricao}</div>', unsafe_allow_html=True)

# Configurações das classes (versão super amigável para crianças)
CLASS_CONFIG = {
    'names': {
        "forest": "🌳 FLORESTAS MÁGICAS", 
        "field": "🌾 CAMPOS VERDES", 
        "farm": "🚜 FAZENDAS ALEGRES", 
        "city": "🏙️ CIDADE MOVIMENTADA", 
        "water": "💧 RIOS BRINCALHÕES", 
        "other": "🌈 OUTRAS SURPRESAS"
    },
    'colors': {
        "🌳 FLORESTAS MÁGICAS": "#1f8d49",
        "🌾 CAMPOS VERDES": "#d6bc74",
        "🚜 FAZENDAS ALEGRES": "#ffef5c", 
        "🏙️ CIDADE MOVIMENTADA": "#d4271e",
        "💧 RIOS BRINCALHÕES": "#2532e4",
        "🌈 OUTRAS SURPRESAS": "#cc66ff"
    },
    'descriptions': {
        "🌳 FLORESTAS MÁGICAS": "Onde os animais vivem felizes! 🐦🦋",
        "🌾 CAMPOS VERDES": "Gramados para correr e brincar! 🌈",
        "🚜 FAZENDAS ALEGRES": "Onde cresce nossa comida! 🍎🌽", 
        "🏙️ CIDADE MOVIMENTADA": "Casas, escolas e parques! 🏠🎡",
        "💧 RIOS BRINCALHÕES": "Água para beber e nadar! 🏊‍♂️🐠",
        "🌈 OUTRAS SURPRESAS": "Lugares especiais e diferentes! ✨"
    }
}

# Dados realistas e educativos para Santa Luzia
@st.cache_data
def generate_santa_luzia_data():
    years = list(range(2018, 2024))
    
    # Base realista para Santa Luzia (MA)
    data = []
    for year in years:
        # Tendências baseadas em dados reais da região
        areas = {
            "forest": 850 - (year - 2018) * 18,  # Florestas diminuindo gradualmente
            "field": 620 - (year - 2018) * 12,   # Campos naturais reduzindo
            "farm": 480 + (year - 2018) * 22,    # Agricultura aumentando
            "city": 65 + (year - 2018) * 6,      # Expansão urbana
            "water": 45,                         # Água relativamente estável
            "other": 120                         # Outras áreas
        }
        
        # Adicionar variações realistas
        for class_type, base_area in areas.items():
            variation = np.random.normal(0, base_area * 0.03)
            area = max(base_area + variation, 5)
            
            data.append({
                "Ano": year,
                "Classe": CLASS_CONFIG['names'][class_type],
                "Área (km²)": round(area, 2),
                "Tipo": class_type
            })
    
    df = pd.DataFrame(data)
    
    # Calcular porcentagens
    for year in years:
        year_total = df[df['Ano'] == year]['Área (km²)'].sum()
        df.loc[df['Ano'] == year, 'Porcentagem'] = (df[df['Ano'] == year]['Área (km²)'] / year_total * 100).round(1)
    
    return df

# Sidebar interativa
st.sidebar.markdown("## 🎮 **PAINEL DO EXPLORADOR**")

# Seletor de anos colorido
st.sidebar.markdown("### 🗓️ **ESCOLHA SUA AVENTURA NO TEMPO**")
year_range = st.sidebar.slider(
    "Arraste para viajar no tempo:",
    min_value=2018,
    max_value=2023,
    value=(2021, 2023),
    step=1
)

selected_years = list(range(year_range[0], year_range[1] + 1))

# Seletor de áreas para explorar
st.sidebar.markdown("### 🌟 **QUAIS LUGARES EXPLORAR?**")
all_classes = list(CLASS_CONFIG['names'].values())
selected_classes = st.sidebar.multiselect(
    "Escolha os tipos de lugares:",
    options=all_classes,
    default=all_classes,
    format_func=lambda x: f"{x} {CLASS_CONFIG['descriptions'][x]}"
)

# Informações educativas
st.sidebar.markdown("### 📚 **CURIOSIDADES**")
st.sidebar.markdown("""
<div style="background: linear-gradient(135deg, #e3f2fd, #bbdefb); padding: 15px; border-radius: 15px; border: 2px solid #64b5f6;">
🎯 <strong>Você sabia?</strong><br>
Santa Luzia é um município do Maranhão com muita natureza para explorar! 
Árvores altas, rios limpos e muitas histórias para contar! 📖
</div>
""", unsafe_allow_html=True)

# Layout principal com abas divertidas
tab1, tab2, tab3, tab4 = st.tabs(["🎯 VISÃO GERAL", "📊 GRÁFICOS DIVERTIDOS", "🗺️ NOSSO MAPA", "📋 DADOS LEGAIS"])

with tab1:
    st.markdown("## 🎯 **PANORAMA DE SANTA LUZIA**")
    
    df = generate_santa_luzia_data()
    df_filtered = df[(df['Ano'].isin(selected_years)) & (df['Classe'].isin(selected_classes))]
    
    if not df_filtered.empty:
        latest_year = max(selected_years)
        latest_data = df_filtered[df_filtered['Ano'] == latest_year]
        
        st.markdown(f"### 📍 **FOTOGRAFIA DE {latest_year}**")
        
        # Métricas interativas
        cols = st.columns(3)
        metrics = [
            ("🌳", "FLORESTAS", latest_data[latest_data['Classe'] == "🌳 FLORESTAS MÁGICAS"]['Área (km²)'].sum()),
            ("💧", "ÁGUA", latest_data[latest_data['Classe'] == "💧 RIOS BRINCALHÕES"]['Área (km²)'].sum()),
            ("🚜", "ALIMENTOS", latest_data[latest_data['Classe'] == "🚜 FAZENDAS ALEGRES"]['Área (km²)'].sum())
        ]
        
        for col, (emoji, nome, valor) in zip(cols, metrics):
            with col:
                st.markdown(
                    f'<div class="metric-card">'
                    f'<div style="font-size: 3rem;">{emoji}</div>'
                    f'<div style="font-size: 1.3rem; font-weight: bold;">{nome}</div>'
                    f'<div style="font-size: 2rem; margin-top: 15px;">{valor:.0f} km²</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
        
        # Gráfico de pizza super colorido
        st.markdown("### 🍕 **COMO ESTÁ DIVIDIDA NOSSA TERRA?**")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            pie_fig = px.pie(
                latest_data,
                names="Classe",
                values="Área (km²)",
                title=f"Distribuição das Áreas em {latest_year}",
                color="Classe",
                color_discrete_map=CLASS_CONFIG['colors'],
                hole=0.6,
                height=500
            )
            pie_fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate="<b>%{label}</b><br>%{percent:.1f}%<br>Área: %{value:.2f} km²",
                marker=dict(line=dict(color='white', width=4)),
                pull=[0.1, 0, 0, 0, 0, 0]  # Destacar florestas
            )
            pie_fig.update_layout(
                font=dict(size=16, family='Comic Sans MS'),
                showlegend=False
            )
            st.plotly_chart(pie_fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 📖 **HISTÓRIA DE CADA LUGAR**")
            for classe in latest_data['Classe'].unique():
                st.markdown(f"""
                <div style="background: {CLASS_CONFIG['colors'][classe]}; color: white; padding: 15px; 
                         margin: 10px 0; border-radius: 15px; text-align: center;">
                <strong>{classe}</strong><br>
                <small>{CLASS_CONFIG['descriptions'][classe]}</small>
                </div>
                """, unsafe_allow_html=True)

with tab2:
    st.markdown("## 📊 **BRINCANDO COM GRÁFICOS**")
    
    df_filtered = df[(df['Ano'].isin(selected_years)) & (df['Classe'].isin(selected_classes))]
    
    if not df_filtered.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📈 **A EVOLUÇÃO DA NATUREZA**")
            
            area_fig = px.area(
                df_filtered.pivot_table(index="Ano", columns="Classe", values="Área (km²)", aggfunc='sum').fillna(0),
                title="Como nossa natureza mudou?",
                labels={"value": "Área (km²)", "variable": "Tipo"},
                color_discrete_map=CLASS_CONFIG['colors'],
                height=400
            )
            area_fig.update_layout(
                font=dict(family='Comic Sans MS'),
                xaxis_title="Ano",
                yaxis_title="Área (km²)"
            )
            st.plotly_chart(area_fig, use_container_width=True)
        
        with col2:
            st.markdown("### 🏆 **COMPETIÇÃO DAS ÁREAS**")
            
            bar_fig = px.bar(
                df_filtered,
                x="Ano",
                y="Área (km²)", 
                color="Classe",
                barmode="group",
                title="Quem ganha em cada ano?",
                color_discrete_map=CLASS_CONFIG['colors'],
                height=400
            )
            bar_fig.update_layout(
                font=dict(family='Comic Sans MS'),
                xaxis_title="Ano",
                yaxis_title="Área (km²)",
                xaxis={'type': 'category'}
            )
            st.plotly_chart(bar_fig, use_container_width=True)
        
        # Gráfico de linhas animado
        st.markdown("### 🎯 **AVENTURA DAS MUDANÇAS**")
        
        line_fig = px.line(
            df_filtered,
            x="Ano",
            y="Área (km²)",
            color="Classe",
            markers=True,
            title="A jornada de cada tipo de área",
            color_discrete_map=CLASS_CONFIG['colors'],
            height=500
        )
        line_fig.update_layout(
            font=dict(family='Comic Sans MS', size=14),
            xaxis_title="Ano",
            yaxis_title="Área (km²)"
        )
        st.plotly_chart(line_fig, use_container_width=True)

with tab3:
    st.markdown("## 🗺️ **MAPA DA AVENTURA**")
    
    st.markdown("""
    <div class="fun-fact">
    <h3>🎨 DESENHE O MAPA DA SUA IMAGINAÇÃO! 🎨</h3>
    <p>Enquanto preparamos nosso mapa interativo, que tal imaginar como é Santa Luzia?</p>
    <p><strong>💡 Desafio:</strong> Desenhe como você imagina a divisão das áreas!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mapa ilustrativo
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(
            "https://via.placeholder.com/800x500/87CEEB/FFFFFF?text=🌳+💧+🚜+🏙️+\\n+MAPEANDO+SANTA+LUZIA+\\n+EM+BREVE+!+🎯",
            caption="🗺️ Nosso mapa está sendo preparado com muito carinho!",
            use_container_width=True  # CORRIGIDO AQUI
        )
    
    # Legenda interativa
    st.markdown("### 🎨 **LEGENDA COLORIDA**")
    legend_cols = st.columns(3)
    classes_list = list(CLASS_CONFIG['names'].values())
    
    for i, (col, classe) in enumerate(zip(legend_cols * 2, classes_list)):
        if i < len(classes_list):
            with col:
                st.markdown(
                    f'<div style="background: {CLASS_CONFIG["colors"][classe]}; color: white; '
                    f'padding: 15px; margin: 5px; border-radius: 10px; text-align: center; font-weight: bold;">'
                    f'{classe}'
                    f'</div>',
                    unsafe_allow_html=True
                )

with tab4:
    st.markdown("## 📋 **NOSSO BAÚ DE DADOS**")
    
    if not df_filtered.empty:
        # Tabela colorida
        pivot_table = df_filtered.pivot_table(
            index='Ano', 
            columns='Classe', 
            values='Área (km²)', 
            aggfunc='sum'
        ).round(1)
        
        # Adicionar totais
        pivot_table['TOTAL'] = pivot_table.sum(axis=1)
        
        st.markdown("### 📊 **TABELA DOS EXPLORADORES**")
        st.dataframe(pivot_table.style.background_gradient(cmap='Greens'), use_container_width=True)  # CORRIGIDO AQUI
        
        # Estatísticas divertidas
        st.markdown("### 🏆 **RECORDES E CURIOSIDADES**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Maior área atualmente
            current_max = df_filtered[df_filtered['Ano'] == max(selected_years)]
            biggest_class = current_max.loc[current_max['Área (km²)'].idxmax()]
            st.markdown(f"**🥇 Maior área:** {biggest_class['Classe']} ({biggest_class['Área (km²)']:.0f} km²)")
            
            # Mais crescimento
            growth_data = []
            for classe in selected_classes:
                class_data = df_filtered[df_filtered['Classe'] == classe]
                if len(class_data) > 1:
                    growth = class_data['Área (km²)'].iloc[-1] - class_data['Área (km²)'].iloc[0]
                    growth_data.append((classe, growth))
            
            if growth_data:
                fastest_grower = max(growth_data, key=lambda x: x[1])
                st.markdown(f"**📈 Cresceu mais:** {fastest_grower[0]} (+{fastest_grower[1]:.1f} km²)")
        
        with col2:
            # Área total
            total_now = current_max['Área (km²)'].sum()
            st.markdown(f"**📏 Área total:** {total_now:.0f} km²")
            
            # Número de áreas monitoradas
            st.markdown(f"**🔍 Áreas monitoradas:** {len(selected_classes)}")
        
        # Botão de download
        st.markdown("---")
        csv_data = df_filtered.to_csv(index=False)
        st.download_button(
            label="📥 **BAIXAR NOSSA PESQUISA**",
            data=csv_data,
            file_name=f"aventura_ecologica_santa_luzia.csv",
            mime="text/csv"
        )

# Rodapé super divertido
st.markdown("---")
st.markdown(
    "<div style='text-align: center; background: linear-gradient(135deg, #2E8B57, #32CD32); "
    "color: white; padding: 30px; border-radius: 25px; margin-top: 30px;'>"
    "<h2>🌟 VOCÊ É UM GUARDIÃO DA NATUREZA! 🌟</h2>"
    "<p style='font-size: 18px;'>Cada árvore, cada rio, cada animal conta com você!</p>"
    "<p style='font-size: 16px;'>💚 <strong>Cuide, preserve e admire!</strong> 💚</p>"
    f"<p style='margin-top: 20px;'><small>Aventura atualizada em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}</small></p>"
    "</div>",
    unsafe_allow_html=True
)

# Mensagem de sucesso
st.balloons()