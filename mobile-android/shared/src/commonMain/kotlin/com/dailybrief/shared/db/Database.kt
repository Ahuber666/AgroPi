package com.dailybrief.shared.db

import com.dailybrief.shared.model.Event
import com.squareup.sqldelight.db.SqlDriver
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class EventStore(private val driver: SqlDriver) {
    private val database = DailyBriefDatabase(driver)

    suspend fun upsert(events: List<Event>) = withContext(Dispatchers.Default) {
        database.transaction {
            events.forEach { event ->
                database.dailyBriefQueries.insertItem(
                    id = event.id,
                    title = event.title,
                    topic = event.topic,
                    summary = event.summary,
                    score = event.serverScore.toDouble()
                )
            }
        }
    }

    suspend fun list(): List<Event> = withContext(Dispatchers.Default) {
        database.dailyBriefQueries.selectAll().executeAsList().map {
            Event(
                id = it.id,
                title = it.title,
                topic = it.topic,
                summary = it.summary,
                serverScore = it.score.toFloat(),
                topicVec = floatArrayOf(),
                sources = emptyList()
            )
        }
    }
}
