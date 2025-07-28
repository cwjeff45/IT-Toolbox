// script.js

function toggleMenu() {
  const menu = document.getElementById("sideMenu");
  if (menu.style.left === "0px") {
    menu.style.left = "-200px";
  } else {
    menu.style.left = "0px";
  }
}
