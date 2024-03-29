<script setup>
import { ref, computed } from 'vue';
import axios from 'axios';
import ImageUtil from "../../imageResize";

const map_list = ref(['G15', 'G14', 'G12'])
const paste_img = ref(null)       //  貼り付けられた画像
const imageSelected = ref(false)  //  画像が選択されたかどうか
const coordinatesList = ref([])
const similar_img = ref([])     // 類似画像
const selected_map = ref("G15") // 地図種選択
const selected_area = ref(null)
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
    compFile.then((data) => {
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
      coordinatesList.value = [];
      let url = `${import.meta.env.VITE_APP_API_BASE_URL}${selected_map.value}`;
      if (selected_area.value !== null) {
        url += `?selected_area=${selected_area.value}`;
      }
      axios.post(url, fd
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

const area_select = computed(() => {
  switch (selected_map.value) {
    case 'G15':
      return [{"jp": "エルピス", "en": "Elpis"}];
    case 'G14':
      return [{"jp": "ガレマルド", "en": "Garlemald"}, {"jp": "ラヴィリンソス", "en": "Labyrinthos"}, {"jp": "嘆きの海", "en": "MareLamentorum"}, {"jp": "サベネア島", "en": "Thavnair"}, {"jp": "ウルティマトゥーレ", "en": "UltimaThule"}];
    case 'G12':
      return [{"jp": "レイクランド", "en": "Lakeland"}, {"jp": "コルシア島", "en": "Kholusia"}, {"jp": "アムアレーン", "en": "AmhAraeng"}, {"jp": "イルメグ", "en": "IlMheg"}, {"jp": "ラケティカ森林", "en": "theRakTikaGreatwood"}, {"jp": "テンペスト", "en": "theTempest"}]
    default:
      return []
  }
})

// mobile判定
const isMobile = ref(false)
const regex = new RegExp(/iPhone|Android.+Mobile/);
isMobile.value = regex.test(navigator.userAgent);
</script>

<template>
  <div>
    <div class="summary">
      <h1>【FF14】地図座標を探す | Treasure hunt</h1>
      <ol v-if="isMobile">
        <li>検索項目を選択して絞り込み</li>
        <li>ファイルを選択をタップする</li>
        <li>画像を撮影する</li>
      </ol>
      <ol v-else>
        <li>&ensp;検索項目を選択して絞り込み</li>
        <li>［Win］+［Shift］+［S］キーで地図を綺麗に撮影</li>
        <li>［Ctrl］+［V］キーで下の枠内に貼り付け</li>
      </ol>
    </div>
    <div class="map_select">
      <select name="map_select" id="map_select" v-model="selected_map">
        <option v-for="map in map_list" :key="map">{{ map }}</option>
      </select>
      <select name="area_select" id="area_select" v-model="selected_area">
        <option v-for="area in area_select" :key="area['jp']" :value="area['en']">{{ area["jp"] }}</option>
      </select>
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
}
</style>
