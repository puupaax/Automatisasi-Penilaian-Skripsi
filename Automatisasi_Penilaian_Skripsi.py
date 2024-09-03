import subprocess
import sys
import importlib

def install_package(package):
    """Instal package menggunakan pip atau modul sudah ada."""
    try:
        importlib.import_module(package)
        print(f"Module {package} sudah terinstal.")
    except ImportError:
        print(f"Module {package} tidak ditemukan. Menginstal...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

required_packages = ['PyPDF2', 'reportlab', 'tkinter']

for package in required_packages:
    install_package(package)

import io
import os
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def add_signature_and_scores(input_pdf_path, output_pdf_path, signature_image, scores, position_signature, positions_scores):
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    packet_page1 = io.BytesIO()
    can_page1 = canvas.Canvas(packet_page1, pagesize=letter)
    can_page1.drawImage(signature_image, *position_signature[0], width=80, height=50, mask='auto')
    can_page1.save()
    
    packet_page2 = io.BytesIO()
    can_page2 = canvas.Canvas(packet_page2, pagesize=letter)
    can_page2.drawImage(signature_image, *position_signature[1], width=80, height=50, mask='auto')
    can_page2.setFont("Helvetica", 12)
    for score, pos in zip(scores, positions_scores[:-1]):
        can_page2.drawString(pos[0], pos[1], f"{score}")
    
    average_score = sum(scores) / len(scores)
    avg_position = positions_scores[-1]  
    can_page2.drawString(avg_position[0], avg_position[1], f"{average_score:.2f}".replace('.', ','))
    can_page2.save()
    
    packet_page3 = io.BytesIO()
    can_page3 = canvas.Canvas(packet_page3, pagesize=letter)
    can_page3.drawImage(signature_image, *position_signature[2], width=80, height=50, mask='auto')
    can_page3.save()

    packet_page1.seek(0)
    packet_page2.seek(0)
    packet_page3.seek(0)

    for i in range(len(reader.pages)):
        page = reader.pages[i]
        if i == 0:
            page.merge_page(PdfReader(packet_page1).pages[0])
        elif i == 1:
            page.merge_page(PdfReader(packet_page2).pages[0])
        elif i == 2:
            page.merge_page(PdfReader(packet_page3).pages[0])
        writer.add_page(page)

    with open(output_pdf_path, "wb") as output_pdf:
        writer.write(output_pdf)

def get_scores():
    scores = []
    labels = ["Penguasaan Materi", "Penyajian Tulisan", "Sistematika Pendekatan Masalah"]
    for label in labels:
        while True:
            try:
                score = simpledialog.askinteger("Input Nilai", f"Masukkan nilai untuk {label} (0-100):")
                if score is not None and 0 <= score <= 100:
                    scores.append(score)
                    break
                else:
                    tk.messagebox.showwarning("Input Error", "Nilai harus antara 0 dan 100.")
            except ValueError:
                tk.messagebox.showerror("Input Error", "Masukkan nilai yang valid.")
    return scores

def main():
    root = tk.Tk()
    root.withdraw()  

    # Pilih file PDF 
    input_pdf_path = filedialog.askopenfilename(title="Pilih file PDF", filetypes=[("PDF files", "*.pdf")])
    if not input_pdf_path:
        print("Tidak ada file yang dipilih.")
        return

    # Pilih file gambar tanda tangan
    signature_image = filedialog.askopenfilename(title="Pilih file gambar tanda tangan", filetypes=[("Image files", "*.png;*.jpg")])
    if not signature_image:
        print("Tidak ada file gambar tanda tangan yang dipilih.")
        return

    # Ambil nama file dari input PDF dan buat nama file output
    base_name = os.path.basename(input_pdf_path)
    output_pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf", title="Simpan file sebagai", initialfile=base_name)
    if not output_pdf_path:
        print("Tidak ada lokasi penyimpanan yang dipilih.")
        return

    # Nilai
    scores = get_scores()
    if not scores:
        print("Tidak ada nilai yang dimasukkan.")
        return

    # Posisi 
    position_signature = [(390, 440), (430, 313), (385, 184)]
    positions_scores = [(310, 485), (310, 450), (310, 415), (453, 450)]

    add_signature_and_scores(input_pdf_path, output_pdf_path, signature_image, scores, position_signature, positions_scores)

    messagebox.showinfo("Sukses", f"PDF telah berhasil disimpan sebagai {output_pdf_path}")

if __name__ == "__main__":
    main()
