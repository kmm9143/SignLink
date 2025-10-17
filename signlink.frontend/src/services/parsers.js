/**
 * Parsers for translator endpoints.
 * Keep parsing logic isolated to follow OCP (add new parsers without editing components).
 */

export function parseImagePredictions(data) {
    const allPredictions = [];
    if (Array.isArray(data)) {
        data.forEach((item) => {
            item.predictions?.predictions?.forEach((pred) => allPredictions.push(pred));
        });
    } else if (data?.predictions?.predictions) {
        allPredictions.push(...data.predictions.predictions);
    }

    let highestPred = null;
    allPredictions.forEach((pred) => {
        if (!highestPred || pred.confidence > highestPred.confidence) highestPred = pred;
    });
    return highestPred;
}

export function parseVideoPredictions(data) {
    const allPreds = (data.predictions || []).flatMap((frameData) => {
        const predictionArray = frameData.prediction || [];
        return predictionArray.flatMap((inner) => {
            const preds = inner.predictions?.predictions || [];
            return preds.map((p) => ({
                frame: frameData.frame,
                label: p.class || p.label || p.sign || "Unknown",
                confidence: parseFloat(p.confidence ?? p.conf ?? p.probability ?? 0),
            }));
        });
    });

    const topPredsPerFrame = Object.values(
        allPreds.reduce((acc, p) => {
            if (!acc[p.frame] || p.confidence > acc[p.frame].confidence) {
                acc[p.frame] = p;
            }
            return acc;
        }, {})
    );

    return topPredsPerFrame;
}