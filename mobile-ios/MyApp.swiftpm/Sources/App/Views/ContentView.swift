import SwiftUI

struct ContentView: View {
    @EnvironmentObject private var viewModel: SlateViewModel

    var body: some View {
        TabView {
            TopBriefView(
                events: viewModel.events,
                isLoading: viewModel.isLoading,
                errorMessage: viewModel.lastError,
                refresh: viewModel.fetch
            )
            .tabItem { Label("Top", systemImage: "newspaper") }

            TopicListView(
                events: viewModel.events,
                isLoading: viewModel.isLoading,
                errorMessage: viewModel.lastError,
                refresh: viewModel.fetch
            )
            .tabItem { Label("Topics", systemImage: "list.bullet") }
        }
        .task {
            await NotificationScheduler().scheduleDailyBrief()
        }
    }
}
