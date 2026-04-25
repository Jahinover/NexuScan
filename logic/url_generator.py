def generar_enlaces_movimiento(lista_codigos):
    """
    Toma la lista de códigos únicos y los inserta en la URL base.
    """
    url_base = "https://ltsa.systram.com.co/formularios/Movimiento.aspx?page=1&busq=2|{}|0|0"
    enlaces = []
    
    for item in lista_codigos:
        codigo = item['Código']
        # Usamos .format() o f-strings para meter el código en los corchetes {}
        enlace_completo = url_base.format(codigo)
        enlaces.append(enlace_completo)
        
    return enlaces