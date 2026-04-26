import pytesseract
from PIL import Image, ImageOps, ImageEnhance
import io
import fitz
import re
import streamlit as st

# Configuración de la ruta de Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extraer_codigo_de_pagina(page, numero_pagina):
    """
    Función optimizada para leer remesas en páginas pares.
    Recibe la página y el número de página para el diagnóstico.
    """
    try:
        # 1. Renderizado a alta resolución (Matrix 3.5 para capturar fuentes pequeñas de remesas)
        pix = page.get_pixmap(matrix=fitz.Matrix(3.5, 3.5)) 
        img_original = Image.open(io.BytesIO(pix.tobytes()))
        
        # 2. Pre-procesamiento de imagen
        img_gris = ImageOps.grayscale(img_original)
        
        # Versión A: Blanco y negro puro (umbral)
        img_bn = img_gris.point(lambda x: 0 if x < 165 else 255, '1')
        
        # Versión B: Contraste optimizado
        enhancer = ImageEnhance.Contrast(img_gris)
        img_contraste = enhancer.enhance(2.0)

        # 3. Proceso de lectura
        # Para remesas, 0° y 180° cubren la gran mayoría de casos
        angulos = [0, 180] 
        versiones = [img_bn, img_contraste]
        
        for angulo in angulos:
            for version_img in versiones:
                # Rotar si es necesario
                img_actual = version_img if angulo == 0 else version_img.rotate(angulo, expand=True)

                # Usamos PSM 11: ideal para encontrar texto pequeño como "Movimiento Nro"
                # en documentos con muchas tablas y líneas.
                texto = pytesseract.image_to_string(img_actual, config='--psm 11')
                
                # Regex estricto para evitar capturar el Manifiesto Nro que está a la par
                # Captura el número inmediatamente después de la etiqueta de Movimiento
                patron = r"(?i)Movimiento\s*(?:Nro|Nr|No)?[:\.\s]*(\d{7,10})"
                match = re.search(patron, texto)
                
                if match:
                    return match.group(1)

        # 4. Si tras todos los intentos no detecta nada, muestra el diagnóstico
        with st.expander(f"⚠️ Diagnóstico Hoja {numero_pagina}"):
            st.warning("No se detectó el código en esta remesa.")
            st.image(img_contraste, caption="Imagen procesada analizada", use_container_width=True)
            
        return "No detectado"
            
    except Exception as e:
        return f"Error: {str(e)}"