import os
import json
import webbrowser
import pytesseract
from pdf2image import convert_from_path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import shutil


# Specifica il percorso di Tesseract
pytesseract.pytesseract.tesseract_cmd = r"O:\TESSERACT\tesseract.exe"

class OCRToolSettings:
    def __init__(self, input_folder=None, output_folder=None):
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.settings_file = 'settings.json'
        self.load_settings()

    def load_settings(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
                self.input_folder = settings.get('input_folder', self.input_folder)
                self.output_folder = settings.get('output_folder', self.output_folder)

    def save_settings(self):
        settings = {
            'input_folder': self.input_folder,
            'output_folder': self.output_folder
        }
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f)

class OCRTool:
    def __init__(self, root):
        self.root = root
        self.root.title('OCR Tool')
        self.root.geometry('500x600')

        # Inizializza le impostazioni
        self.settings = OCRToolSettings()

        # Configura lo stile moderno con bordi arrotondati
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", padding=6, relief="flat", borderwidth=0)
        
        # Layout principale
        self.create_main_view()

    def create_main_view(self):
        """Crea la vista principale."""
        for widget in self.root.winfo_children():
            widget.destroy()  # Rimuovi tutti i widget esistenti

        # Header con logo e titolo
        header_frame = ttk.Frame(self.root)
        header_frame.pack(pady=10)

        logo_path = r"O:\GIOVANNI PIO\logo.png"
        try:
            logo = Image.open(logo_path)
            logo.thumbnail((100, 100), Image.Resampling.LANCZOS)  # Mantieni proporzioni senza stirare
            logo_tk = ImageTk.PhotoImage(logo)
            logo_label = ttk.Label(header_frame, image=logo_tk, cursor="hand2")
            logo_label.image = logo_tk  # Mantieni riferimento all'immagine
            logo_label.pack()
            logo_label.bind("<Button-1>", lambda e: webbrowser.open("https://truccoloangelo.com"))
        except FileNotFoundError:
            ttk.Label(header_frame, text="Logo non trovato", foreground="red").pack()

        ttk.Label(header_frame, text='OCR Tool - Modern Edition', font=('Arial', 16)).pack(pady=5)

        # Selezione documento
        ttk.Label(self.root, text='Seleziona il tipo di documento:', font=('Arial', 12)).pack(pady=10)
        
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text='RENTRI NOSTRI', command=lambda: self.start_ocr('RENTRI NOSTRI'), width=20).pack(pady=5)
        ttk.Button(button_frame, text='RENTRI PORTALE', command=lambda: self.start_ocr('RENTRI PORTALE'), width=20).pack(pady=5)

        # Pulsanti aggiuntivi (Impostazioni e Guida)
        action_frame = ttk.Frame(self.root)
        action_frame.pack(pady=20)

        ttk.Button(action_frame, text='Impostazioni', command=self.show_settings_view).pack(side=tk.LEFT, padx=10)
        ttk.Button(action_frame, text='Guida', command=self.show_guide).pack(side=tk.LEFT, padx=10)

        # Icona info in basso a destra
        info_icon = ttk.Label(self.root, text="ℹ️", font=("Arial", 16), cursor="hand2")
        info_icon.pack(side=tk.BOTTOM, pady=10)
        info_icon.bind("<Button-1>", lambda e: webbrowser.open("https://www.linkedin.com/in/giovanni-pio-familiari/"))

    def show_settings_view(self):
        """Mostra la vista delle impostazioni."""
        for widget in self.root.winfo_children():
            widget.destroy()  # Rimuovi tutti i widget esistenti

        ttk.Label(self.root, text="Impostazioni", font=("Arial", 16)).pack(pady=10)

        input_button = ttk.Button(self.root, text="Seleziona Input", command=self.set_input_folder)
        input_button.pack(pady=5)

        output_button = ttk.Button(self.root, text="Seleziona Output", command=self.set_output_folder)
        output_button.pack(pady=5)

        # Mostra il percorso della cartella di input selezionata (se presente)
        if self.settings.input_folder:
            input_label = ttk.Label(
                self.root,
                text=f"Input: {self.settings.input_folder}",
                font=("Arial", 10),
                wraplength=400,
                foreground="blue"
            )
            input_label.pack(pady=5)

        # Mostra il percorso della cartella di output selezionata (se presente)
        if self.settings.output_folder:
            output_label = ttk.Label(
                self.root,
                text=f"Output: {self.settings.output_folder}",
                font=("Arial", 10),
                wraplength=400,
                foreground="green"
            )
            output_label.pack(pady=5)

        # Pulsante per tornare indietro alla schermata principale
        back_button = ttk.Button(self.root, text="Torna Indietro", command=self.create_main_view)
        back_button.pack(pady=20)

    def set_input_folder(self):
        """Seleziona la cartella di input e aggiorna la vista."""
        input_dir = filedialog.askdirectory(title="Seleziona la cartella di input")
        if input_dir:
            self.settings.input_folder = input_dir
            self.show_settings_view()  # Aggiorna la vista per mostrare il percorso selezionato

    def set_output_folder(self):
        """Seleziona la cartella di output e aggiorna la vista."""
        output_dir = filedialog.askdirectory(title="Seleziona la cartella di output")
        if output_dir:
            self.settings.output_folder = output_dir
            self.show_settings_view()  # Aggiorna la vista per mostrare il percorso selezionato

    def show_guide(self):
        """Mostra una finestra con la guida."""
        guide_text = (
            "Benvenuto nella guida dell'OCR Tool!\n\n"
            "1. **Seleziona Input**: Premi 'Seleziona Input' nelle impostazioni per scegliere "
            "la cartella contenente i file PDF da elaborare.\n\n"
            "2. **Seleziona Output**: Premi 'Seleziona Output' per scegliere dove salvare i file elaborati.\n\n"
            "3. **Funzionamento**: Il programma legge un quadrato in alto a destra del documento "
            "per estrarre informazioni utili.\n\n"
            "4. **Easter Egg**: Clicca sul logo per visitare il sito ufficiale.\n\n"
            "5. **Crediti**: Clicca sull'icona ℹ️ in basso per vedere chi ha creato questo programma."
        )

        # Finestra della guida
        guide_window = tk.Toplevel(self.root)
        guide_window.title("Guida")
        guide_window.geometry("400x400")
        guide_window.resizable(False, False)

        # Testo della guida
        guide_label = tk.Label(
            guide_window,
            text=guide_text,
            font=("Arial", 12),
            wraplength=380,
            justify="left",
            padx=10,
            pady=10,
        )
        guide_label.pack(fill="both", expand=True)

    def start_ocr(self, scan_type):
        """Avvia il processo OCR in base al tipo di documento selezionato."""
        bbox_map = {
            'RENTRI NOSTRI': (1259, 37, 1649, 122),
            'RENTRI PORTALE': (1197, 72, 1633, 205)
        }

        bbox = bbox_map.get(scan_type)
        
        input_folder = self.settings.input_folder or r"O:\GIOVANNI PIO\PDF_in_input"
        output_folder = self.settings.output_folder or os.path.expanduser(r"~/Desktop/Output")

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        try:
            ocr_pdf_to_pdf(input_folder, output_folder, bbox=bbox)
            messagebox.showinfo('Info', 'Processo OCR completato!')
            
            # Salva le impostazioni attuali dopo l'OCR
            self.settings.save_settings()
            
        except Exception as e:
            messagebox.showerror("Errore", f"Si è verificato un errore: {e}")

def ocr_pdf_to_pdf(input_folder, output_folder, bbox=None):
    poppler_path = r"O:\GIOVANNI PIO\poppler-24.08.0\Library\bin"
    for filename in os.listdir(input_folder):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(input_folder, filename)
            
            # Converti solo la prima pagina per l'OCR
            images = convert_from_path(pdf_path, first_page=1, last_page=1, poppler_path=poppler_path)

            if images:
                first_image = images[0]
                cropped_image = first_image.crop(bbox)
                
                text = pytesseract.image_to_string(cropped_image).strip()
                
                valid_filename = "".join(c for c in text if c.isalnum() or c in (' ', '_')).rstrip()
                
                # Copia il file originale invece di crearne uno nuovo
                output_filename = os.path.join(output_folder, f"{valid_filename}.pdf")
                shutil.copy2(pdf_path, output_filename)

if __name__ == '__main__':
    root = tk.Tk()
    app = OCRTool(root)
    root.mainloop()
