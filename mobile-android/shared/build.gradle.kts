plugins {
    id("com.android.library")
    id("org.jetbrains.kotlin.multiplatform")
    id("com.squareup.sqldelight")
}

kotlin {
    androidTarget()
    ios()

    sourceSets {
        val commonMain by getting {
            dependencies {
                implementation("io.ktor:ktor-client-core:2.3.9")
                implementation("io.ktor:ktor-client-json:2.3.9")
                implementation("io.ktor:ktor-client-logging:2.3.9")
                implementation("com.squareup.sqldelight:runtime:1.5.5")
                implementation("com.squareup.sqldelight:coroutines-extensions:1.5.5")
            }
        }
        val commonTest by getting
        val androidMain by getting {
            dependencies {
                implementation("io.ktor:ktor-client-okhttp:2.3.9")
                implementation("com.squareup.sqldelight:android-driver:1.5.5")
            }
        }
        val iosMain by getting {
            dependencies {
                implementation("io.ktor:ktor-client-darwin:2.3.9")
                implementation("com.squareup.sqldelight:native-driver:1.5.5")
            }
        }
    }
}

android {
    namespace = "com.dailybrief.shared"
    compileSdk = 34

    defaultConfig {
        minSdk = 26
    }
}

sqldelight {
    database("DailyBriefDatabase") {
        packageName = "com.dailybrief.shared.db"
        schemaOutputDirectory = file("src/commonMain/sqldelight")
    }
}
