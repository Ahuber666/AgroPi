import org.gradle.api.JavaVersion
import org.gradle.api.tasks.Sync
import java.io.File
import org.jetbrains.kotlin.gradle.plugin.mpp.KotlinNativeTarget
plugins {
    id("com.android.library")
    id("org.jetbrains.kotlin.multiplatform")
    id("com.squareup.sqldelight")
}

kotlin {
    androidTarget {
        compilations.all {
            kotlinOptions.jvmTarget = "17"
        }
    }
    val iosTargets = listOf(iosX64(), iosArm64(), iosSimulatorArm64())
    iosTargets.forEach { target ->
        target.binaries.framework {
            baseName = "shared"
        }
    }

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
        val iosX64Main by getting {
            dependencies {
                implementation("io.ktor:ktor-client-darwin:2.3.9")
                implementation("com.squareup.sqldelight:native-driver:1.5.5")
            }
        }
        val iosArm64Main by getting {
            dependencies {
                implementation("io.ktor:ktor-client-darwin:2.3.9")
                implementation("com.squareup.sqldelight:native-driver:1.5.5")
            }
        }
        val iosSimulatorArm64Main by getting {
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

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

}

sqldelight {
    database("DailyBriefDatabase") {
        packageName = "com.dailybrief.shared.db"
        schemaOutputDirectory = file("src/commonMain/sqldelight")
    }
}

val packForXCode by tasks.registering(Sync::class) {
    val mode = (project.findProperty("CONFIGURATION") as? String) ?: "Debug"
    val sdkName = (project.findProperty("SDK_NAME") as? String) ?: "iphonesimulator"
    val target = when {
        sdkName.startsWith("iphoneos") -> "iosArm64"
        sdkName.startsWith("iphonesimulator") -> "iosSimulatorArm64"
        else -> "iosX64"
    }
    val framework = kotlin.targets.getByName<KotlinNativeTarget>(target).binaries.getFramework(mode)
    dependsOn(framework.linkTask)
    from({ framework.outputDirectory })
    into(File(buildDir, "xcode-frameworks"))
}
