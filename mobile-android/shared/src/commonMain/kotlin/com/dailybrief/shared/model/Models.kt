package com.dailybrief.shared.model

data class Source(
    val id: String,
    val name: String,
    val locale: String,
    val logoUrl: String
)

data class Event(
    val id: String,
    val title: String,
    val topic: String,
    val summary: String,
    val serverScore: Float,
    val topicVec: FloatArray,
    val sources: List<Source>
)
