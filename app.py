from PIL import Image

def limpiar_transparencia_dtf(input_path, output_path, umbral=128):
    # Abrimos la imagen original
    img = Image.open(input_path).convert("RGBA")
    datos = img.getdata()

    nueva_data = []
    for item in datos:
        # item[3] es el canal Alfa (0 a 255)
        if item[3] < umbral:
            # Si es más transparente que el umbral, lo hacemos invisible
            nueva_data.append((0, 0, 0, 0))
        else:
            # Si supera el umbral, lo hacemos 100% opaco
            nueva_data.append((item[0], item[1], item[2], 255))

    img.putdata(nueva_data)
    img.save(output_path, "PNG")

# Ejemplo: Cualquier píxel con más de 50% de opacidad se vuelve sólido
limpiar_transparencia_dtf("imagen_ia.png", "resultado_dtf.png", umbral=128)
