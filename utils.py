import json
import os


class ExportUtils:
    @staticmethod
    def save_album(album_data, tracklist, image, folder_path):
        # REQUIREMENT 8: Klasör içine fiktif meta verileri JSON ve kapağı PNG olarak aktarma
        # Dosya sisteminde hata yaratmaması için geçersiz karakterleri temizliyoruz
        safe_album_name = "".join(
            c for c in album_data.get("album_name", "album") if c.isalnum() or c in (" ", "_", "-")).strip().replace(
            " ", "_")

        json_path = os.path.join(folder_path, f"{safe_album_name}.json")
        png_path = os.path.join(folder_path, f"{safe_album_name}.png")

        export_data = {
            "fictional_album_metadata": album_data,
            "real_tracklist": tracklist
        }

        # Türkçe karakter korumalı UTF-8 JSON kaydı
        with open(json_path, "w", encoding="utf-8") as file:
            json.dump(export_data, file, indent=4, ensure_ascii=False)

        # PNG görsel kaydı
        image.save(png_path, "PNG")
