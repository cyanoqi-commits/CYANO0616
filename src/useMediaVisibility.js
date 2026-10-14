import { useEffect } from 'react'
import { resetHoverVideo } from './HoverVideo'

export default function useMediaVisibility(route) {
  useEffect(() => {
    const visible = new Set()
    const videos = [...document.querySelectorAll('video')]
    const sync = () => videos.forEach(video => {
      if (document.hidden || !visible.has(video)) {
        video.pause()
        if (video.dataset.hoverSrc) resetHoverVideo(video)
      }
      else if (video.autoplay) video.play().catch(() => {})
    })
    const observer = new IntersectionObserver(entries => {
      entries.forEach(({ target: video, isIntersecting, intersectionRatio }) => {
        if (isIntersecting && intersectionRatio > 0) {
          visible.add(video)
          if (video.dataset.poster) {
            video.poster = video.dataset.poster
            delete video.dataset.poster
          }
          if (video.dataset.src) {
            video.src = video.dataset.src
            delete video.dataset.src
            video.load()
          }
        } else visible.delete(video)
      })
      sync()
    })
    const frame = requestAnimationFrame(() => videos.forEach(video => observer.observe(video)))
    document.addEventListener('visibilitychange', sync)
    return () => {
      cancelAnimationFrame(frame)
      observer.disconnect()
      document.removeEventListener('visibilitychange', sync)
      videos.forEach(video => video.pause())
    }
  }, [route])
}
