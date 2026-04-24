import pytesseract
from PIL import Image
import io
import fitz  # PyMuPDF

def extraer_codigo_de_pagina(page):
    """
    Convierte una página de PDF en imagen y extrae el texto usando OCR.
    """
    # Aumentamos resolución para mejor lectura [cite: 135, 136]
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) 
    img = Image.open(io.BytesIO(pix.tobytes()))
    
    # Ejecutar OCR [cite: 117, 121]
    # Usamos psm 6 que es óptimo para bloques de texto uniformes
    texto = pytesseract.image_to_string(img, config='--psm 6').strip()
    
    # Retornamos la primera línea como el código
    return texto.split('\n')[0] if texto else ""