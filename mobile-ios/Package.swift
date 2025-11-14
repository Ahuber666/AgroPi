// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "Core",
    platforms: [
        .iOS("16.0"),
        .macOS("13.0")
    ],
    products: [
        .library(name: "Core", targets: ["Core"])
    ],
    targets: [
        .target(
            name: "Core",
            path: "Sources/Core"
        ),
        .testTarget(
            name: "CoreTests",
            dependencies: ["Core"],
            path: "Tests/CoreTests"
        )
    ]
)
