document.addEventListener("DOMContentLoaded", function () {
  console.log("script loaded");
  const video = document.querySelector("video");

  document.addEventListener("keydown", (e) => {
    if (e.code !== "Space") return;
    if (video.paused) {
      video.play();
    } else {
      video.pause();
    }
  });
});
