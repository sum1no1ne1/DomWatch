import os
import shutil
from PIL import Image, ImageDraw, ImageFont
import img2pdf

def pdfcreate():
    
    folder_path = "screenshots"
    output_pdf = os.path.join("screenshots", "output.pdf")
    temp_folder = os.path.join(folder_path, "temp")

    os.makedirs(temp_folder, exist_ok=True)
    edited_images = []

    for filename in os.listdir(folder_path):
        if not filename.lower().endswith(".png"):
            continue

        img_path = os.path.join(folder_path, filename)
        img = Image.open(img_path)
        name = os.path.splitext(filename)[0]

        text_space = 50
        new_img = Image.new("RGB", (img.width, img.height + text_space), "white")
        new_img.paste(img, (0, text_space))

        draw = ImageDraw.Draw(new_img)
        try:
            font = ImageFont.truetype("arial.ttf", 30)
        except:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), name, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (img.width - text_width) / 2
        y = (text_space - text_height) / 2
        draw.text((x, y), name, fill="black", font=font)

        temp_path = os.path.join(temp_folder, filename)
        new_img.save(temp_path)
        edited_images.append(temp_path)

    with open(output_pdf, "wb") as f:
        f.write(img2pdf.convert(edited_images))

   
    delete_temp = True 
    if delete_temp:
        shutil.rmtree(temp_folder)

    return f" PDF saved at: {output_pdf}"
