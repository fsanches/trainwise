import streamlit as st
import os
import requests

st.set_page_config(page_title="TrainWise | Strava Viewer", layout="wide")
st.title("🚴 TrainWise - Strava Activities Viewer")

# Verifica se o token já existe
token_exists = os.path.exists("tokens/strava_token.json")

if not token_exists:
    st.warning("Você ainda não está conectado à sua conta Strava.")
    st.markdown("[🔐 Conectar com Strava](http://localhost:8000/strava/login)")
    st.stop()

# Se token existe, tenta carregar dados
try:
    response = requests.get("http://localhost:8000/strava/sync")
    data = response.json()

    if isinstance(data, list):
        st.success(f"✅ {len(data)} atividades carregadas com sucesso!")
        st.dataframe(data)
    else:
        st.error("❌ Erro ao buscar atividades.")
        st.json(data)

except Exception as e:
    st.error("⚠️ Erro ao conectar à API. Certifique-se de que FastAPI está rodando.")
    st.exception(e)
