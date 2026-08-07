import argparse
from PIL import Image, ImageDraw
import numpy as np
import random

def generar_imagen(num_lineas, ancho, alto, color_principal, variacion_color):
    # Generar imagen de tamaño especificado
    img = Image.new('RGB', (ancho, alto), 'white')
    draw = ImageDraw.Draw(img)
    
    for i in range(num_lineas):
        # Generación de líneas principales aleatorias
        x1 = random.randint(0, ancho)
        y1 = random.randint(0, alto)
        x2 = random.randint(0, ancho)
        y2 = random.randint(0, alto)
        
        # Generación de color variado con respecto a color principal
        r, g, b = tuple(map(lambda c: int((1 + variacion_color) * c), color_principal))
        if r > 255: r = 255
        if g > 255: g = 255
        if b > 255: b = 255
        
        # Dibujar línea con el color generado
        draw.line((x1, y1, x2, y2), fill=(r, g, b))
    
    del draw  # Liberar memoria
    return img

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_lineas", type=int)
    parser.add_argument("--ancho", type=int)
    parser.add_argument("--alto", type=int)
    parser.add_argument("--color_principal", type=str)
    parser.add_argument("--variacion_color", type=float)
    
    args = parser.parse_args()
    
    # Convertir color principal a formato RGB
    r, g, b = tuple(map(lambda x: int(x, 16), args.color_principal[1:].split('')))
    
    img = generar_imagen(args.num_lineas, args.ancho, args.alto, (r, g, b), args.variacion_color)
    img.save("tren_{}_{}_{}.png".format(args.num_lineas, args.ancho, args.alto))
    
if __name__ == "__main__":
    main()
