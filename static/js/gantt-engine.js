/* static/js/gantt-engine.js */

/**
 * Initialise ou met à jour le diagramme de Gantt
 * @param {string} containerId - Sélecteur CSS (ex: "#gantt")
 * @param {Array} items - Liste des blocs/opérations issus de l'API
 * @param {string} viewMode - Mode d'affichage ('Day', 'Week', 'Month')
 */
export function initGantt(containerId, items, viewMode = "Week") {
    // 1. Transformation des données pour Frappe Gantt
    const tasks = items.map(b => {
        // Sécurité : Si les dates ne sont pas définies, on n'affiche pas sur le Gantt
        if (!b.date_debut_planifiee || !b.date_fin_planifiee) return null;

        return {
            id: String(b.id),
            name: b.nom || `Op ${b.id}`,
            // Frappe Gantt accepte le format YYYY-MM-DD ou ISO
            start: b.date_debut_planifiee.split('T')[0],
            end: b.date_fin_planifiee.split('T')[0],
            // Calcul du pourcentage d'avancement
            progress: b.quantite_a_produire > 0 
                ? Math.min(100, Math.round((b.quantite_produite / b.quantite_a_produire) * 100)) 
                : 0,
            // Classe CSS personnalisée selon le statut
            custom_class: b.est_realisee ? "gantt-done" : "gantt-pending",
            // Optionnel : ajout de métadonnées pour usage ultérieur
            dependencies: b.bloc_precedent_id ? String(b.bloc_precedent_id) : ""
        };
    }).filter(Boolean); // Supprime les entrées nulles

    // 2. Gestion de l'affichage si aucune tâche n'est planifiée
    const container = document.querySelector(containerId);
    if (tasks.length === 0) {
        if (container) {
            container.innerHTML = `
                <div style="padding: 2rem; text-align: center; color: #888;">
                    Aucune opération planifiée à afficher. 
                    <br><small>Vérifiez que les opérations ont des dates de début et de fin.</small>
                </div>`;
        }
        return null;
    }

    // 3. Création de l'instance Gantt
    // Note: Frappe Gantt gère lui-même le nettoyage de l'ancien SVG si on réutilise le sélecteur
    return new Gantt(containerId, tasks, {
        header_height: 50,
        column_width: 30,
        step: 24,
        view_modes: ['Day', 'Week', 'Month'],
        bar_height: 25,
        bar_corner_radius: 3,
        arrow_curve: 5,
        padding: 18,
        view_mode: viewMode,
        language: "fr",
        
        // --- INTERACTION ---
        on_click: task => {
            // Appelle la fonction exposée globalement dans app.js
            if (typeof window.openEditModal === "function") {
                window.openEditModal(task.id);
            } else {
                console.warn("La fonction window.openEditModal n'est pas encore chargée.");
            }
        },
        
        // Optionnel : Gestion du changement de date par glisser-déposer
        on_date_change: (task, start, end) => {
            console.log(`Nouvelles dates pour ${task.id}:`, start, end);
            // On pourrait appeler une fonction API.updateDates ici
        },

        // Permet de personnaliser le contenu du popup au survol
        custom_popup_html: function(task) {
            const end_date = task._end.toLocaleDateString();
            return `
                <div class="details-container" style="padding:10px; background:#333; color:#fff; border-radius:5px;">
                    <h5>${task.name}</h5>
                    <p>Fin prévue: ${end_date}</p>
                    <p>${task.progress}% complété</p>
                </div>
            `;
        }
    });
}