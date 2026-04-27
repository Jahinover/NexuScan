import pytesseract
from PIL import Image, ImageOps, ImageEnhance
import io
import fitz
import re
import streamlit as st

# Configuración de Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extraer_codigo_de_pagina(page, numero_pagina):
    try:
        # 1. Renderizado a resolución media para no perder velocidad
        # Matrix 2.5 es suficiente para detectar un "032" claro
        pix = page.get_pixmap(matrix=fitz.Matrix(2.5, 2.5)) 
        img_original = Image.open(io.BytesIO(pix.tobytes()))

        # 2. PROCESO DE LECTURA EN DOS ÁNGULOS (0° y 180°)
        for angulo in [0, 180]:
            img_actual = img_original if angulo == 0 else img_original.rotate(angulo)
            
            # Pre-procesamiento rápido para resaltar números
            img_gris = ImageOps.grayscale(img_actual)
            img_final = ImageEnhance.Contrast(img_gris).enhance(2.0)
            
            # Leemos la página completa buscando bloques de texto
            # PSM 3 es el mejor para encontrar texto esparcido
            texto = pytesseract.image_to_string(img_final, config='--psm 3')
            
            # 3. FILTRO ESPECÍFICO PARA TU CÓDIGO (Empieza por 032)
            # Buscamos la secuencia que empiece por 032 seguido de 5 a 7 dígitos
            patron_032 = re.search(r"032\d{5,7}", texto)
            
            if patron_032:
                codigo_encontrado = patron_032.group(0)
                
                # --- TU REGLA: Omitir el cero inicial ---
                # Esto convierte "032..." en "32..."
                return codigo_encontrado[1:]

        # 4. DIAGNÓSTICO EN CASO DE FALLO
        with st.expander(f"⚠️ No se detectó '032' en Hoja {numero_pagina}"):
            st.image(img_original, caption="Vista de la hoja analizada", use_container_width=True)
            st.write("Texto detectado (primeras líneas):", texto[:200])
            
        return "No detectado"
            
    except Exception as e:
        return f"Error: {str(e)}"