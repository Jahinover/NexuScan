import streamlit as st
import fitz
import streamlit.components.v1 as components
from logic.ocr_engine import extraer_codigo_de_pagina
from logic.url_generator import generar_enlaces_movimiento
from logic.pdf_tools import generar_zip_pedidos

# 1. CONFIGURACIÓN DE PÁGINA Y NOMBRE (Recomendación: NexuScan)
st.set_page_config(page_title="NexuScan | PDF Automator", page_icon="📄", layout="wide")

# 2. ESTILO GRÁFICO PERSONALIZADO
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stAlert { border-radius: 10px; }
    .stButton>button { 
        width: 100%; border-radius: 8px; height: 3.5em; 
        background-color: #2e7d32; color: white; font-weight: bold;
        border: none; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #1b5e20; border: none; }
    .card {
        padding: 20px; border-radius: 10px; background-color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# TÍTULO E INSTRUCCIONES
st.title("📄 NexuScan")
st.caption("Extractor automático de códigos, generador de URLs y segmentador de PDFs")
st.markdown("---")

# 3. INTERFAZ DE CARGA
col_main = st.columns([1, 1, 1])[1] # Centramos el cargador

with col_main:
    st.subheader("📁 Subir Documento")
    uploaded_file = st.file_uploader("Arrastra aquí el PDF escaneado", type="pdf", label_visibility="collapsed")

if uploaded_file:
    # --- PROCESAMIENTO AUTOMÁTICO ---
    if 'lista_codigos' not in st.session_state:
        with st.status("🚀 Procesando documento... Por favor espera", expanded=True) as status:
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            total_paginas = len(doc)
            temp_list = []
            
            progreso = st.progress(0)
            # Estrategia: Solo páginas pares (1, 3, 5...)
            for i in range(1, total_paginas, 2):
                page = doc.load_page(i)
                datos_ocr = extraer_codigo_de_pagina(page, i + 1)
                
                temp_list.append({
                    "Página": i + 1, 
                    "Código": datos_ocr['codigo'],
                })
                progreso.progress((i + 1) / total_paginas)
            
            st.session_state.lista_codigos = temp_list
            status.update(label="✅ Escaneo completo", state="complete", expanded=False)

    # --- DISEÑO DE RESULTADOS EN DOS COLUMNAS ---
    st.markdown("---")
    col_izq, col_der = st.columns([1, 1], gap="large")

    with col_izq:
        st.subheader("🔍 Verificación de Códigos")
        st.info("Si el OCR falló en algún código, corrígelo aquí directamente.")
        
        # Lista editable (Sustituye a la antigua tabla de confirmación)
        for idx, item in enumerate(st.session_state.lista_codigos):
            c1, c2 = st.columns([1, 3])
            c1.markdown(f"**H-{item['Página']}**")
            nuevo_val = c2.text_input(
                f"ID_{idx}", 
                value=item['Código'], 
                key=f"input_{idx}",
                label_visibility="collapsed"
            )
            st.session_state.lista_codigos[idx]['Código'] = nuevo_val

    with col_der:
        st.subheader("⚡ Acciones Rápidas")
        
        # BLOQUE DE URLS
        with st.container():
            st.markdown("**🔗 Gestión de Enlaces**")
            mis_urls = generar_enlaces_movimiento(st.session_state.lista_codigos)
            
            # Botón de apertura múltiple con estilo
            if st.button(f"🚀 Abrir {len(mis_urls)} movimientos en pestañas"):
                js_code = f"""
                    <script>
                    const urls = {mis_urls};
                    urls.forEach(url => {{ window.open(url, '_blank'); }});
                    </script>
                """
                components.html(js_code, height=0)
            
            with st.expander("Ver lista de URLs generadas"):
                st.text_area("URLs", value="\n".join(mis_urls), height=150, label_visibility="collapsed")

        st.markdown("<br>", unsafe_allow_html=True)

        # BLOQUE DE DESCARGA
        with st.container():
            st.markdown("**📦 Exportación de Archivos**")
            # Generamos el ZIP automáticamente para que esté listo para el botón
            uploaded_file.seek(0)
            archivo_zip = generar_zip_pedidos(uploaded_file, st.session_state.lista_codigos)
            
            if archivo_zip:
                st.download_button(
                    label="⬇️ DESCARGAR ZIP PROCESADO",
                    data=archivo_zip,
                    file_name=f"NexuScan_{uploaded_file.name.split('.')[0]}.zip",
                    mime="application/zip",
                    use_container_width=True
                )
else:
    st.info("👋 Bienvenida/o. Por favor, sube un archivo PDF para comenzar el proceso automático.")
        