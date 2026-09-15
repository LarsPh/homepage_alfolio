const workVideos = document.querySelectorAll(".work-video");
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
if (workVideos.length && "IntersectionObserver" in window) {
  const observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        const video = entry.target;
        if (entry.isIntersecting && !reducedMotion.matches) {
          video.muted = true;
          video.play().catch(() => {}); // Native controls remain available if autoplay is blocked.
        } else {
          video.pause();
        }
      }
    },
    { threshold: 0.25 }
  );
  workVideos.forEach((video) => observer.observe(video));
  reducedMotion.addEventListener("change", () => {
    if (reducedMotion.matches) workVideos.forEach((video) => video.pause());
  });
}
