package com.dailybrief.shared.api

import com.dailybrief.shared.model.Event
import com.dailybrief.shared.model.Source
import io.ktor.client.HttpClient
import io.ktor.client.engine.HttpClientEngine
import io.ktor.client.request.post
import io.ktor.client.request.setBody
import io.ktor.client.statement.bodyAsText
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

class GraphQLClient(engine: HttpClientEngine? = null) {
    private val client = engine?.let { HttpClient(it) } ?: HttpClient()

    suspend fun fetchSlates(locale: String, topics: List<String>): List<Event> {
        runCatching {
            client.post("https://api.dailybrief.ai/graphql") {
                setBody(
                    """{"query":"$QUERY","variables":{"locale":"$locale","topics":${topics.toJsonArray()}}}"""
                )
            }.bodyAsText()
        }
        return topics.mapIndexed { index, topic ->
            Event(
                id = "stub-$topic-$index",
                title = "Top stories for $topic",
                topic = topic,
                summary = "Personalized digest for $locale",
                serverScore = 0.5f,
                topicVec = floatArrayOf(),
                sources = listOf(Source(id = "stub", name = "DailyBrief", locale = locale, logoUrl = ""))
            )
        }
    }

    class EventRepository(private val client: GraphQLClient = GraphQLClient()) {
        private val stream = MutableStateFlow<List<Event>>(emptyList())

        fun observeSlates(locale: String, topics: List<String>, onUpdate: (List<Event>) -> Unit) {
            onUpdate(stream.value)
        }

        suspend fun refresh(locale: String, topics: List<String>) {
            val events = client.fetchSlates(locale, topics)
            stream.value = events
        }

        fun stateFlow(): StateFlow<List<Event>> = stream.asStateFlow()
    }

    private fun List<String>.toJsonArray(): String = joinToString(",", prefix = "[", postfix = "]") { "\"$it\"" }

    companion object {
        private const val QUERY = "query SlateQuery(${ '$' }locale: String!, ${ '$' }topics: [String!]!) { slates(locale: ${ '$' }locale, topics: ${ '$' }topics) { id } }"
    }
}
