export const dtModule = (function() {
    const modal = document.getElementById("dt-modal");
    const form = document.getElementById("dt-form");

    function openModal(mode, dtId = null) {
        modal.classList.add("active");
        document.getElementById("dt-modal-title").textContent = mode === "edit" ? "Éditer DT" : "Ajouter DT";

        // Charger les articles dans le select
        fetch(`${window.location.origin}/articles/`)
            .then(res => res.json())
            .then(articles => {
                const select = document.getElementById("article-select");
                select.innerHTML = articles.map(a => `<option value="${a.id}">${a.ArticleDesignation}</option>`).join("");
            });

        if (mode === "edit" && dtId) {
            fetch(`${window.location.origin}/dts/${dtId}`)
                .then(res => res.json())
                .then(dt => {
                    document.getElementById("DTCode").value = dt.DTCode;
                    document.getElementById("article-select").value = dt.article_id;
                });
        } else {
            form.reset();
        }

        form.dataset.mode = mode;
        form.dataset.dtId = dtId || "";
    }

    function closeModal() {
        modal.classList.remove("active");
        form.dataset.mode = "";
        form.dataset.dtId = "";
    }

    function bindRowActions() {
        document.querySelectorAll(".btn-edit-dt").forEach(btn => {
            btn.addEventListener("click", () => openModal("edit", btn.dataset.id));
        });
        document.querySelectorAll(".btn-delete-dt").forEach(btn => {
            btn.addEventListener("click", async () => {
                if (!confirm("Confirmer la suppression ?")) return;
                await fetch(`${window.location.origin}/dts/${btn.dataset.id}`, { method: "DELETE" });
                loadDTs();
            });
        });
    }

    async function loadDTs() {
        const res = await fetch(`${window.location.origin}/dts/`);
        const dts = await res.json();
        const tbody = document.getElementById("tbody-dts");

        tbody.innerHTML = dts.length === 0
            ? `<tr><td colspan="3">Aucune DT</td></tr>`
            : dts.map(dt => `
                <tr>
                    <td>${dt.DTCode}</td>
                    <td>${dt.article ? dt.article.ArticleDesignation : "N/A"}</td>
                    <td>
                        <button class="btn-edit-dt" data-id="${dt.id}">✏️</button>
                        <button class="btn-delete-dt" data-id="${dt.id}">🗑️</button>
                    </td>
                </tr>
            `).join("");

        bindRowActions();
    }

    function initForm() {
        form.addEventListener("submit", async e => {
            e.preventDefault();
            const mode = form.dataset.mode;
            const dtId = form.dataset.dtId;
            const DTCode = document.getElementById("DTCode").value.trim();
            const article_id = parseInt(document.getElementById("article-select").value);

            let res;
            if (mode === "edit") {
                res = await fetch(`${window.location.origin}/dts/${dtId}`, {
                    method: "PATCH",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ DTCode, article_id })
                });
            } else {
                res = await fetch(`${window.location.origin}/dts/`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ DTCode, article_id })
                });
            }

            if (!res.ok) {
                const t = await res.text();
                alert(t || "Erreur");
                return;
            }

            closeModal();
            loadDTs();
        });
    }

    function init() {
        document.getElementById("btn-add-dt").addEventListener("click", () => openModal("add"));
        document.getElementById("dt-modal-close").addEventListener("click", closeModal);
        document.getElementById("dt-modal-cancel").addEventListener("click", closeModal);
        modal.addEventListener("click", e => { if (e.target === modal) closeModal(); });

        initForm();
        loadDTs();
    }

    return { init, loadDTs };
})();
