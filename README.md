# OCR PDF Image GUI ✨

Ciao! 👋 Questa repo ti permette di convertire PDF in immagini e usare l'OCR (riconoscimento testi) in una semplice interfaccia grafica 🖼️. Tutto in Python, senza stress… ma prima serve la giusta configurazione! 💻

## Come partire 🚀

Scarica le dipendenze con:
pip install -r requisiti.txt

text

Installa Tesseract OCR 🦾: scarica Tesseract da [qui](https://github.com/tesseract-ocr/tesseract) (Windows: consigliato installer .exe) e ricorda dove lo installi, ad esempio: `C:\Program Files\Tesseract-OCR\tesseract.exe`

Installa Poppler 📄: serve anche Poppler per la conversione PDF→immagini, scaricalo da [questo link](http://blog.alivate.com.au/poppler-windows/) e estrai dove preferisci, ad esempio: `C:\Program Files\poppler\bin`

Devi configurare i percorsi di tesseract.exe e poppler nel codice! Trova le righe tipo queste e inserisci i tuoi percorsi:
Esempio per tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

Esempio per poppler
images = convert_from_path(pdf_path, poppler_path=r'C:\Program Files\poppler\bin')

text

> Se hai Windows, usa i doppio backslash `\\` o una stringa raw `r'...'`!

Ora puoi lanciare il programma e divertirti con l'OCR super-veloce! 😎 Se hai domande lascia una issue ✍️

Non dimenticare: **os**, **json**, **tkinter** sono già nella Standard Library; su Linux puoi installare tutto con:
sudo apt install poppler-utils
sudo apt install tesseract-ocr

text

Happy hacking! 🚦🧠
