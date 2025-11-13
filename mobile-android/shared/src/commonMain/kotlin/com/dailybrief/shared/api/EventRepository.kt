package com.dailybrief.shared.api

import com.dailybrief.shared.model.Event
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class EventRepository(
    private val client: GraphQLClient = GraphQLClient(),
    private val scope: CoroutineScope = CoroutineScope(Dispatchers.Default)
) {
    private val state = MutableStateFlow<List<Event>>(emptyList())

    fun observeSlates(locale: String, topics: List<String>, onUpdate: (List<Event>) -> Unit) {
        scope.launch {
            refresh(locale, topics)
            onUpdate(state.value)
        }
    }

    suspend fun refresh(locale: String, topics: List<String>) {
        val events = client.fetchSlates(locale, topics)
        state.value = events
    }

    fun stateFlow(): StateFlow<List<Event>> = state.asStateFlow()
}
