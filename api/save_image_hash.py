import os
from PIL import Image
import imagehash
import json
from concurrent.futures import ProcessPoolExecutor

image_dir  = "map_image/"

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
      for i in range(9):
        image_path = image_dir + "Elpis" + str(i) + ".webp"
        if i == 0:
          image_path = image_dir + "Elpis.webp"

        future = executor.submit(get_image_hash, image_path)
        img_hash = future.result()
        
        if img_hash is not None:
          if i == 0:
            items.append({"hash": str(img_hash), "name": "Elpis" + ".webp"})
          else:
            items.append({"hash": str(img_hash), "name": "Elpis" + str(i) + ".webp"})

  with open("image_hash.json", "w", encoding="utf-8") as f:
      json.dump(items, f, ensure_ascii=False)


# 実行
if __name__ == "__main__":
  main()