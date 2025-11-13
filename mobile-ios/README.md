# DailyBrief iOS

SwiftUI + Combine client for DailyBrief.  Targets iOS 17 with Dynamic Type, VoiceOver, High Contrast, and reduced motion support baked into the components.

## Highlights
- Tabbed experience (Top Brief + Topics) backed by Combine.
- Actions: save/share/mute per event.
- Notifications scheduled via `UNUserNotificationCenter` for daily + breaking alerts.
- Integrates with the Kotlin Multiplatform `shared` module through the generated `Shared` framework (see `mobile-android/shared`).

## Running
```
xcodebuild -scheme DailyBrief -destination 'platform=iOS Simulator,name=iPhone 15'
```

To import the shared Kotlin framework:
1. `cd mobile-android && ./gradlew :shared:packForXCode`.
2. Drag the produced `Shared.xcframework` into the Xcode project and update `Package.swift` dependency path if needed.
