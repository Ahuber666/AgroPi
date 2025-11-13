package com.dailybrief.android

import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import com.dailybrief.shared.api.EventRepository

class SlateRefreshWorker(appContext: Context, params: WorkerParameters) : CoroutineWorker(appContext, params) {
    private val repository = EventRepository()

    override suspend fun doWork(): Result {
        return try {
            repository.refresh(locale = "en-US", topics = listOf("world"))
            Result.success()
        } catch (t: Throwable) {
            Result.retry()
        }
    }
}
