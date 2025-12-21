export const API = {
    base: window.location.origin,
    async getArticles() {
        const res = await fetch(`${this.base}/articles`);
        return await res.json();
    },
    async createArticle(data) {
        const res = await fetch(`${this.base}/articles`, {
            method: "POST",
            headers: {"Content-Type":"application/json"},
            body: JSON.stringify(data)
        });
        return await res.json();
    }
};
