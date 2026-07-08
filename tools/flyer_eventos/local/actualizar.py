import instaloader
import os
import glob
import shutil
import time
import subprocess
import sys

# --- RUTAS DE LA CARPETA BASE ---
# La carpeta base se obtiene de la variable de entorno RD_AUTOMATIZACION,
# con un fallback a la ruta predeterminada si no está definida.
CARPETA_BASE = os.environ.get("RD_AUTOMATIZACION", r"C:\rd\AUTOMATIZACION")

RUTA_DROPLET = os.path.join(CARPETA_BASE, "Droplet_Flyer.exe")
ARCHIVO_PSD = os.path.join(CARPETA_BASE, "historia.psd")
ARCHIVO_INPUT_IG = os.path.join(CARPETA_BASE, "input_ig.jpg")
ARCHIVO_FINAL_IMAGEN = os.path.join(CARPETA_BASE, "flyer_final.jpg") # Corregido: Droplet produce flyer_final.jpg
OUTPUT_RENDER_PATH = os.path.join(CARPETA_BASE, "render_output.png")
TEMPLATE_BLENDER = os.path.join(CARPETA_BASE, "RD.blend")
# ---------------------------

def automatizar_flyer():
    # Asegurarse de que el script se ejecute en la carpeta base
    os.chdir(CARPETA_BASE)
    
    # Limpiar cualquier carpeta temporal previa
    if os.path.exists("temp_flyer"):
        shutil.rmtree("temp_flyer", ignore_errors=True)

    print("=== AUTOMATIZADOR DE FLYERS ===")
    
    # Obtener URL de Instagram desde argumentos CLI o solicitar al usuario
    if len(sys.argv) > 1:
        url = sys.argv[1]
        print(f"URL de Instagram recibida desde CLI: {url}")
    else:
        url = input("Por favor, ingrese la URL de Instagram del post o reel:\n> ")
    
    # Extraer shortcode del URL
    try:
        if "/p/" in url:
            shortcode = url.split("/p/")[1].split("/")[0]
        elif "/reel/" in url:
            shortcode = url.split("/reel/")[1].split("/")[0]
        else:
            print("\nError: El enlace proporcionado no es válido. Debe contener '/p/' o '/reel/'.")
            return
    except Exception:
        print("\nOcurrió un error al procesar el enlace de Instagram.")
        return

    print("\nDescargando contenido multimedia desde Instagram...")
    L = instaloader.Instaloader(download_video_thumbnails=False, download_comments=False, save_metadata=False)
    
    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        L.download_post(post, target="temp_flyer")
    except Exception as e:
        print(f"\nError al descargar el contenido: {e}")
        return

    # Buscar la imagen JPG descargada
    archivos_jpg = glob.glob(os.path.join("temp_flyer", "*.jpg"))
    if not archivos_jpg:
        print("\nNo se encontró ninguna imagen JPG en el contenido descargado.")
        return
        
    imagen_descargada = os.path.abspath(archivos_jpg[0])

    print("Actualizando input_ig.jpg con la imagen descargada...")
    if os.path.exists(ARCHIVO_INPUT_IG):
        os.remove(ARCHIVO_INPUT_IG)
    shutil.copy(imagen_descargada, ARCHIVO_INPUT_IG)

    # Pausa breve para que el sistema de archivos registre el archivo nuevo
    print("Esperando brevemente a que el sistema procese el archivo...")
    time.sleep(2)

    print("\nLanzando Adobe Photoshop Droplet...")
    
    # Usar 'start' para ejecutar el Droplet de Photoshop
    comando_droplet = f'start "" "{RUTA_DROPLET}" "{ARCHIVO_PSD}"'
    os.system(comando_droplet)
    
    # Esperar activamente a que Photoshop genere el archivo flyer_final.jpg
    print(f"Esperando que el Droplet de Photoshop genere '{os.path.basename(ARCHIVO_FINAL_IMAGEN)}'...")
    droplet_start_time = time.time()
    max_wait_time = 300 # segundos
    poll_interval = 2 # segundos
    file_ready = False
    
    while time.time() - droplet_start_time < max_wait_time:
        if os.path.exists(ARCHIVO_FINAL_IMAGEN):
            file_mtime = os.path.getmtime(ARCHIVO_FINAL_IMAGEN)
            # Verificar si el archivo fue modificado después de lanzar el Droplet
            if file_mtime > droplet_start_time:
                print(f"Archivo '{os.path.basename(ARCHIVO_FINAL_IMAGEN)}' detectado y actualizado.")
                file_ready = True
                break
        time.sleep(poll_interval)
        print(f"[{int(time.time() - droplet_start_time)}/{max_wait_time}s] Esperando '{os.path.basename(ARCHIVO_FINAL_IMAGEN)}'...")

    if not file_ready:
        print(f"Error: El archivo '{os.path.basename(ARCHIVO_FINAL_IMAGEN)}' no se generó o actualizó en {max_wait_time} segundos.")
        shutil.rmtree("temp_flyer", ignore_errors=True)
        return

    print("\nIniciando proceso de renderizado en Blender...")
    try:
        subprocess.run(
            ['blender', '--background', '--python', 'blender_render.py', '--',
             ARCHIVO_FINAL_IMAGEN, OUTPUT_RENDER_PATH, TEMPLATE_BLENDER],
            check=True
        )
        print("Renderizado de Blender completado exitosamente.")
    except FileNotFoundError:
        print("Error: El ejecutable 'blender' no se encontró en el PATH del sistema. Asegúrese de que Blender esté instalado y su ruta esté configurada correctamente.")
    except subprocess.CalledProcessError as e:
        print(f"Error: Blender finalizó con un código de error {e.returncode}. Detalles: {e}")
    except Exception as e:
        print(f"Error inesperado al ejecutar Blender: {e}")
    
    print("\nProceso completado exitosamente.")
        
    shutil.rmtree("temp_flyer", ignore_errors=True)

if __name__ == "__main__":
    automatizar_flyer()
