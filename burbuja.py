import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import mysql.connector
from datetime import datetime

# ==== CONFIGURACIÓN BASE DE DATOS ====
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "1234"
DB_NAME = "habilidades_programacion"

# ==== FUNCIONES DE BASE DE DATOS ====
def conectar_bd():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

def crear_tabla_si_no_existe(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS listas_ordenadas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            lista_original TEXT,
            lista_ordenada TEXT,
            fecha DATETIME
        );
    """)
    conn.commit()

def insertar_lista(conn, original, ordenada):
    cursor = conn.cursor()
    sql = """
        INSERT INTO listas_ordenadas (lista_original, lista_ordenada, fecha)
        VALUES (%s, %s, %s)
    """
    datos = (str(original), str(ordenada), datetime.now())
    cursor.execute(sql, datos)
    conn.commit()

# ==== FUNCIONES DE LA APP ====
def ingresar_manual():
    global lista_original
    lista_original = []
    for i in range(20):
        while True:
            try:
                num = simpledialog.askinteger("Entrada manual", f"Ingrese el número {i+1}:")
                if num is not None:
                    lista_original.append(num)
                    break
                else:
                    return  # Cancelado
            except ValueError:
                messagebox.showerror("Error", "Entrada inválida. Debe ser un número entero.")
    mostrar_lista("Lista ingresada manualmente", lista_original)

def generar_aleatoria():
    global lista_original
    lista_original = [random.randint(1, 100) for _ in range(20)]
    mostrar_lista("Lista generada aleatoriamente", lista_original)

def mostrar_lista(titulo, lista):
    text_output.delete(1.0, tk.END)
    text_output.insert(tk.END, f"{titulo}:\n{lista}\n\n")

def ordenar_y_mostrar():
    if not lista_original:
        messagebox.showwarning("Advertencia", "Primero debes ingresar o generar una lista.")
        return

    lista = lista_original.copy()
    text_output.delete(1.0, tk.END)
    text_output.insert(tk.END, f"Lista original:\n{lista}\n\n")

    n = len(lista)
    paso = 1
    for i in range(n):
        for j in range(0, n - i - 1):
            if lista[j] > lista[j + 1]:
                lista[j], lista[j + 1] = lista[j + 1], lista[j]
            text_output.insert(tk.END, f"Paso {paso}: {lista}\n")
            paso += 1
        text_output.insert(tk.END, f"--- Fin de la iteración {i + 1} ---\n")

    text_output.insert(tk.END, "\nLISTA ORDENADA FINAL:\n")
    text_output.insert(tk.END, f"{lista}\n", "resaltado")

    try:
        conn = conectar_bd()
        crear_tabla_si_no_existe(conn)
        insertar_lista(conn, lista_original, lista)
        conn.close()
        messagebox.showinfo("Éxito", "La lista se guardó correctamente en la base de datos.")
    except Exception as e:
        messagebox.showerror("Error de base de datos", str(e))

def salir():
    if messagebox.askyesno("Salir", "¿Seguro que deseas salir?"):
        root.destroy()

def reiniciar():
    global lista_original
    lista_original = []
    text_output.delete(1.0, tk.END)

# ==== INTERFAZ GRÁFICA ====
root = tk.Tk()
root.title("Ordenamiento de Listas - Burbuja")
root.geometry("800x600")

lista_original = []

frame_botones = tk.Frame(root)
frame_botones.pack(pady=10)

btn_ingresar = tk.Button(frame_botones, text="Ingresar Números Manualmente", command=ingresar_manual, width=30)
btn_generar = tk.Button(frame_botones, text="Generar Números Aleatorios", command=generar_aleatoria, width=30)
btn_ordenar = tk.Button(frame_botones, text="Ordenar y Mostrar Pasos", command=ordenar_y_mostrar, width=30)
btn_reiniciar = tk.Button(frame_botones, text="Ingresar Otra Lista", command=reiniciar, width=30)
btn_salir = tk.Button(frame_botones, text="Salir", command=salir, width=30)

btn_ingresar.grid(row=0, column=0, padx=5, pady=5)
btn_generar.grid(row=0, column=1, padx=5, pady=5)
btn_ordenar.grid(row=1, column=0, padx=5, pady=5)
btn_reiniciar.grid(row=1, column=1, padx=5, pady=5)
btn_salir.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

text_output = tk.Text(root, height=25, wrap=tk.WORD)
text_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
text_output.tag_config("resaltado", foreground="blue", font=("Helvetica", 12, "bold"))

root.mainloop()
