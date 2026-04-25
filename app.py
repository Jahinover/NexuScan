import streamlit as st
import fitz
from logic.ocr_engine import extraer_codigo_de_pagina
import streamlit.components.v1 as components # Necesario para el botón de apertura múltiple
from logic.url_generator import generar_enlaces_movimiento

# Configuración de página
st.set_page_config(page_title="Extractor Flexible", layout="wide")
st.title("Fase 1: Subida y Validación de Códigos")

uploaded_file = st.file_uploader("Sube tu PDF escaneado", type="pdf")

if uploaded_file:
    # Abrimos el documento
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    total_paginas = len(doc)
    
    # Inicializamos el estado si no existe
    if 'lista_codigos' not in st.session_state:
        st.session_state.lista_codigos = []

    if st.button("🔍 Iniciar Lectura de OCR"):
        progreso = st.progress(0)
        temp_list = []
        
        # --- NUEVO: Variable para rastrear el último código detectado ---
        ultimo_codigo_guardado = None
        
        for i in range(total_paginas):
            page = doc.load_page(i)
            
            # Llamamos a la lógica del OCR que ya configuramos con Regex
            codigo_actual = extraer_codigo_de_pagina(page)
            
            # --- NUEVO: Lógica para evitar duplicados consecutivos ---
            # Solo guardamos si el código es nuevo o si es diferente al anterior
            if codigo_actual != ultimo_codigo_guardado:
                temp_list.append({
                    "Página": i + 1, 
                    "Código": codigo_actual
                })
                # Actualizamos cuál fue el último código que decidimos guardar
                ultimo_codigo_guardado = codigo_actual
            
            # Actualizar barra de progreso
            progreso.progress((i + 1) / total_paginas)
            
        st.session_state.lista_codigos = temp_list
        st.success(f"Lectura finalizada. Se detectaron {len(temp_list)} códigos únicos.")

    # --- TABLA DE VALIDACIÓN EDITABLE ---
    if st.session_state.lista_codigos:
        st.subheader("Verifica y corrige los códigos únicos")
        st.info("Si una secuencia de hojas tenía el mismo código, aquí verás solo una entrada.")
        
        # Mostramos los códigos únicos para que los confirmes
        for idx, item in enumerate(st.session_state.lista_codigos):
            col1, col2 = st.columns([1, 4])
            col1.write(f"Desde Hoja {item['Página']}")
            
            # Creamos el campo de texto para que puedas editar si el OCR falló
            nuevo_val = col2.text_input(
                f"Código único {idx+1}", 
                value=item['Código'], 
                key=f"input_{idx}"
            )
            # Guardamos cualquier corrección manual que hagas
            st.session_state.lista_codigos[idx]['Código'] = nuevo_val

        if st.button("Confirmar Códigos y Continuar"):
            st.session_state.confirmado = True
            st.success("✅ Códigos confirmados.")
from logic.url_generator import generar_enlaces_movimiento # Importa la nueva lógica

# ... (debajo de donde tienes el botón de Confirmar Códigos) ...

if 'confirmado' in st.session_state and st.session_state.confirmado:
    st.divider()
    st.subheader("🔗 Enlaces de Acceso Rápido")
    
    # 1. Generamos las URLs
    mis_urls = generar_enlaces_movimiento(st.session_state.lista_codigos)
    todas_las_urls_texto = "\n".join(mis_urls)
    
    # 2. Mostramos solo el cuadro de texto (segunda forma)
    st.write("Copia los enlaces generados:")
    st.text_area("Lista de URLs", value=todas_las_urls_texto, height=150)

    # 3. Botón para abrir todas las pestañas
    if st.button(f"🚀 Abrir los {len(mis_urls)} movimientos en pestañas nuevas"):
        # Creamos un script de JS que recorre la lista y abre cada una
        js_code = f"""
            <script>
            const urls = {mis_urls};
            urls.forEach(url => {{
                window.open(url, '_blank');
            }});
            </script>
        """
        # Ejecutamos el componente
        components.html(js_code, height=0)
        