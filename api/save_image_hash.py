import os
from PIL import Image
import imagehash
import json
from concurrent.futures import ProcessPoolExecutor

map_name = "G15"
image_dir = f"map_image/{map_name}/"
# image_name_list = ["Garlemald", "Labyrinthos", "MareLamentorum", "Thavnair", "UltimaThule"]
image_name_list = ["Elpis"]

# image_hashの取得
def get_image_hash(image_path):
    if os.path.isfile(image_path):
        return imagehash.phash(Image.open(image_path))
    else:
        return None

# main関数
def main():
    items = []
    with ProcessPoolExecutor(max_workers=4) as executor:
        for image_name in image_name_list:
            for i in range(1, 9):
                image_path = image_dir + image_name + str(i) + ".webp"

                future = executor.submit(get_image_hash, image_path)
                img_hash = future.result()

                if img_hash is not None:
                    items.append({"hash": str(img_hash), "name": image_name + str(i) + ".webp"})

    with open(f"map_hash/image_hash_{map_name}.json", "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False)


# 実行
if __name__ == "__main__":
    main()
