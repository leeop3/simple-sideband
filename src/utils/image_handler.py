# utils/image_handler.py
import base64
import os
from io import BytesIO
from PIL import Image


def compress_and_encode_image(image_path, max_size_kb=200, quality=75, max_dimension=800):
    try:
        img = Image.open(image_path)

        # Convert non-RGB modes to RGB with white background
        if img.mode in ("RGBA", "P", "LA"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            mask = img.split()[-1] if img.mode in ("RGBA", "LA") else None
            background.paste(img, mask=mask)
            img = background
        elif img.mode != "RGB":
            img = img.convert("RGB")

        # Resize if larger than max_dimension on either side
        if max(img.size) > max_dimension:
            ratio = max_dimension / max(img.size)
            new_size = tuple(int(dim * ratio) for dim in img.size)
            # FIX: LANCZOS attribute moved in Pillow 10+; fall back gracefully
            resample = getattr(Image, "Resampling", Image).LANCZOS
            img = img.resize(new_size, resample)

        # Compress, reducing quality until under max_size_kb
        current_quality = quality
        buffer = BytesIO()
        while current_quality >= 10:
            buffer = BytesIO()
            img.save(buffer, format="JPEG", quality=current_quality, optimize=True)
            size_kb = buffer.tell() / 1024
            if size_kb <= max_size_kb:
                break
            current_quality -= 10

        # FIX: always seek(0) after the loop, whether we broke early or exhausted quality
        buffer.seek(0)
        encoded = base64.b64encode(buffer.read()).decode("ascii")

        metadata = {
            "filename": os.path.basename(image_path),
            "original_size": os.path.getsize(image_path),
            "compressed_size": len(encoded),
            "dimensions": img.size,
            "quality_used": current_quality
        }
        print("Image compressed: " + metadata["filename"]
              + " q=" + str(current_quality)
              + " size=" + str(round(buffer.tell() / 1024, 1)) + "kb")
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
