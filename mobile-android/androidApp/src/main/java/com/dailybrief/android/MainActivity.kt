package com.dailybrief.android

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import com.dailybrief.shared.api.EventRepository
import com.dailybrief.shared.reranker.Reranker
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.util.concurrent.TimeUnit

class MainActivity : ComponentActivity() {
    private val state = MutableStateFlow(UiState())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        scheduleBackgroundFetch()
        val repository = EventRepository()
        repository.observeSlates(locale = "en-US", topics = listOf("world")) { events ->
            val reranked = Reranker.rerank(events, FloatArray(events.firstOrNull()?.topicVec?.size ?: 0))
            state.value = state.value.copy(events = reranked.map { it.title to it.summary.orEmpty() })
        }
        setContent {
            MaterialTheme {
                Surface(Modifier.fillMaxSize()) {
                    DailyBriefScreen(state = state.asStateFlow())
                }
            }
        }
    }

    private fun scheduleBackgroundFetch() {
        val request = PeriodicWorkRequestBuilder<SlateRefreshWorker>(15, TimeUnit.MINUTES).build()
        WorkManager.getInstance(this).enqueue(request)
    }
}

data class UiState(val events: List<Pair<String, String>> = emptyList())

@Composable
fun DailyBriefScreen(state: kotlinx.coroutines.flow.StateFlow<UiState>) {
    val uiState by state.collectAsState()
    Column(modifier = Modifier.padding(16.dp)) {
        uiState.events.forEach { (title, summary) ->
            Card(modifier = Modifier.padding(bottom = 12.dp)) {
                Column(Modifier.padding(16.dp)) {
                    Text(text = title, style = MaterialTheme.typography.titleMedium)
                    Text(text = summary, style = MaterialTheme.typography.bodyMedium)
                }
            }
        }
    }
}
