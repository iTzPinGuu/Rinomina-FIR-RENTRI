import os
import json
import shutil
import re
import threading
import pytesseract
import fitz  # PyMuPDF
from datetime import datetime
from pdf2image import convert_from_path
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import webbrowser

# Configurazioni globali
PATHS = {
    'tesseract': r"O:\TESSERACT\tesseract.exe",
    'poppler': r"O:\GIOVANNI PIO\poppler-24.08.0\Library\bin",
    'logo': r"O:\GIOVANNI PIO\logo.png"
}
pytesseract.pytesseract.tesseract_cmd = PATHS['tesseract']

class OCRToolSettings:
    """Gestisce il caricamento/salvataggio delle impostazioni"""
    def __init__(self, settings_file):
        self.settings_file = settings_file
        self.input_folder = None
        self.output_folder = None
        self.load_settings()

    def load_settings(self):
        """Carica le impostazioni da file"""
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
                self.input_folder = settings.get('input_folder')
                self.output_folder = settings.get('output_folder')

    def save_settings(self):
        """Salva le impostazioni su file"""
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
        self.root.geometry('500x500')
        
        self.fir_settings = OCRToolSettings('fir_settings.json')
        self.riscontri_settings = OCRToolSettings('riscontri_settings.json')
        self.processing = False
        
        self.setup_ui()

    def setup_ui(self):
        """Configura l'interfaccia grafica"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Header
        header_frame = ttk.Frame(self.root)
        header_frame.pack(pady=5)
        
        try:
            logo = Image.open(PATHS['logo'])
            logo.thumbnail((80, 80), Image.Resampling.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(logo)
            logo_label = ttk.Label(header_frame, image=self.logo_img, cursor="hand2")
            logo_label.pack()
            logo_label.bind("<Button-1>", lambda e: webbrowser.open("https://truccoloangelo.com"))
        except Exception as e:
            print(f"Errore caricamento logo: {str(e)}")

        # Pulsanti principali
        main_frame = ttk.Frame(self.root)
        main_frame.pack(pady=5)
        
        btn_config = [
            ('RENTRI COMBINATO', self.start_combined_process),
            ('RISCONTRI', self.start_riscontri_process)
        ]
        
        for text, cmd in btn_config:
            ttk.Button(main_frame, text=text, command=cmd).pack(pady=3, fill=tk.X)

        # Pulsanti impostazioni
        settings_frame = ttk.Frame(self.root)
        settings_frame.pack(pady=10)
        
        ttk.Button(settings_frame, text='Impostazioni FIR', 
                 command=lambda: self.show_settings('fir')).pack(side=tk.LEFT, padx=5)
        ttk.Button(settings_frame, text='Impostazioni Riscontri', 
                 command=lambda: self.show_settings('riscontri')).pack(side=tk.LEFT, padx=5)

        # Barra di avanzamento
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')

    def toggle_controls(self, state):
        """Abilita/disabilita i controlli"""
        for child in self.root.winfo_children():
            if isinstance(child, ttk.Button):
                child['state'] = state
        self.processing = (state == 'disabled')

    def start_combined_process(self):
        """Avvia elaborazione combinata RENTRI"""
        if not self.processing:
            self.toggle_controls('disabled')
            self.progress.pack(fill=tk.X, pady=5)
            self.progress.start()
            threading.Thread(target=self.process_combined, daemon=True).start()

    def process_combined(self):
        """Elaborazione combinata per entrambi i tipi di RENTRI"""
        try:
            # Mappa delle coordinate di ritaglio
            bbox_map = {
                'RENTRI NOSTRI': (1259, 37, 1649, 122),
                'RENTRI PORTALE': (1197, 72, 1633, 205)
            }
            
            input_folder = self.fir_settings.input_folder or r"O:\GIOVANNI PIO\PDF_in_input"
            output_folder = self.fir_settings.output_folder or os.path.expanduser(r"~/Desktop/Output")
            
            os.makedirs(output_folder, exist_ok=True)
            
            for filename in os.listdir(input_folder):
                if filename.lower().endswith('.pdf'):
                    pdf_path = os.path.join(input_folder, filename)
                    try:
                        images = convert_from_path(pdf_path, first_page=1, last_page=1, poppler_path=PATHS['poppler'])
                        if images:
                            # Controlla entrambe le aree e trova il miglior risultato
                            best_match = None
                            
                            for scan_type, bbox in bbox_map.items():
                                cropped = images[0].crop(bbox)
                                text = pytesseract.image_to_string(cropped).strip().upper()
                                
                                # Cerca il formato standard 5 lettere + 6 numeri + 2 lettere
                                rentri_match = re.search(r'\b([A-Z]{5})\s+(\d{6})\s+([A-Z]{2})\b', text)
                                
                                if rentri_match:
                                    best_match = rentri_match
                                    print(f"Trovato match in {scan_type}: {rentri_match.group(0)}")
                                    break  # Usa il primo match valido trovato
                            
                            # Costruzione nome file
                            if best_match:
                                valid_name = f"{best_match.group(1)} {best_match.group(2)} {best_match.group(3)}"
                            else:
                                # Gestione incrementale per file non validi
                                base_name = 'FILE_NON_VALIDO'
                                counter = 1
                                valid_name = base_name
                                
                                # Verifica se esiste già un file con questo nome e incrementa il contatore
                                while os.path.exists(os.path.join(output_folder, f"{valid_name}.pdf")):
                                    counter += 1
                                    valid_name = f"{base_name} {counter}"
                            
                            dest_path = os.path.join(output_folder, f"{valid_name}.pdf")
                            shutil.copy2(pdf_path, dest_path)
                            print(f"File processato: {filename} -> {valid_name}")

                    except Exception as e:
                        print(f"Errore elaborazione {filename}: {str(e)}")
                        self.show_error(f"Errore file {filename}: {str(e)}")

            self.show_finish_message('Elaborazione combinata completata!')
            
        except Exception as e:
            self.show_error(f"Errore critico: {str(e)}")
        finally:
            self.reset_ui()

    def start_riscontri_process(self):
        """Avvia elaborazione RISCONTRI"""
        if not self.processing:
            self.toggle_controls('disabled')
            self.progress.pack(fill=tk.X, pady=5)
            self.progress.start()
            threading.Thread(target=self.process_riscontri, daemon=True).start()

    def process_riscontri(self):
        """Elaborazione principale RISCONTRI"""
        try:
            if not all([self.riscontri_settings.input_folder, self.riscontri_settings.output_folder]):
                self.show_error("Configurare tutte le cartelle nelle impostazioni!")
                return

            os.makedirs(self.riscontri_settings.output_folder, exist_ok=True)

            for filename in os.listdir(self.riscontri_settings.input_folder):
                if filename.lower().endswith('.pdf'):
                    pdf_path = os.path.join(self.riscontri_settings.input_folder, filename)
                    try:
                        new_name = self.process_single_riscontro(pdf_path)
                        dest_path = os.path.join(self.riscontri_settings.output_folder, new_name)
                        shutil.copy2(pdf_path, dest_path)
                        print(f"File processato: {filename} -> {new_name}")
                    except Exception as e:
                        self.show_error(f"Errore file {filename}: {str(e)}")

            self.show_finish_message('Riscontri elaborati con successo!')
            
        except Exception as e:
            self.show_error(f"Errore sistema: {str(e)}")
        finally:
            self.reset_ui()

    def process_single_riscontro(self, pdf_path):
        """Elabora un singolo file RISCONTRO"""
        with fitz.open(pdf_path) as doc:
            page = doc[0]
            text = page.get_text("text", clip=(21.0, 109.0, 584.0, 171.0)) or ''
            
            try:
                prod_line = text.split("\n")[0].split("Prod. : ")[-1].split("-", 1)[-1].strip()
            except (IndexError, AttributeError):
                prod_line = "LINEA_SCONOSCIUTA"
                self.show_warning(f"Formattazione non standard in: {os.path.basename(pdf_path)}")
            
            clean_prod_line = re.sub(r'[<>:"/\\|?*]', '', prod_line).strip() or 'NON_RICONOSCIUTO'
            
            dates = re.findall(r"\d{2}/\d{2}/\d{4}", text)
            if len(dates) < 2:
                today = datetime.today().strftime('%d/%m/%Y')
                dates = [today, today]
            
            return f"Risc. Merce {clean_prod_line} dal {dates[0].replace('/', '-')} al {dates[1].replace('/', '-')}.pdf"

    def reset_ui(self):
        self.root.after(0, self.progress.stop)
        self.root.after(0, self.progress.pack_forget)
        self.root.after(0, lambda: self.toggle_controls('normal'))

    def show_finish_message(self, msg):
        self.root.after(0, lambda: messagebox.showinfo('Successo', msg))

    def show_error(self, msg):
        self.root.after(0, lambda: messagebox.showerror('Errore', msg))

    def show_warning(self, msg):
        self.root.after(0, lambda: messagebox.showwarning('Attenzione', msg))

    def show_settings(self, settings_type):
        """Mostra la finestra impostazioni"""
        settings = self.fir_settings if settings_type == 'fir' else self.riscontri_settings
        title = f"Impostazioni {settings_type.upper()}"
        
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("400x250")
        
        ttk.Button(win, text="Seleziona Input", 
                 command=lambda: self.set_folder(settings, 'input', win)).pack(pady=5)
        ttk.Button(win, text="Seleziona Output",
                 command=lambda: self.set_folder(settings, 'output', win)).pack(pady=5)
        
        if settings.input_folder:
            ttk.Label(win, text=f"Input: {settings.input_folder}", wraplength=350).pack(pady=5)
        if settings.output_folder:
            ttk.Label(win, text=f"Output: {settings.output_folder}", wraplength=350).pack(pady=5)

    def set_folder(self, settings_obj, folder_type, window):
        path = filedialog.askdirectory(title=f"Seleziona cartella {folder_type}")
        if path:
            setattr(settings_obj, f'{folder_type}_folder', path)
            settings_obj.save_settings()
            window.destroy()
            self.show_settings('fir' if settings_type == 'fir' else 'riscontri')

if __name__ == "__main__":
    root = tk.Tk()
    app = OCRTool(root)
    root.mainloop()
