import SwiftUI

struct ContentView: View {
    @EnvironmentObject private var viewModel: SlateViewModel

    var body: some View {
        TabView {
            TopBriefView(events: viewModel.events)
                .tabItem { Label("Top", systemImage: "newspaper") }
            TopicListView(events: viewModel.events)
                .tabItem { Label("Topics", systemImage: "list.bullet") }
        }
        .task {
            await NotificationScheduler().scheduleDailyBrief()
        }
    }
}
