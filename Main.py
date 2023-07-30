import tkinter as tk
from tkinter import filedialog

def open_folder():
    global selected_folder
    folder_path = filedialog.askdirectory()
    if folder_path:
        selected_folder = folder_path
        print("Cartella selezionata:", selected_folder)
        root.destroy()  # Chiudi la finestra di dialogo

# Creazione dell'interfaccia utente
root = tk.Tk()
root.title("Seleziona una cartella")

selected_folder = None  # Variabile per memorizzare il percorso della cartella selezionata

# Creazione di un pulsante per aprire il dialogo di selezione della cartella
open_button = tk.Button(root, text="Apri cartella", command=open_folder)
open_button.pack(pady=20)

# Avvio dell'interfaccia utente
root.mainloop()

# Dopo la chiusura della finestra, puoi utilizzare la variabile "selected_folder"
if selected_folder:
    print("Percorso della cartella selezionata:", selected_folder)
    # Puoi aggiungere ulteriori azioni da eseguire con il percorso della cartella selezionata qui.
