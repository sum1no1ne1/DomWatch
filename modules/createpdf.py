import os
from PIL import Image, ImageDraw, ImageFont
import img2pdf

def pdfcreate():
    folder_path = "screenshots"
    output_pdf = os.path.join(folder_path, "output.pdf")

    # Remove old PDF if exists
    if os.path.exists(output_pdf):
        os.remove(output_pdf)

    # Get PNG files in folder
    png_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".png")]
    png_files.sort()  # optional: alphabetical

    # Process each image one by one
    for idx, filename in enumerate(png_files):
        img_path = os.path.join(folder_path, filename)
        img = Image.open(img_path)
        name = os.path.splitext(filename)[0]

        # Create new image with space for text
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

        # Save temporary file
        temp_path = os.path.join(folder_path, f"temp_{filename}")
        new_img.save(temp_path)

        # Append to PDF incrementally
        with open(output_pdf, "ab") as f:  # append binary mode
            f.write(img2pdf.convert(temp_path))

        # Remove temp image
        os.remove(temp_path)

    return f"PDF saved at: {output_pdf}"
