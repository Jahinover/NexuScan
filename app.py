import streamlit as st
import fitz
from logic.ocr_engine import extraer_codigo_de_pagina # Importamos nuestra lógica modular

# Configuración de página
st.set_page_config(page_title="Extractor Flexible", layout="wide")
st.title("Fase 1: Subida y Validación de Códigos")

uploaded_file = st.file_uploader("Sube tu PDF escaneado", type="pdf")

if uploaded_file:
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    total_paginas = len(doc)
    
    if 'lista_codigos' not in st.session_state:
        st.session_state.lista_codigos = []

    if st.button("🔍 Iniciar Lectura de OCR"):
        progreso = st.progress(0)
        temp_list = []
        
        for i in range(total_paginas):
            page = doc.load_page(i)
            
            # Llamamos a la función que pusimos en logic/ocr_engine.py
            codigo = extraer_codigo_de_pagina(page)
            
            temp_list.append({"Página": i + 1, "Código": codigo})
            progreso.progress((i + 1) / total_paginas)
            
        st.session_state.lista_codigos = temp_list
        st.success("Lectura finalizada.")

    # --- TABLA DE VALIDACIÓN EDITABLE --- [cite: 143, 145]
    if st.session_state.lista_codigos:
        st.subheader("Verifica y corrige los códigos detectados")
        st.info("Puedes corregir los códigos directamente en la tabla si el OCR falló o la secuencia cambió.")
        
        for idx, item in enumerate(st.session_state.lista_codigos):
            col1, col2 = st.columns([1, 4])
            col1.write(f"Hoja {item['Página']}")
            nuevo_codigo = col2.text_input(f"Código detectado (H{item['Página']})", 
                                        value=item['Código'], 
                                        key=f"input_{idx}")
            st.session_state.lista_codigos[idx]['Código'] = nuevo_codigo

        if st.button("Confirmar Códigos y Continuar"):
            st.session_state.confirmado = True
            st.write("✅ Códigos guardados. Listos para separar archivos y generar URLs.")