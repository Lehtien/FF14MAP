<script setup>
import { ref } from 'vue';
import axios from 'axios'

const paste_img = ref(null)
const getImage = (e) => {
  if (e.clipboardData.types[0] === 'Files') {
    const pastedImage = e.clipboardData.items[0].getAsFile();
    // paste_img.value = URL.createObjectURL(pastedImage);
    const reader = new FileReader();
    reader.onload = (e) => {
      paste_img.value.src = e.target.result;
      console.log(paste_img.value)
    }
    reader.readAsDataURL(pastedImage)

    const fd = new FormData()
    fd.append("MAX_FILE_SIZE", 2097152);
    fd.append("upload_file", pastedImage);

    axios.post('http://127.0.0.1:8000/uploadfile', fd
    ).then((response) => {
      console.log(response.data)
    }).catch((error) => {
      console.log(error)
    })
  }
} 
</script>

<template>
  <div>
    <div contenteditable @paste.prevent="getImage" class="paste_area">
      <img :src=paste_img ref="paste_img" alt/>
    </div>
  </div>
</template>s

<style lang="scss" scoped>
.paste_area {
  border: 1px solid white;
  width: 480px;
  height: 340px;
}
</style>
