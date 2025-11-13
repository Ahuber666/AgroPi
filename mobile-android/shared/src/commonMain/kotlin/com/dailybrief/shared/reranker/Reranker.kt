package com.dailybrief.shared.reranker

import com.dailybrief.shared.model.Event
import kotlin.math.sqrt

object Reranker {
    fun rerank(slate: List<Event>, userVec: FloatArray): List<Event> {
        return slate.sortedByDescending { event ->
            val serverScore = event.serverScore
            val userScore = if (event.topicVec.isNotEmpty() && userVec.isNotEmpty()) cosine(userVec, event.topicVec) else 0f
            0.7f * serverScore + 0.3f * userScore
        }
    }

    private fun cosine(a: FloatArray, b: FloatArray): Float {
        val size = minOf(a.size, b.size)
        if (size == 0) return 0f
        var dot = 0f
        var normA = 0f
        var normB = 0f
        for (i in 0 until size) {
            dot += a[i] * b[i]
            normA += a[i] * a[i]
            normB += b[i] * b[i]
        }
        if (normA == 0f || normB == 0f) return 0f
        return (dot / (sqrt(normA) * sqrt(normB))).coerceIn(-1f, 1f)
    }
}
