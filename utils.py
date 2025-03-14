from PIL import Image, ImageDraw

def crop_image_to_circle(input_path, output_path):
    img = Image.open(input_path).convert("RGBA")
    size = min(img.size)

    # Crop to square
    left = (img.width - size) // 2
    top = (img.height - size) // 2
    right = left + size
    bottom = top + size
    img_cropped = img.crop((left, top, right, bottom))

    # Create circular mask
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)

    # Apply mask
    img_cropped.putalpha(mask)

    # Save with transparency
    img_cropped.save(output_path, format="PNG")