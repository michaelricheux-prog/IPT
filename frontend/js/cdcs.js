// frontend/js/cdc.js
export const cdcModule = (() => {
    const modal = document.getElementById("cdc-modal");
    const form = document.getElementById("cdc-form");

    function openModal(mode, id = null) {
        modal.classList.add("active");
        document.getElementById("cdc-modal-title").textContent =
            mode === "edit" ? "Éditer cdc" : "Ajouter cdc";

        if (mode === "edit" && id) {
            fetch(`${window.location.origin}/cdcs/${id}`)
                .then(res => res.json())
                .then(cdc => {
                    document.getElementById("cdcCode").value = cdc.cdcCode;
                    document.getElementById("cdcName").value = cdc.cdcName;
                    document.getElementById("cdcCapa").value = cdc.Capa;
                });
        } else {
            form.reset();
        }

        form.dataset.mode = mode;
        form.dataset.cdcId = id || "";
    }

    function closeModal() {
        modal.classList.remove("active");
        form.dataset.mode = "";
        form.dataset.cdcId = "";
    }

    function bindRowActions() {
        document.querySelectorAll(".btn-edit-cdc").forEach(btn => {
            btn.addEventListener("click", () => openModal("edit", btn.dataset.id));
        });
        document.querySelectorAll(".btn-delete-cdc").forEach(btn => {
            btn.addEventListener("click", async () => {
                if (!confirm("Confirmer la suppression ?")) return;
                await fetch(`${window.location.origin}/cdcs/${btn.dataset.id}`, { method: "DELETE" });
                loadcdcs();
            });
        });
    }

    async function loadcdcs() {
        const res = await fetch(`${window.location.origin}/cdcs/`);
        const cdcs = await res.json();
        const tbody = document.getElementById("tbody-cdcs");

        tbody.innerHTML = cdcs.length === 0
            ? `<tr><td colspan="4">Aucun cdc</td></tr>`
            : cdcs.map(cdc => `
                <tr>
                    <td>${cdc.cdcCode}</td>
                    <td>${cdc.cdcName}</td>
                    <td>${cdc.Capa}</td>
                    <td>
                        <button class="btn-edit-cdc" data-id="${cdc.id}">✏️</button>
                        <button class="btn-delete-cdc" data-id="${cdc.id}">🗑️</button>
                    </td>
                </tr>
            `).join("");

        bindRowActions();
    }

    function initForm() {
        form.addEventListener("submit", async e => {
            e.preventDefault();
            const mode = form.dataset.mode;
            const cdcId = form.dataset.cdcId;
            const cdcCode = document.getElementById("cdcCode").value.trim();
            const cdcName = document.getElementById("cdcName").value.trim();
            const Capa = parseFloat(document.getElementById("cdcCapa").value);

            let res;
            if (mode === "edit") {
                res = await fetch(`${window.location.origin}/cdcs/${cdcId}`, {
                    method: "PATCH",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ cdcCode, cdcName, Capa })
                });
            } else {
                res = await fetch(`${window.location.origin}/cdcs/`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ cdcCode, cdcName, Capa })
                });
            }

            if (!res.ok) {
                const t = await res.text();
                alert(t || "Erreur");
                return;
            }

            closeModal();
            loadcdcs();
        });
    }

    function init() {
        document.getElementById("btn-add-cdc").addEventListener("click", () => openModal("add"));
        document.getElementById("cdc-modal-close").addEventListener("click", closeModal);
        document.getElementById("cdc-modal-cancel").addEventListener("click", closeModal);
        modal.addEventListener("click", e => { if (e.target === modal) closeModal(); });

        initForm();
        loadcdcs();
    }

    return { init, loadcdcs };
})();
