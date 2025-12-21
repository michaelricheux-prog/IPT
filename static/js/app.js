/* static/js/app.js */
import { API } from './api.js';
import { initGantt } from './gantt-engine.js';

const $ = (id) => document.getElementById(id);

// --- FONCTION PRINCIPALE ---
async function refreshAll() {
    try {
        const params = { 
            q: $("q")?.value || "", 
            size: 100 
        };
        const items = await API.fetchBlocs(params);
        
        // Rendu du Tableau
        renderTable(items);
        
        // Rendu du Gantt
        const viewMode = $("gantt-view-mode")?.value || "Week";
        initGantt("#gantt", items, viewMode);
        
        console.log("Données rafraîchies avec succès.");
    } catch (e) {
        console.error("Erreur de rafraîchissement:", e);
    }
}

// --- RENDU DU TABLEAU ---
function renderTable(items) {
    const tbody = $("tbody-blocs");
    if (!tbody) return;
    
    if (items.length === 0) {
        tbody.innerHTML = `<tr><td colspan="12">Aucune donnée trouvée.</td></tr>`;
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
                <button class="small" onclick="window.openEditModal(${b.id})">Éditer</button>
            </td>
        </tr>
    `).join("");
}

// --- LOGIQUE DE PLANIFICATION ---
async function runPlanning() {
    const mode = $("plan-mode").value;
    const status = $("status-planning");
    const data = {};

    if (mode === "asap") {
        data.start_date = $("start_date").value;
    } else {
        data.due_date = $("due_date").value;
    }

    try {
        if (status) status.textContent = "Calcul en cours...";
        await API.runPlanning(mode, data);
        if (status) status.textContent = "Calcul terminé !";
        await refreshAll();
    } catch (e) {
        if (status) status.textContent = "Erreur lors du calcul.";
    }
}

// --- GESTION DE LA MODALE D'ÉDITION ---
window.openEditModal = async (id) => {
    try {
        console.log("Ouverture de l'opération :", id);
        const res = await fetch(`/blocs/${id}`);
        if (!res.ok) throw new Error("Erreur lors de la récupération");
        const data = await res.json();

        // Remplir le formulaire
        if ($('modal-op-id')) $('modal-op-id').textContent = data.id;
        if ($('edit-nom')) $('edit-nom').value = data.nom || "";
        if ($('edit-qte-prev')) $('edit-qte-prev').value = data.quantite_a_produire || 0;
        if ($('edit-qte-prod')) $('edit-qte-prod').value = data.quantite_produite || 0;
        if ($('edit-machine')) $('edit-machine').value = data.centre_charge_id || "";

        // Afficher la modale
        $('edit-modal')?.classList.remove('hidden');
    } catch (e) {
        console.error("Erreur lors de l'ouverture", e);
    }
};

window.closeModal = () => {
    $('edit-modal')?.classList.add('hidden');
};

// --- INITIALISATION AU CHARGEMENT ---
document.addEventListener("DOMContentLoaded", () => {
    // 1. Boutons standards
    $("btn-refresh")?.addEventListener("click", refreshAll);
    $("btn-load")?.addEventListener("click", refreshAll);
    $("btn-run")?.addEventListener("click", runPlanning);
    $("gantt-view-mode")?.addEventListener("change", refreshAll);

    // 2. Soumission du formulaire de modale
    $("edit-op-form")?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const id = $('modal-op-id').textContent;
        
        const updatedData = {
            nom: $('edit-nom').value,
            quantite_a_produire: parseInt($('edit-qte-prev').value),
            quantite_produite: parseInt($('edit-qte-prod').value),
            centre_charge_id: $('edit-machine').value
        };

        try {
            const res = await fetch(`/blocs/${id}`, {
                method: 'PATCH',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(updatedData)
            });
            if (!res.ok) throw new Error("Échec de la mise à jour");
            
            window.closeModal();
            await refreshAll(); 
        } catch (err) {
            console.error(err);
            alert("Erreur lors de la mise à jour.");
        }
    });

    // 3. Sidebar resizable
    const handle = $("drag-handle");
    const sidebar = $("resizable-sidebar");
    if (handle && sidebar) {
        let isResizing = false;
        handle.addEventListener("mousedown", () => isResizing = true);
        document.addEventListener("mousemove", (e) => {
            if (!isResizing) return;
            sidebar.style.width = `${e.clientX}px`;
        });
        document.addEventListener("mouseup", () => isResizing = false);
    }

    refreshAll();
});

// --- EXPOSITION GLOBALE ---
window.refreshAll = refreshAll;
window.runPlanning = runPlanning;
window.exportData = () => API.exportExcel();