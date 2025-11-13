// swift-tools-version: 5.9
import PackageDescription
import AppleProductTypes

let package = Package(
    name: "DailyBriefApp",
    platforms: [
        .iOS("17.0")
    ],
    products: [
        .iOSApplication(
            name: "DailyBrief",
            targets: ["App"],
            bundleIdentifier: "ai.dailybrief.app",
            teamIdentifier: "ABCDE12345",
            displayVersion: "1.0",
            bundleVersion: "1",
            iconAssetName: "AppIcon",
            accentColorAssetName: "AccentColor"
        )
    ],
    targets: [
        .executableTarget(
            name: "App",
            path: "Sources/App"
        )
    ]
)
