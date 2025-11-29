// useTranslationHistory.js
import { useEffect, useState, useCallback } from "react";
import translationHistoryService from "../services/translationHistoryService";

export default function useTranslationHistory(userId) {
    const [history, setHistory] = useState([]);
    const [filteredHistory, setFilteredHistory] = useState([]);
    const [loading, setLoading] = useState(true);

    const [filter, setFilter] = useState(
        () => localStorage.getItem("historyFilter") || "All"
    );

    const [sortOrder, setSortOrder] = useState(
        () => localStorage.getItem("historySortOrder") || "Newest"
    );

    const [editMode, setEditMode] = useState(false);
    const [selectedIds, setSelectedIds] = useState([]);

    // Fetch history
    useEffect(() => {
        const fetchData = async () => {
            if (userId == null) return;
            setLoading(true);

            const data = await translationHistoryService.getHistory(userId);

            setHistory(data || []);
            setLoading(false);
        };

        fetchData();
    }, [userId]);

    // Apply filter & sort
    useEffect(() => {
        localStorage.setItem("historyFilter", filter);
        localStorage.setItem("historySortOrder", sortOrder);

        let result =
            filter === "All"
                ? [...history]
                : history.filter(
                    (item) =>
                        (item.INPUT_TYPE ?? item.input_type)?.toLowerCase() ===
                        filter.toLowerCase()
                );

        result.sort((a, b) =>
            sortOrder === "Newest"
                ? new Date(b.CREATED_AT) - new Date(a.CREATED_AT)
                : new Date(a.CREATED_AT) - new Date(b.CREATED_AT)
        );

        setFilteredHistory(result);
    }, [filter, sortOrder, history]);

    // Selection helpers
    const toggleSelect = useCallback((id) => {
        setSelectedIds((prev) =>
            prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
        );
    }, []);

    const selectAll = useCallback(() => {
        setSelectedIds((prev) =>
            prev.length === filteredHistory.length
                ? []
                : filteredHistory.map((i) => i.ID)
        );
    }, [filteredHistory]);

    // Delete selected
    const deleteSelected = useCallback(async () => {
        if (!selectedIds.length) return;

        await translationHistoryService.deleteLogs(userId, selectedIds);

        setHistory((prev) => prev.filter((i) => !selectedIds.includes(i.ID)));
        setSelectedIds([]);
        setEditMode(false);
    }, [selectedIds, userId]);

    return {
        loading,
        history: filteredHistory,
        filter,
        setFilter,
        sortOrder,
        setSortOrder,
        editMode,
        setEditMode,
        selectedIds,
        toggleSelect,
        selectAll,
        deleteSelected,
    };
}