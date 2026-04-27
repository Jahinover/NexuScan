import io        # <--- ESTA ES LA QUE FALTA Y CAUSA EL ERROR
import zipfile
import fitz

def generar_zip_pedidos(pdf_file, datos_procesados):
    zip_buffer = io.BytesIO()
    # Importante: resetear puntero del PDF original
    pdf_file.seek(0)
    pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    
    # Creamos el ZIP una sola vez
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for i in range(len(pdf_document)):
            idx_dato = i // 2
            
            # Buscamos la info en la lista que viene de app.py
            if idx_dato < len(datos_procesados):
                info = datos_procesados[idx_dato]
                # USAR LAS LLAVES EXACTAS: 'Código' y 'Placa'
                codigo = info.get('Código', 'DESCONOCIDO')
                placa = info.get('Placa', 'SIN_PLACA')
            else:
                codigo, placa = "SOBRANTE", "SIN_PLACA"

            tipo = "MANIFIESTO" if i % 2 == 0 else "REMESA"
            orden = str(i + 1).zfill(3)
            nombre_pdf = f"{orden}_{tipo}_{codigo}.pdf"
            
            # Extraer página
            doc_individual = fitz.open()
            doc_individual.insert_pdf(pdf_document, from_page=i, to_page=i)
            
            # Guardar página en el ZIP
            buf_pag = io.BytesIO()
            doc_individual.save(buf_pag)
            zip_file.writestr(nombre_pdf, buf_pag.getvalue())
            doc_individual.close()

    pdf_document.close()
    zip_buffer.seek(0)
    return zip_buffer