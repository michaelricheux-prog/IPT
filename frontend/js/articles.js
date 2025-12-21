export const articleModule = (function() {
    const modal = document.getElementById("article-modal");
    const form = document.getElementById("article-form");

    function openModal(mode, code = null) {
        modal.classList.add("active");
        document.getElementById("modal-title").textContent =
            mode === "edit" ? "Éditer Article" : "Ajouter Article";

        if (mode === "edit" && code) {
            fetch(`${window.location.origin}/articles/${code}`)
                .then(res => res.json())
                .then(a => {
                    document.getElementById("ArticleCode").value = a.ArticleCode;
                    document.getElementById("ArticleCode").disabled = true;
                    document.getElementById("ArticleDesignation").value = a.ArticleDesignation;
                });
        } else {
            form.reset();
            document.getElementById("ArticleCode").disabled = false;
        }

        form.dataset.mode = mode;
    }

    function closeModal() {
        modal.classList.remove("active");
        form.dataset.mode = "";
    }

    function bindRowActions() {
        document.querySelectorAll(".btn-edit").forEach(btn => {
            btn.addEventListener("click", () => openModal("edit", btn.dataset.code));
        });
        document.querySelectorAll(".btn-delete").forEach(btn => {
            btn.addEventListener("click", async () => {
                if (!confirm("Confirmer la suppression ?")) return;
                await fetch(`${window.location.origin}/articles/${btn.dataset.code}`, { method: "DELETE" });
                loadArticles();
            });
        });
    }

    async function loadArticles() {
        const res = await fetch(`${window.location.origin}/articles/`);
        const articles = await res.json();
        const tbody = document.getElementById("tbody-articles");

        tbody.innerHTML = articles.length === 0
            ? `<tr><td colspan="3">Aucun article</td></tr>`
            : articles.map(a => `
                <tr>
                    <td>${a.ArticleCode}</td>
                    <td>${a.ArticleDesignation}</td>
                    <td>
                        <button class="btn-edit" data-code="${a.ArticleCode}">✏️</button>
                        <button class="btn-delete" data-code="${a.ArticleCode}">🗑️</button>
                    </td>
                </tr>
            `).join("");

        bindRowActions();
    }

    function initForm() {
        form.addEventListener("submit", async e => {
            e.preventDefault();
            const mode = form.dataset.mode;
            const ArticleCode = document.getElementById("ArticleCode").value.trim();
            const ArticleDesignation = document.getElementById("ArticleDesignation").value.trim();

            let res;
            if (mode === "edit") {
                res = await fetch(`${window.location.origin}/articles/${ArticleCode}`, {
                    method: "PATCH",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ ArticleDesignation })
                });
            } else {
                res = await fetch(`${window.location.origin}/articles/`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ ArticleCode, ArticleDesignation })
                });
            }

            if (!res.ok) {
                const t = await res.text();
                alert(t || "Erreur");
                return;
            }

            closeModal();
            loadArticles();
        });
    }

    function init() {
        const btnAdd = document.getElementById("btn-add-article");
        const btnClose = document.getElementById("modal-close");
        const btnCancel = document.getElementById("modal-cancel");
        // const searchInput = document.getElementById("q"); <-- retirer

        btnAdd.addEventListener("click", () => openModal("add"));
        btnClose.addEventListener("click", closeModal);
        btnCancel.addEventListener("click", closeModal);
        modal.addEventListener("click", e => { if (e.target === modal) closeModal(); });

        // searchInput.addEventListener("input", loadArticles); <-- retirer

        initForm();
        loadArticles(); // ⚡ important pour charger au démarrage
    }

    return { init, loadArticles };
})();
