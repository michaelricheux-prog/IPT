/* app.js — IPT front minimal (CRUD + liste + planning optionnel) */
/* Le front parle à l'API servie par FastAPI, même origine (window.location.origin). */

(() => {
    "use strict";

    // ---------- Helpers ----------
    const $ = (id) => document.getElementById(id);
    const setStatus = (el, msg, ok = true) => {
        if (!el) return;
        el.textContent = msg;
        el.className = "status mono " + (ok ? "ok" : "err");
    };
    const base = window.location.origin;

    // ---------- Détection des endpoints planning ----------
    async function detectPlanning() {
        const panel = $("planning-panel");
        if (!panel) return;
        try {
            const res = await fetch(`${base}/openapi.json`);
            if (!res.ok) {
                panel.classList.add("hidden");
                return;
            }
            const spec = await res.json();
            const paths = Object.keys(spec.paths || {});
            const show = paths.includes("/planning/run") && paths.includes("/planning");
            panel.classList.toggle("hidden", !show);
        } catch {
            panel.classList.add("hidden");
        }
    }

    // Toggle ASAP/RETRO
    function onModeChange(e) {
        if (!e.target || e.target.name !== "mode") return;
        const asap = e.target.value === "asap";
        $("asap-row")?.classList.toggle("hidden", !asap);
        $("retro-row")?.classList.toggle("hidden", asap);
    }
    document.addEventListener("change", onModeChange);

    // ---------- CRUD ----------
    async function createBloc() {
        const statusEl = $("status-create");
        const payload = {
            nom: $("c_nom")?.value?.trim(),
            quantite_a_produire: $("c_qap")?.value ? parseFloat($("c_qap").value) : undefined,
            temps_prevu: $("c_tp")?.value ? parseFloat($("c_tp").value) : undefined,
            duree_prevue_semaine: $("c_dps")?.value ? parseFloat($("c_dps").value) : undefined,
            centre_charge_id: $("c_cc")?.value ? parseInt($("c_cc").value) : undefined,
            ordre_fabrication_id: $("c_of")?.value ? parseInt($("c_of").value) : undefined,
            bloc_precedent_id: $("c_prev")?.value ? parseInt($("c_prev").value) : undefined,
        };
        if (!payload.nom) {
            setStatus(statusEl, "Le nom est requis.", false);
            return;
        }
        try {
            const res = await fetch(`${base}/blocs/`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            setStatus(statusEl, "Opération créée.");
            // 🚩 APPEL GLOBAL : Rafraîchit liste ET Gantt
            await refreshAll();
        } catch (e) {
            setStatus(statusEl, `Erreur: ${e.message}`, false);
        }
    }

    async function updateBloc() {
        const statusEl = $("status-update");
        const id = $("u_id")?.value ? parseInt($("u_id").value) : null;
        if (!id) {
            setStatus(statusEl, "ID requis.", false);
            return;
        }
        const payload = {};
        const push = (k, v) => {
            if (v !== "" && v !== null && v !== undefined) payload[k] = v;
        };

        push("nom", $("u_nom")?.value?.trim() || undefined);
        push("quantite_produite", $("u_qp")?.value ? parseFloat($("u_qp").value) : undefined);
        push("temps_passe", $("u_tpasse")?.value ? parseFloat($("u_tpasse").value) : undefined);
        push("quantite_a_produire", $("u_qap")?.value ? parseFloat($("u_qap").value) : undefined);
        push("duree_prevue_semaine", $("u_dps")?.value ? parseFloat($("u_dps").value) : undefined);
        push("centre_charge_id", $("u_cc")?.value ? parseInt($("u_cc").value) : undefined);
        push("ordre_fabrication_id", $("u_of")?.value ? parseInt($("u_of").value) : undefined);
        push("bloc_precedent_id", $("u_prev")?.value ? parseInt($("u_prev").value) : undefined);
        if ($("u_realisee")?.checked) push("est_realisee", true);

        try {
            const res = await fetch(`${base}/blocs/${id}`, {
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
            const ok = res.ok;
            const data = await res.json().catch(() => ({}));
            if (!ok) throw new Error(data?.detail || `HTTP ${res.status}`);
            setStatus(statusEl, "Opération mise à jour.");
            // 🚩 APPEL GLOBAL : Rafraîchit liste ET Gantt
            await refreshAll();
        } catch (e) {
            setStatus(statusEl, `Erreur: ${e.message}`, false);
        }
    }

    // ---------- Liste / filtres / tri / pagination ----------
    function buildParams() {
        const p = new URLSearchParams();
        const q = $("q")?.value?.trim();
        const est = $("est")?.value;
        const cc = $("f_cc")?.value;
        const of = $("f_of")?.value;
        if (q) p.append("q", q);
        if (est) p.append("est_realisee", est);
        if (cc) p.append("centre_charge_id", cc);
        if (of) p.append("ordre_fabrication_id", of);
        p.append("page", $("page")?.value || "1");
        p.append("size", $("size")?.value || "20");
        p.append("order_by", $("order_by")?.value || "id");
        p.append("order_dir", $("order_dir")?.value || "asc");
        return p;
    }

    async function loadBlocs() {
        const statusEl = $("status-list");
        try {
            const res = await fetch(`${base}/blocs/?${buildParams().toString()}`);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const items = await res.json();
            renderBlocs(items);
            setStatus(statusEl, `Chargé ${Array.isArray(items) ? items.length : 0} élément(s).`);
            return items; // 🚩 Important : retourne les items chargés
        } catch (e) {
            setStatus(statusEl, `Erreur: ${e.message}. L'API est-elle lancée ?`, false);
            renderBlocs([]);
            return [];
        }
    }

    function renderBlocs(items) {
        const tbody = $("tbody-blocs");
        if (!tbody) return;
        if (!Array.isArray(items) || items.length === 0) {
            tbody.innerHTML = `<tr><td colspan="12" class="mono">Aucune opération.</td></tr>`;
            return;
        }
        tbody.innerHTML = items
            .map(
                (b) => `
                <tr>
                    <td class="mono">${b.id}</td>
                    <td>${b.nom ?? ""}</td>
                    <td class="mono">${b.ordre_fabrication_id ?? ""}</td>
                    <td class="mono">${b.quantite_a_produire ?? ""}</td>
                    <td class="mono">${b.quantite_produite ?? ""}</td>
                    <td class="mono">${b.temps_prevu ?? ""}</td>
                    <td class="mono">${b.temps_passe ?? ""}</td>
                    <td class="mono">${b.duree_prevue_semaine ?? ""}</td>
                    <td class="mono">${b.centre_charge_id ?? ""}</td>
                    <td class="mono">${b.bloc_precedent_id ?? ""}</td>
                    <td>${b.est_realisee ? "✔️" : "⏳"}</td>
                    <td>
                        <button onclick="document.getElementById('u_id').value='${b.id}';document.getElementById('u_nom').value='${b.nom ?? ""}';">Éditer</button>
                    </td>
                </tr>`
            )
            .join("");
    }

    // ---------- Planification (optionnelle) ----------
    async function runPlanning() {
        const panelHidden = $("planning-panel")?.classList?.contains("hidden");
        if (panelHidden) return; // endpoints non présents -> ne rien faire

        const modeEl = document.querySelector('input[name="mode"]:checked');
        const mode = modeEl ? modeEl.value : "asap";
        const statusEl = $("status-planning");

        const body = {};
        if (mode === "asap") {
            const startRaw = $("start_date")?.value;
            if (startRaw) body.start_date = new Date(startRaw).toISOString();
        } else {
            const dueRaw = $("due_date")?.value;
            if (!dueRaw) {
                setStatus(statusEl, "Saisir une date d'échéance pour RETRO.", false);
                return;
            }
            body.due_date = new Date(dueRaw).toISOString();
        }

        try {
            const res = await fetch(`${base}/planning/run?mode=${mode}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(body),
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            setStatus(statusEl, `Planning ${mode.toUpperCase()} appliqué.`);
            // 🚩 APPEL GLOBAL : Rafraîchit liste ET Gantt après le calcul
            await refreshAll();
        } catch (e) {
            setStatus(statusEl, `Erreur planning: ${e.message}`, false);
        }
    }

    // ---------- Events ----------
    function bindEvents() {
        $("btn-create")?.addEventListener("click", createBloc);
        $("btn-update")?.addEventListener("click", updateBloc);
        $("btn-load")?.addEventListener("click", refreshAll); // 🚩 Appel direct à refreshAll

        document.addEventListener("click", (e) => {
            if (e.target && e.target.id === "btn-run") runPlanning();
            if (e.target && e.target.id === "btn-refresh") refreshAll(); // 🚩 Appel direct à refreshAll
        });
    }

    // ---------- Init ----------
    async function init() {
        await detectPlanning();
        bindEvents();
        // 🚩 Démarre l'application en rafraîchissant tout
        await refreshAll();
    }

    // démarrage de l'application
    document.addEventListener("DOMContentLoaded", init);

    // 🚩 Fonction de rafraîchissement global
    async function refreshAll() {
        // 1. Charge les blocs pour la liste
        const items = await loadBlocs(); 
        
        // 2. Transmet les blocs chargés au Gantt
        await loadGantt(items);
    }
})();


/* ----- Gantt ----- */
// 🚩 Cette partie n'est plus dans une IIFE, elle est dans le scope global
// pour pouvoir être appelée par le bloc principal (IIFE) via refreshAll().

function blocsToTasks(items) {
    // Transforme tes blocs en tâches Frappe Gantt
    const fmt = (d) => {
        if (!d) return null;
        const dt = new Date(d);
        if (isNaN(dt)) return null; // Vérifie si la date est valide
        
        // retourne ISO court (YYYY-MM-DD), nécessaire pour Frappe Gantt
        return `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, "0")}-${String(dt.getDate()).padStart(2, "0")}`;
    };

    return items
        .map((b) => {
            const start = fmt(b.date_debut_planifiee);
            const end = fmt(b.date_fin_planifiee);

            // Si pas de dates planifiées, on ignore
            if (!start || !end) return null;

            return {
                id: String(b.id),
                name: b.nom || `Bloc ${b.id}`,
                start,
                end,
                progress: Number(b.quantite_produite || 0) > 0 && Number(b.quantite_a_produire || 0) > 0
                    ? Math.min(100, Math.round(100 * (b.quantite_produite / b.quantite_a_produire)))
                    : 0,
                // Utilisation de la dépendance si bloc_precedent_id existe
                dependencies: b.bloc_precedent_id ? String(b.bloc_precedent_id) : undefined,
                custom_class: b.est_realisee ? "done" : "pending",
            };
        })
        .filter(Boolean); // Retire les éléments 'null'
}

let ganttInstance = null;

// 🚩 Modifié pour accepter les items directement, évitant un double appel API
async function loadGantt(apiItems) {
    const mount = document.querySelector("#gantt");
    if (!mount) return;
    mount.innerHTML = ""; // reset

    // Utilise les items passés ou tente un chargement si besoin (par sécurité)
    const items = Array.isArray(apiItems) ? apiItems : await loadBlocs();


    const tasks = blocsToTasks(items);
    
    // Le code ci-dessous vérifie si le format Frappe Gantt est bien respecté
    // console.log("Tasks formatées pour Gantt:", tasks);

    if (!tasks.length) {
        mount.innerHTML = `<div class="mono" style="padding:8px;color:#9ca3af">Aucune tâche planifiable (ajoutez des dates, ou calculez le planning ASAP/RETRO).</div>`;
        return;
    }
    
    // Si l'instance existe, la détruire avant de la recréer pour un rafraîchissement complet
    if (ganttInstance) {
        ganttInstance = null;
    }

    // Initialisation Frappe Gantt
    ganttInstance = new Gantt("#gantt", tasks, {
        view_mode: "Week",    // Day|Week|Month|Year
        date_format: "YYYY-MM-DD",
        readonly: true,
        today_button: true,
        language: "fr",
        lines: "both",
        container_height: 420
    });
}