//frontend/js/main.js


import { articleModule } from "./articles.js";
import { cdcModule } from "./cdcs.js";
import { dtModule } from "./dts.js";

document.addEventListener("DOMContentLoaded", () => {
    // Sidebar : afficher la section Articles par défaut
    document.getElementById("articles-section").style.display = "block";

    const menuItems = document.querySelectorAll(".menu-item");
    const sections = document.querySelectorAll("main section");

    menuItems.forEach(item => {
        item.addEventListener("click", e => {
            e.preventDefault();
            // Activer le menu sélectionné
            menuItems.forEach(i => i.classList.remove("active"));
            item.classList.add("active");

            // Afficher uniquement la section correspondante
            const target = item.dataset.target;
            sections.forEach(sec => {
                sec.style.display = sec.id === target ? "block" : "none";
            });
        });
    });

    // Initialiser les modules
    articleModule.init();
    cdcModule.init();
    dtModule.init();
});
