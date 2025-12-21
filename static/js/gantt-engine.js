/* static/js/gantt-engine.js */

let ganttInstance = null;

export function initGantt(containerId, items, viewMode = "Week", onTaskClick) {
    const container = document.querySelector(containerId);
    if (!container) return null;

    // 1️⃣ Nettoyer l'ancien Gantt
    if (container) {
        container.innerHTML = "";
    }

    // Préparer les tâches
    const tasks = items
        .map(b => {
            if (!b.date_debut_planifiee || !b.date_fin_planifiee) return null;
            return {
                id: String(b.id),
                name: b.nom || `Op ${b.id}`,
                start: b.date_debut_planifiee.split("T")[0],
                end: b.date_fin_planifiee.split("T")[0],
                progress: b.quantite_a_produire > 0
                    ? Math.min(100, Math.round((b.quantite_produite / b.quantite_a_produire) * 100))
                    : 0,
                custom_class: b.est_realisee ? "gantt-done" : "gantt-pending",
                dependencies: b.bloc_precedent_id ? String(b.bloc_precedent_id) : ""
            };
        })
        .filter(Boolean);

    if (!tasks.length) {
        container.innerHTML = `<div style="padding:2rem;text-align:center;color:#888;">
            Aucune opération planifiée à afficher.
        </div>`;
        return null;
    }

    // Créer l'instance Gantt
    ganttInstance = new Gantt(containerId, tasks, {
        header_height: 50,
        column_width: 30,
        step: 24,
        view_modes: ["Day", "Week", "Month"],
        bar_height: 25,
        bar_corner_radius: 3,
        arrow_curve: 5,
        padding: 18,
        view_mode: viewMode,
        language: "fr",
        on_click: task => {
            if (typeof onTaskClick === "function") onTaskClick(task.id);
        },
        on_date_change: (task, start, end) => {
            console.log("Changement de dates :", task.id, start, end);
            // Ici tu pourrais appeler API.updateDates(task.id, start, end)
        },
        custom_popup_html: task => {
            const endDate = task._end.toLocaleDateString();
            return `
                <div style="padding:10px;background:#333;color:#fff;border-radius:5px;">
                    <strong>${task.name}</strong><br>
                    Fin prévue : ${endDate}<br>
                    Avancement : ${task.progress}%
                </div>`;
        }
    });

    return ganttInstance;
}
