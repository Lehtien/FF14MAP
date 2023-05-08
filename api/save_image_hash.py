import os
from PIL import Image
import imagehash
import json
from concurrent.futures import ProcessPoolExecutor

image_dir  = "map_image/G15/"

# image_hashの取得
def get_image_hash(image_path):
  if os.path.isfile(image_path):
    return imagehash.average_hash(Image.open(image_path))
  else:
    return None


# main関数
def main():
  items = []
  with ProcessPoolExecutor(max_workers=4) as executor:
      for i in range(1,9):
        image_path = image_dir + "Elpis" + str(i) + ".webp"

        future = executor.submit(get_image_hash, image_path)
        img_hash = future.result()
        
        if img_hash is not None:
            items.append({"hash": str(img_hash), "name": "Elpis" + str(i) + ".webp"})

  with open("map_hash/image_hash_G15.json", "w", encoding="utf-8") as f:
      json.dump(items, f, ensure_ascii=False)


# 実行
if __name__ == "__main__":
  main()