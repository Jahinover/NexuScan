import pytesseract
from PIL import Image
import io
import fitz
import re

# Si estás en Windows, asegúrate de que esta ruta sea correcta:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extraer_codigo_de_pagina(page):
    """
    Busca el patrón 'Movimiento Nro:XXXXX' y extrae solo los números.
    Funciona aunque el número de dígitos aumente en el futuro.
    """
    try:
        # 1. Mejoramos la resolución para que el OCR no confunda números (ej: 0 con 8)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) 
        img = Image.open(io.BytesIO(pix.tobytes()))
        
        # 2. OCR - Configuramos para buscar texto denso (--psm 6)
        texto_completo = pytesseract.image_to_string(img, config='--psm 6')
        
        # 3. Regex flexible: 
        # 'Movimiento' + espacio opcional + 'Nro' + ':' opcional + espacio opcional + (DÍGITOS)
        patron = r"Movimiento\s*Nro\s*:?\s*(\d+)"
        match = re.search(patron, texto_completo, re.IGNORECASE)
        
        if match:
            # Retorna solo el grupo de números capturado
            return match.group(1)
        else:
            return "No detectado"
            
    except Exception as e:
        return f"Error: {str(e)}"