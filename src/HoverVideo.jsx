import assets from './videoAssets.json'

export function playHoverVideo(video) {
  if (!video) return
  if (!video.getAttribute('src')) video.src = video.dataset.hoverSrc
  video.play().catch(() => {})
}

export function resetHoverVideo(video) {
  if (!video || !video.getAttribute('src')) return
  video.pause()
  video.removeAttribute('src')
  video.load()
}

export default function HoverVideo({ src, onClick, label }) {
  const path = src.split('?')[0]
  const media = assets[path]
  return <video
    data-hover-src={`${import.meta.env.BASE_URL}${src}`}
    data-poster={`${import.meta.env.BASE_URL}${media.poster}`}
    width={media.width} height={media.height}
    muted loop playsInline preload="none" aria-label={label}
    onMouseEnter={(event) => playHoverVideo(event.currentTarget)}
    onMouseLeave={(event) => resetHoverVideo(event.currentTarget)}
    onClick={onClick}
  />
}
