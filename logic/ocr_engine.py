import pytesseract
from PIL import Image
import io
import fitz
import re

# Si estás en Windows, asegúrate de que esta ruta sea correcta:
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extraer_codigo_de_pagina(page):
    """
    Lee cada página, detecta su rotación, la endereza y extrae el código.
    """
    try:
        # 1. Convertir página a imagen (alta resolución)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) 
        img = Image.open(io.BytesIO(pix.tobytes()))
        
        # --- NUEVO: DETECCIÓN Y CORRECCIÓN DE ROTACIÓN (OSD) ---
        # Configuramos Tesseract para que solo detecte la orientación
        try:
            # osd contiene info como 'Orientation: 180', 'Rotate: 180'
            osd = pytesseract.image_to_osd(img)
            # Extraemos cuántos grados hay que rotar para enderezar
            angulo_rotacion = re.search('(?<=Rotate: )\d+', osd).group(0)
            
            # Si hay rotación, enderezamos la imagen
            if angulo_rotacion != "0":
                # Rotamos en sentido contrario a las agujas del reloj
                img = img.rotate(int(angulo_rotacion), expand=True)
        except Exception as e_osd:
            # Si falla la detección de orientación, seguimos con la imagen original
            # pero lo registramos internamente para saber qué pasó.
            # print(f"Aviso OSD: {str(e_osd)}")
            pass
        # ---------------------------------------------------------
        
        # 2. OCR - Leemos la imagen (ahora enderezada)
        texto_completo = pytesseract.image_to_string(img, config='--psm 6')
        
        # 3. Regex flexible (igual que antes)
        patron = r"Movimiento\s*Nro\s*:?\s*(\d+)"
        match = re.search(patron, texto_completo, re.IGNORECASE)
        
        if match:
            return match.group(1)
        else:
            return "No detectado"
            
    except Exception as e:
        return f"Error: {str(e)}"