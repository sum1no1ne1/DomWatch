import os
from PIL import Image, ImageDraw, ImageFont
import img2pdf

def pdfcreate():
    folder_path = "screenshots"
    output_pdf = os.path.join(folder_path, "output.pdf")

    # Remove old PDF if exists
    if os.path.exists(output_pdf):
        os.remove(output_pdf)

    # Get all PNG files
    png_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".png")]
    if not png_files:
        return "No screenshots to create PDF."

    png_files.sort()  # optional: maintain order

    # Combine all images into a single PDF
    pdf_bytes = []
    for filename in png_files:
        img_path = os.path.join(folder_path, filename)
        img = Image.open(img_path)
        name = os.path.splitext(filename)[0]

        # Add space for text above image
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

        # Save temporary image to append to PDF
        temp_path = os.path.join(folder_path, f"temp_{filename}")
        new_img.save(temp_path)
        pdf_bytes.append(temp_path)

    # Write all images to a single PDF
    with open(output_pdf, "wb") as f:
        f.write(img2pdf.convert(pdf_bytes))

    # Remove temporary images
    for temp_img in pdf_bytes:
        os.remove(temp_img)

    return f"PDF saved at: {output_pdf}"
