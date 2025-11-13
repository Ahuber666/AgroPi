package com.dailybrief.shared.api

import com.dailybrief.shared.model.Event
import com.dailybrief.shared.model.Source
import io.ktor.client.HttpClient
import io.ktor.client.call.body
import io.ktor.client.engine.HttpClientEngine
import io.ktor.client.plugins.contentnegotiation.ContentNegotiation
import io.ktor.client.request.post
import io.ktor.client.request.setBody
import io.ktor.serialization.kotlinx.json.json
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json

class GraphQLClient(engine: HttpClientEngine? = null) {
    private val json = Json { ignoreUnknownKeys = true }
    private val client = if (engine == null) {
        HttpClient {
            install(ContentNegotiation) { json(json) }
        }
    } else {
        HttpClient(engine) {
            install(ContentNegotiation) { json(json) }
        }
    }

    suspend fun fetchSlates(locale: String, topics: List<String>): List<Event> {
        val response: GraphQLResponse = client.post("https://api.dailybrief.ai/graphql") {
            setBody(GraphQLRequest(query = QUERY, variables = mapOf("locale" to locale, "topics" to topics)))
        }.body()
        return response.data?.slates?.flatMap { slate ->
            slate.events.map { event ->
                Event(
                    id = event.id,
                    title = event.title,
                    topic = event.topic,
                    summary = event.summary ?: "",
                    serverScore = event.serverScore.toFloat(),
                    topicVec = event.topicVec.map { it.toFloat() }.toFloatArray(),
                    sources = event.sources.map { Source(it.id, it.name, it.locale, it.logoUrl) }
                )
            }
        } ?: emptyList()
    }

    companion object {
        private const val QUERY = """
            query SlateQuery($locale: String!, $topics: [String!]!) {
              slates(locale: $locale, topics: $topics) {
                events {
                  id
                  title
                  topic
                  summary
                  serverScore
                  topicVec
                  sources { id name locale logoUrl }
                }
              }
            }
        """
    }
}

@Serializable
private data class GraphQLRequest(val query: String, val variables: Map<String, Any?>)

@Serializable
private data class GraphQLResponse(val data: GraphQLData? = null)

@Serializable
private data class GraphQLData(val slates: List<Slate> = emptyList())

@Serializable
private data class Slate(val events: List<EventPayload>)

@Serializable
private data class EventPayload(
    val id: String,
    val title: String,
    val topic: String,
    val summary: String? = null,
    val serverScore: Double,
    val topicVec: List<Double>,
    val sources: List<SourcePayload>
)

@Serializable
private data class SourcePayload(
    val id: String,
    val name: String,
    val locale: String,
    val logoUrl: String,
)
