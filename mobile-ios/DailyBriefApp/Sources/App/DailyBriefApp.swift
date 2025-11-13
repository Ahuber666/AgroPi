import SwiftUI
import UserNotifications
// import Shared

@main
struct DailyBriefApp: App {
    @StateObject private var viewModel = SlateViewModel()

    init() {
        NotificationScheduler().register()
    }

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(viewModel)
        }
    }
}
