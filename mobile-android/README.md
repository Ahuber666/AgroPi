# DailyBrief Android + Shared Module

This project hosts the Jetpack Compose Android client and the Kotlin Multiplatform `:shared` module consumed by both Android and iOS (via XCFramework export).  The shared module bundles data models, a GraphQL client, SQLDelight offline cache, and on-device reranking utilities.

## Modules

- `androidApp/` – Compose UI, WorkManager background refresh, push-ready architecture.
- `shared/` – Kotlin Multiplatform sources plus SQLDelight schema.  Expose `GraphQLClient` and `Reranker` utilities to native targets.

## Quick start

```bash
cd mobile-android
./gradlew :androidApp:assembleDebug
./gradlew :shared:packForXCode # produces XCFramework for SwiftUI app
```

## Notifications & background sync

`SlateRefreshWorker` triggers every 15 minutes using WorkManager.  Hook FCM in `MainActivity` to display push alerts.
