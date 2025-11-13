package com.dailybrief.shared

import android.content.Context
import com.squareup.sqldelight.android.AndroidSqliteDriver
import com.dailybrief.shared.db.DailyBriefDatabase

class DatabaseDriverFactory(private val context: Context) {
    fun create() = AndroidSqliteDriver(DailyBriefDatabase.Schema, context, "dailybrief.db")
}
