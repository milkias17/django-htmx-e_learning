function removeMessages() {
  const alerts = document.querySelectorAll(".message-alert");
  for (const alert of alerts) {
    alert.addEventListener("animationend", (e) => {
      if (e.animationName == "remove-element") {
        alert.remove();
      }
    });
  }
}

document.addEventListener("DOMContentLoaded", () => {
  removeMessages();

  const targetNode = document.getElementById("message-container");

  const observer = new MutationObserver(removeMessages);
  observer.observe(targetNode, {
    childList: true,
    subtree: true,
  });
});
