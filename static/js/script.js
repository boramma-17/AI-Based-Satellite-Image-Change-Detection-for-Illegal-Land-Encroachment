// Auto-dismiss flash messages after a few seconds
document.addEventListener("DOMContentLoaded", () => {
  const flashes = document.querySelectorAll(".flash");
  flashes.forEach((el) => {
    setTimeout(() => {
      el.style.transition = "opacity 0.5s ease";
      el.style.opacity = "0";
      setTimeout(() => el.remove(), 500);
    }, 5000);
  });

  // Simple client-side preview for image inputs on the upload page
  const beforeInput = document.getElementById("before_image");
  const afterInput = document.getElementById("after_image");

  const attachPreview = (input) => {
    if (!input) return;
    input.addEventListener("change", () => {
      const file = input.files[0];
      if (!file) return;
      const maxSizeMB = 16;
      if (file.size / (1024 * 1024) > maxSizeMB) {
        alert(`File too large. Max size is ${maxSizeMB}MB.`);
        input.value = "";
      }
    });
  };

  attachPreview(beforeInput);
  attachPreview(afterInput);
});