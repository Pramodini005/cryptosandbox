import io
import base64
from PIL import Image
import numpy as np


class SteganographyService:
    DELIMITER = "###END###"

    def hide_text(self, image_bytes: bytes, secret: str) -> bytes:
        """Hide text in image using LSB steganography."""
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        pixels = np.array(img)

        message = secret + self.DELIMITER
        binary_msg = ''.join(format(ord(c), '08b') for c in message)

        flat = pixels.flatten()
        if len(binary_msg) > len(flat):
            raise ValueError("Message too large for this image")

        for i, bit in enumerate(binary_msg):
            flat[i] = (flat[i] & ~1) | int(bit)

        result = flat.reshape(pixels.shape)
        out_img = Image.fromarray(result.astype('uint8'), 'RGB')
        buf = io.BytesIO()
        out_img.save(buf, format="PNG")
        return buf.getvalue()

    def extract_text(self, image_bytes: bytes) -> str:
        """Extract hidden text from image using LSB steganography."""
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        pixels = np.array(img)
        flat = pixels.flatten()

        bits = [str(flat[i] & 1) for i in range(min(len(flat), 1000000))]
        chars = []
        for i in range(0, len(bits) - 7, 8):
            byte = ''.join(bits[i:i+8])
            char = chr(int(byte, 2))
            chars.append(char)
            if ''.join(chars[-len(self.DELIMITER):]) == self.DELIMITER:
                return ''.join(chars[:-len(self.DELIMITER)])

        raise ValueError("No hidden message found or delimiter missing")

    def get_capacity(self, image_bytes: bytes) -> dict:
        """Calculate steganographic capacity of an image."""
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        pixels = np.array(img)
        total_bits = pixels.size
        max_chars = total_bits // 8 - len(self.DELIMITER)
        return {
            "width": img.width,
            "height": img.height,
            "total_pixels": img.width * img.height,
            "max_characters": max(0, max_chars),
            "max_bytes": max(0, max_chars),
        }


steganography_service = SteganographyService()
