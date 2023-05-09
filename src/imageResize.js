import imageCompression from "browser-image-compression";

export default {
  // アップロードされた画像ファイルを取得
  async getCompressImageFileAsync(file) {
    const options = {
      maxSizeMB: 10, // 最大ファイルサイズ
      maxWidthOrHeight: 800 // 最大画像幅もしくは高さ
    };
    try {
      // 圧縮画像の生成
      return await imageCompression(file, options);
    } catch (error) {
      console.error("getCompressImageFileAsync is error", error);
      throw error;
    }
  }
};