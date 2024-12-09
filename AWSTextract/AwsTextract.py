import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk
import boto3
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def upload_file():
    aws_mag_con = boto3.session.Session(profile_name='sathvik_textract')
    client = aws_mag_con.client(service_name='textract', region_name='us-west-2')
    global img
    f_types = [('Image Files', "*.jpg *.jpeg *.png *.bmp *.tiff *.gif")]  
    filename = filedialog.askopenfilename(filetypes=f_types)
    if filename: 
        try:
            img = Image.open(filename)
            img_resize = img.resize((400, 200))
            img = ImageTk.PhotoImage(img_resize)
            imgbytes = get_image_byte(filename)
            img_label.config(image=img)
            img_label.image = img  
            
            response = client.detect_document_text(Document={'Bytes': imgbytes})
            
            
            text_area.delete('1.0', tk.END)
            
            
            extracted_text = ""
            for item in response['Blocks']:
                if item['BlockType'] == 'LINE':
                    extracted_text += item['Text'] + " "

            
            text_area.insert(tk.END, extracted_text)
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error loading image or extracting text: {e}")

def get_image_byte(filename):
    with open(filename, 'rb') as imgfile:
        return imgfile.read()

def save_as_pdf():
    text = text_area.get("1.0", tk.END).strip()
    if not text:
        messagebox.showwarning("Warning", "No text to save!")
        return
    
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", 
                                            filetypes=[("PDF files", "*.pdf")])
    if file_path:
        try:
            c = canvas.Canvas(file_path, pagesize=letter)
            width, height = letter
            margin = 40
            text_object = c.beginText(margin, height - margin)
            text_object.setFont("Times-Roman", 12)
            
            
            words = text.split()
            max_width = width - 2 * margin
            line = ""
            for word in words:
                if text_object.getCursor()[0] + c.stringWidth(line + word + " ") > max_width:
                    text_object.textLine(line)
                    line = word + " "
                else:
                    line += word + " "
            if line:
                text_object.textLine(line)

            c.drawText(text_object)
            c.save()
            messagebox.showinfo("Success", "Text saved as PDF successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving PDF: {e}")


my_w = tk.Tk()
my_w.geometry("500x700")
my_w.title('AWS Textract')


my_font1 = ('Helvetica', 18, 'bold')


l1 = tk.Label(my_w, text="Upload an Image", width=30, font=my_font1)
l1.pack(pady=10)


img_label = tk.Label(my_w, borderwidth=2, relief="solid")
img_label.pack(pady=10)


text_area = ScrolledText(my_w, wrap=tk.WORD, width=50, height=8, font=('Helvetica', 12))
text_area.pack(pady=10)


upload_button = tk.Button(my_w, text='Upload Image', width=30, command=upload_file, bg='#4CAF50', fg='white', font=('Helvetica', 12, 'bold'))
upload_button.pack(pady=10)


save_button = tk.Button(my_w, text='Save as PDF', width=30, command=save_as_pdf, bg='#2196F3', fg='white', font=('Helvetica', 12, 'bold'))
save_button.pack(pady=10)


my_w.mainloop()
