/* static/js/app.js */
import { API } from './api.js';
import { initGantt } from './gantt-engine.js';

const $ = id => document.getElementById(id);

// --- RAFRAÎCHISSEMENT TABLEAU + GANTT ---
async function refreshAll() {
    try {
        const items = await API.fetchBlocs({ q: $("q")?.value || "", size: 100 });
        renderTable(items);
        const viewMode = $("gantt-view-mode")?.value || "Week";
        initGantt("#gantt", items, viewMode, openEditModal);
    } catch (e) {
        console.error("Erreur refreshAll:", e);
    }
}

// --- RENDU DU TABLEAU ---
function renderTable(items) {
    const tbody = $("tbody-blocs");
    if (!tbody) return;
    if (!items.length) {
        tbody.innerHTML = `<tr><td colspan="12">Aucune donnée</td></tr>`;
        return;
    }
    tbody.innerHTML = items.map(b => `
        <tr>
            <td>${b.id}</td>
            <td>${b.nom || ''}</td>
            <td>${b.ordre_fabrication_id || ''}</td>
            <td>${b.quantite_a_produire || 0}</td>
            <td>${b.quantite_produite || 0}</td>
            <td>${b.temps_prevu || 0}h</td>
            <td>${b.temps_passe || 0}h</td>
            <td>${b.duree_prevue_semaine || ''}</td>
            <td>${b.centre_charge_id || ''}</td>
            <td>${b.bloc_precedent_id || '-'}</td>
            <td>${b.est_realisee ? "✔️" : "⏳"}</td>
            <td>
                <button class="small" onclick="openEditModal(${b.id})">Éditer</button>
                <button class="small" onclick="deleteBloc(${b.id})">🗑️</button>
            </td>
        </tr>
    `).join("");
}

// --- MODALE ÉDITION / CRÉATION ---
async function openEditModal(id) {
    try {
        let data = { id: null, nom: "", quantite_a_produire: 0, quantite_produite: 0, centre_charge_id: "" };
        if (id) {
            const res = await fetch(`/blocs/${id}`);
            if (!res.ok) throw new Error("Impossible de charger l'opération");
            data = await res.json();
        }

        $("modal-op-id").textContent = data.id ?? "";
        $("edit-nom").value = data.nom || "";
        $("edit-qte-prev").value = data.quantite_a_produire ?? "";
        $("edit-qte-prod").value = data.quantite_produite ?? "";
        $("edit-machine").value = data.centre_charge_id ?? "";

        $("edit-modal").classList.remove("hidden");
    } catch (e) {
        console.error(e);
        alert("Impossible d'ouvrir la modale.");
    }
}

function closeModal() {
    $("edit-modal")?.classList.add("hidden");
}

// --- SOUMISSION FORMULAIRE MODALE ---
$("edit-op-form")?.addEventListener("submit", async e => {
    e.preventDefault();
    const id = $("modal-op-id").textContent || null;
    const payload = {
        nom: $("edit-nom").value.trim() || undefined,
        quantite_a_produire: $("edit-qte-prev").value ? parseFloat($("edit-qte-prev").value) : undefined,
        quantite_produite: $("edit-qte-prod").value ? parseFloat($("edit-qte-prod").value) : undefined,
        centre_charge_id: $("edit-machine").value ? parseInt($("edit-machine").value) : undefined
    };

    try {
        const method = id ? "PATCH" : "POST";
        const url = id ? `/blocs/${id}` : `/blocs/`;
        const res = await fetch(url, {
            method,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error("Erreur API");

        closeModal();
        refreshAll();
    } catch (err) {
        console.error(err);
        alert("Impossible d'enregistrer l'opération");
    }
});

// --- SUPPRESSION ---
async function deleteBloc(id) {
    if (!confirm("Supprimer cette opération ?")) return;
    try {
        const res = await fetch(`/blocs/${id}`, { method: "DELETE" });
        if (!res.ok) throw new Error("Erreur suppression");
        refreshAll();
    } catch (err) {
        console.error(err);
        alert("Impossible de supprimer l'opération");
    }
}

// --- LOGIQUE DE PLANIFICATION ---
async function runPlanning() {
    const mode = $("plan-mode")?.value;
    const data = {};
    if (mode === "asap") data.start_date = $("start_date")?.value;
    else data.due_date = $("due_date")?.value;

    try {
        $("status-planning").textContent = "Calcul en cours...";
        await API.runPlanning(mode, data);
        $("status-planning").textContent = "Calcul terminé !";
        refreshAll();
    } catch (e) {
        $("status-planning").textContent = "Erreur lors du calcul.";
        console.error(e);
    }
}

// --- INITIALISATION ---
document.addEventListener("DOMContentLoaded", () => {
    $("btn-refresh")?.addEventListener("click", refreshAll);
    $("btn-load")?.addEventListener("click", refreshAll);
    $("btn-run")?.addEventListener("click", runPlanning);
    $("gantt-view-mode")?.addEventListener("change", refreshAll);

    // Sidebar resizable
    const handle = $("drag-handle"), sidebar = $("resizable-sidebar");
    if (handle && sidebar) {
        let isResizing = false;
        handle.addEventListener("mousedown", () => isResizing = true);
        document.addEventListener("mousemove", e => { if (isResizing) sidebar.style.width = `${e.clientX}px`; });
        document.addEventListener("mouseup", () => isResizing = false);
    }

    refreshAll();
});

// --- EXPOSITION GLOBALE ---
window.refreshAll = refreshAll;
window.runPlanning = runPlanning;
window.openEditModal = openEditModal;
window.closeModal = closeModal;
window.deleteBloc = deleteBloc;
