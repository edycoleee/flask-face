import os
from PIL import Image

folder = "/home/sultan/Downloads/data"

for filename in os.listdir(folder):
    # Abaikan folder
    if os.path.isdir(os.path.join(folder, filename)):
        continue

    name, ext = os.path.splitext(filename)

    # Jika file TIDAK punya ekstensi, atau ekstensinya bukan jpg/png
    if ext == "" or ext.lower() not in [".jpg", ".jpeg", ".png"]:
        input_path = os.path.join(folder, filename)
        output_path = os.path.join(folder, name + ext + ".jpg")

        try:
            img = Image.open(input_path)
            img = img.convert("RGB")  # ambil frame pertama GIF
            img.save(output_path, "JPEG")

            print(f"Converted: {filename} → {output_path}")

        except Exception as e:
            print(f"Gagal memproses {filename}: {e}")

print("Semua selesai!")
