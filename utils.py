import json
import os


class ExportUtils:
    @staticmethod
    def save_album(album_data, tracklist, image, folder_path):
        album_name = album_data["album_name"].replace(" ", "_")

        json_path = os.path.join(folder_path, f"{album_name}.json")
        png_path = os.path.join(folder_path, f"{album_name}.png")

        export_data = {
            "album": album_data,
            "tracks": tracklist
        }

        with open(json_path, "w", encoding="utf-8") as file:
            json.dump(export_data, file, indent=4, ensure_ascii=False)

        image.save(png_path)