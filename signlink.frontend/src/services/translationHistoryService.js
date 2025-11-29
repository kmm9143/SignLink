// translationHistoryService.js

//const BASE_URL = "/api/translations";
const BASE_URL = "/api/translations";

class TranslationHistoryService {
    async getHistory(userId) {
        try {
            const res = await fetch(`${BASE_URL}/${userId}`, {
                credentials: "include",
            });

            if (!res.ok) throw new Error(`Failed to fetch history (${res.status})`);
            return await res.json();
        } catch (err) {
            console.error("History fetch error:", err);
            return [];
        }
    }

    async deleteLogs(userId, logIds) {
        try {
            const res = await fetch(`${BASE_URL}/${userId}/logs`, {
                method: "DELETE",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify({ log_ids: logIds }),
            });

            if (!res.ok) {
                const detail = await res.json().catch(() => null);
                throw new Error(detail?.detail || "Failed to delete logs");
            }

            return await res.json();
        } catch (err) {
            console.error("Delete logs error:", err);
            throw err;
        }
    }

    async deleteAll(userId) {
        try {
            const res = await fetch(`${BASE_URL}/${userId}/all`, {
                method: "DELETE",
                credentials: "include",
            });

            if (!res.ok) throw new Error("Failed to clear history");
            return await res.json();
        } catch (err) {
            console.error("Clear history error:", err);
            throw err;
        }
    }
}

const translationHistoryService = new TranslationHistoryService();
export default translationHistoryService;