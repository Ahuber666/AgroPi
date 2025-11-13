package com.dailybrief.shared

import com.dailybrief.shared.db.DailyBriefDatabase
import com.squareup.sqldelight.drivers.native.NativeSqliteDriver

class DatabaseDriverFactory {
    fun create() = NativeSqliteDriver(DailyBriefDatabase.Schema, "dailybrief.db")
}
