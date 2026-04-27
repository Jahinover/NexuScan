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
        # 1. Renderizado
        pix = page.get_pixmap(matrix=fitz.Matrix(2.5, 2.5)) 
        img_original = Image.open(io.BytesIO(pix.tobytes()))

        # Inicializamos variables por defecto
        codigo = "No detectado"
        placa = "SIN_PLACA"

        # 2. PROCESO DE LECTURA (0° y 180°)
        for angulo in [0, 180]:
            img_actual = img_original if angulo == 0 else img_original.rotate(angulo)
            
            # Pre-procesamiento
            img_gris = ImageOps.grayscale(img_actual)
            img_final = ImageEnhance.Contrast(img_gris).enhance(2.0)
            
            # OCR
            texto = pytesseract.image_to_string(img_final, config='--psm 3')
            texto_limpio = texto.upper().replace(" ", "") # Limpiamos espacios para la placa
            # --- LÓGICA POR FILAS PARA LA PLACA ---
            lineas = texto.upper().splitlines()
            # 3. BUSCAR CÓDIGO (032...)
            if codigo == "No detectado":
                patron_032 = re.search(r"032\d{5,7}", texto)
                if patron_032:
                    # Quitamos el cero inicial como pediste
                    codigo = patron_032.group(0)[1:]

            # 4. BUSCAR PLACA (ABC123)
            # 1. Obtenemos los datos detallados (coordenadas)
            datos_ocr = pytesseract.image_to_data(img_final, output_type=pytesseract.Output.DICT)
            
        # 5. DIAGNÓSTICO (Solo si falló el código)
        if codigo == "No detectado":
            with st.expander(f"⚠️ Diagnóstico Hoja {numero_pagina}"):
                st.image(img_original, caption="Hoja analizada", use_container_width=True)
                st.write("Texto detectado:", texto[:200])
            
        # RETORNAMOS AMBOS DATOS
        return {"codigo": codigo}
            
    except Exception as e:
        return {"codigo": "ERROR"}
    