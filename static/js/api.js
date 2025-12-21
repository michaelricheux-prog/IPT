/* static/js/api.js */
export const API = {
    base: window.location.origin,

    async fetchBlocs(params) {
        const query = new URLSearchParams(params).toString();
        const res = await fetch(`${this.base}/blocs/?${query}`);
        if (!res.ok) throw new Error("Erreur lors de la récupération des blocs");
        return await res.json();
    },

    async runPlanning(mode, data) {
        const res = await fetch(`${this.base}/planning/run?mode=${mode}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });
        return await res.json();
    },

    async exportExcel() {
        window.location.href = `${this.base}/excel/export`;
    }
};