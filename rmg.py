from rembg import remove
from PIL import Image

input_path = "sprites_sheet.png"
output_path = "sprites_sheet_transparent.png"

with open(input_path, "rb") as i:
    with open(output_path, "wb") as o:
        o.write(remove(i.read()))