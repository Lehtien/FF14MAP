<script setup>
import { ref } from 'vue';
import axios from 'axios';
import ImageUtil from "../../imageResize";

const paste_img = ref(null)       //  貼り付けられた画像
const imageSelected = ref(false)  //  画像が選択されたかどうか
const coordinatesList = ref([])
const similar_img = ref([])     // 類似画像
const select = ref("G15")       // 地図種選択
const error_message = ref("")

const getImage = (e) => {
  error_message.value = "";
  if ((!isMobile.value && e.clipboardData.types[0] === 'Files') || isMobile.value && e.target.files.length > 0) {
    let pastedImage = null;
    if (!isMobile.value) {
      pastedImage = e.clipboardData.items[0].getAsFile();
    } else {
      pastedImage = e.target.files[0]
    }

    const compFile = ImageUtil.getCompressImageFileAsync(pastedImage)
    compFile.then((data)=> {
      pastedImage = data;

    const reader = new FileReader();
    reader.onload = (e) => {
      paste_img.value.src = e.target.result;
    }
    reader.readAsDataURL(pastedImage)
    imageSelected.value = true;

    const fd = new FormData()
    fd.append("MAX_FILE_SIZE", 10485760);
    fd.append("upload_file", pastedImage);

    similar_img.value = []
    axios.post(`${import.meta.env.VITE_APP_API_BASE_URL}${select.value}`, fd
    ).then((response) => {
      const coordinates = response.data.coordinates;
      for (let place of coordinates) {
        coordinatesList.value.push(place[0])
      }
      const image_list = response.data.image_data;
      for (let image of image_list) {
        similar_img.value.push("data:image/*;base64," + image)
      }
    }).catch((error) => {
      error_message.value = error.response.data.error_message || error.message;
    })
  })
  }
}

// mobile判定
const isMobile = ref(false)
const regex = new RegExp(/iPhone|Android.+Mobile/);
isMobile.value = regex.test(navigator.userAgent);
</script>

<template>
  <div>
    <div class="summary">
      <h1>地図座標を探す | Treasure hunt</h1>
      <ol v-if="isMobile">
        <li>ファイルを選択をタップする</li>
        <li>画像を撮影する</li>
      </ol>
      <ol v-else>
        <li>［Win］+［Shift］+［S］キーで地図を綺麗に撮影</li>
        <li>［Ctrl］+［V］キーで下の枠内に貼り付け</li>
      </ol>
    </div>
    <div class="map_select">
      <input type="radio" v-model="select" value="G15" id="G15">
      <label for="G15">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512" class="map_icon">
          <path
            d="M565.6 36.2C572.1 40.7 576 48.1 576 56V392c0 10-6.2 18.9-15.5 22.4l-168 64c-5.2 2-10.9 2.1-16.1 .3L192.5 417.5l-160 61c-7.4 2.8-15.7 1.8-22.2-2.7S0 463.9 0 456V120c0-10 6.1-18.9 15.5-22.4l168-64c5.2-2 10.9-2.1 16.1-.3L383.5 94.5l160-61c7.4-2.8 15.7-1.8 22.2 2.7zM48 136.5V421.2l120-45.7V90.8L48 136.5zM360 422.7V137.3l-144-48V374.7l144 48zm48-1.5l120-45.7V90.8L408 136.5V421.2z" />
        </svg>
        G15
      </label>
      <input type="radio" v-model="select" value="G14" id="G14">
      <label for="G14">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512" class="map_icon">
          <path
            d="M565.6 36.2C572.1 40.7 576 48.1 576 56V392c0 10-6.2 18.9-15.5 22.4l-168 64c-5.2 2-10.9 2.1-16.1 .3L192.5 417.5l-160 61c-7.4 2.8-15.7 1.8-22.2-2.7S0 463.9 0 456V120c0-10 6.1-18.9 15.5-22.4l168-64c5.2-2 10.9-2.1 16.1-.3L383.5 94.5l160-61c7.4-2.8 15.7-1.8 22.2 2.7zM48 136.5V421.2l120-45.7V90.8L48 136.5zM360 422.7V137.3l-144-48V374.7l144 48zm48-1.5l120-45.7V90.8L408 136.5V421.2z" />
        </svg>
        G14
      </label>
    </div>
    <div v-if="isMobile" class="paste_area">
      <input type="file" id="environment" capture="environment" accept="image/*" @change="getImage">
      <img :src=paste_img ref="paste_img" alt v-if="imageSelected" />
    </div>
    <div v-else contenteditable @paste.prevent="getImage" class="paste_area">
      <img :src=paste_img ref="paste_img" alt v-if="imageSelected" />
    </div>
    <p>(C) SQUARE ENIX CO., LTD. All Rights Reserved.</p>
    <div class="similar_images">
      <p class="error_message" v-if="error_message !== ''">{{ error_message }}</p>
      <picture v-for="(img_src, index) in similar_img" :key="img_src">
        <span v-if="index % 2 === 0">候補{{ index / 2 + 1 }}：</span>
        <img :src="img_src" alt />
        <div v-if="index % 2 === 0">
          <p>
            {{ coordinatesList[index / 2]["point"] }}
            X: {{ coordinatesList[index / 2]["X"].toFixed(1) }},
            Y: {{ coordinatesList[index / 2]["Y"].toFixed(1) }}
          </p>
        </div>
      </picture>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.paste_area {
  border: 1px solid white;
  width: 480px;
  height: 340px;
  position: relative;

  img {
    max-width: 80%;
    max-height: 90%;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
  }
}

.similar_images {
  padding: 1em;

  picture {
    margin-bottom: 2em;

    span {
      vertical-align: top;
    }

    p {
      font-size: 1.5em;
      vertical-align: center;
    }
  }

  display: grid;
  grid-template-columns: 0.3fr 1fr;

  picture:nth-child(odd)>img {
    width: 80%;
  }

  picture:nth-child(even)>img {
    width: 50%;
  }
}

@media screen and (max-width: 768px) {
  .paste_area {
    width: 100%;
    height: 220px;

    img {
      max-width: 80%;
      max-height: 75%;
    }
  }

  .similar_images {
    grid-template-columns: 1fr;

    picture:nth-child(odd)>img {
      width: 50%;
    }

    picture:nth-child(even)>img {
      width: 100%;
    }

    picture {
      margin-bottom: 0;

      span {
        display: block;
      }
    }
  }
}

.summary {
  margin-bottom: 2em;
}

.map_icon {
  width: 1.1em;
  fill: white;
  margin: 0 0.1em 0 0.5em;
}

.error_message {
  color: red;
  position: absolute;
  top: 1em;
}</style>
