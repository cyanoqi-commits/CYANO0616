import images from './optimizedImages.json'
import thumbnails from './thumbnailAssets.json'

export default function mediaAsset(path, thumbnail = false) {
  const resolved = images[path] ?? path
  return `${import.meta.env.BASE_URL}${thumbnail ? thumbnails[resolved] ?? resolved : resolved}`
}
