import io
import zipfile  # Esto eliminará el resaltado amarillo
import fitz
import re
import streamlit as st

def generar_zip_pedidos(pdf_file, datos_procesados):
    """
    Genera un ZIP con las páginas separadas y renombradas.
    datos_procesados: Lista de dicts [{'codigo': '322...', 'placa': 'TTY959'}, ...]
    """
    zip_buffer = io.BytesIO()
    
    try:
        # Abrimos el PDF desde los bytes
        pdf_file.seek(0)
        pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
        
        # Creamos el archivo ZIP en memoria
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for i in range(len(pdf_document)):
                # Calculamos a qué par de documentos pertenece esta hoja
                # Hoja 1 y 2 -> indice 0; Hoja 3 y 4 -> indice 1
                idx_dato = i // 2
                
                # Obtenemos la info detectada en la remesa (página par)
                if idx_dato < len(datos_procesados):
                    info = datos_procesados[idx_dato]
                    codigo = info.get('Código', 'SIN_CODIGO')
                    placa = info.get('Placa', 'SIN_PLACA')
                else:
                    codigo, placa = "DESCONOCIDO", "SIN_PLACA"

                # Lógica de nombre: Hoja Impar = MANIFIESTO, Hoja Par = REMESA
                tipo = "MANIFIESTO" if i % 2 == 0 else "REMESA"
                
                # Formato final: TIPO_CODIGO_PLACA-ORDEN.pdf
                nombre_pdf = f"{tipo}_{codigo}_{placa}-{i+1}.pdf"
                
                # Extraemos la página actual a un nuevo documento PDF
                doc_individual = fitz.open()
                doc_individual.insert_pdf(pdf_document, from_page=i, to_page=i)
                
                # Guardamos la página en un buffer temporal para meterla al ZIP
                buf_individual = io.BytesIO()
                doc_individual.save(buf_individual)
                zip_file.writestr(nombre_pdf, buf_individual.getvalue())
                doc_individual.close()

        pdf_document.close()
        zip_buffer.seek(0)
        return zip_buffer
        
    except Exception as e:
        st.error(f"Error técnico al crear el ZIP: {e}")
        return None