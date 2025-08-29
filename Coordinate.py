import tkinter as tk
from tkinter import filedialog
from pdf2image import convert_from_path
from PIL import Image, ImageTk

class CoordinateSelector:
    def __init__(self, root):
        self.root = root
        self.root.title('Seleziona Area')

        self.canvas = tk.Canvas(root, cursor="cross")
        self.canvas.pack(expand=True, fill=tk.BOTH)
        
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.bbox = None

        # Carica un PDF di esempio
        self.load_pdf()

    def load_pdf(self):
        file_path = filedialog.askopenfilename(title="Seleziona un file PDF",
                                               filetypes=(("PDF files", "*.pdf"), ("all files", "*.*")))
        if file_path:
            images = convert_from_path(file_path, poppler_path=r"O:\GIOVANNI PIO\poppler-24.08.0\Library\bin")
            if images:
                self.image = images[0]  # Usa la prima pagina del PDF
                self.tk_image = ImageTk.PhotoImage(self.image)
                self.canvas.config(width=self.tk_image.width(), height=self.tk_image.height())
                self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

                # Bind del mouse per la selezione dell'area
                self.canvas.bind("<ButtonPress-1>", self.on_button_press)
                self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
                self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def on_button_press(self, event):
        # Inizio della selezione dell'area
        self.start_x = event.x
        self.start_y = event.y
        
    def on_mouse_drag(self, event):
        # Aggiorna il rettangolo durante il drag
        if self.rect:
            self.canvas.delete(self.rect)
        
        cur_x, cur_y = (event.x, event.y)
        
        # Disegna il rettangolo di selezione
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, cur_x, cur_y, outline='red')

    def on_button_release(self, event):
        # Fine della selezione dell'area
        end_x, end_y = (event.x, event.y)
        
        # Imposta la bounding box basata sulla selezione dell'utente
        if end_x > self.start_x and end_y > self.start_y:
            self.bbox = (self.start_x, self.start_y, end_x, end_y)
            print(f"Bounding box selezionata: {self.bbox}")

if __name__ == '__main__':
    root = tk.Tk()
    app = CoordinateSelector(root)
    root.mainloop()
