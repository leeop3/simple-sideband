# src/utils/image_handler.py
# Handles image compression and encoding

import base64
from PIL import Image
from io import BytesIO
import os

def compress_and_encode_image(image_path, max_size_kb=200, quality=75, max_dimension=800):
    try:
        img = Image.open(image_path)
        if img.mode in ("RGBA", "P", "LA"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            background.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
            img = background
        if max(img.size) > max_dimension:
            ratio = max_dimension / max(img.size)
            new_size = tuple(int(dim * ratio) for dim in img.size)
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        current_quality = quality
        while current_quality > 10:
            buffer = BytesIO()
            img.save(buffer, format="JPEG", quality=current_quality, optimize=True)
            size_kb = buffer.tell() / 1024
            if size_kb <= max_size_kb:
                break
            current_quality -= 10
        buffer.seek(0)
        encoded = base64.b64encode(buffer.read()).decode("ascii")
        metadata = {
            "filename": os.path.basename(image_path),
            "original_size": os.path.getsize(image_path),
            "compressed_size": len(encoded),
            "dimensions": img.size,
            "quality_used": current_quality
        }
        print("Image compressed successfully")
        return encoded, metadata
    except Exception as e:
        print("Error processing image: " + str(e))
        return None, None

def decode_and_save_image(encoded_data, output_path):
    try:
        image_data = base64.b64decode(encoded_data)
        with open(output_path, "wb") as f:
            f.write(image_data)
        print("Image saved: " + output_path)
        return True
    except Exception as e:
        print("Error saving image: " + str(e))
        return False
