import Core
import Foundation

final class SlateViewModel: ObservableObject {
    @Published var events: [EventViewModel] = []
    @Published var isLoading = false
    @Published var lastError: String?

    private let newsService: LiveNewsService

    init(newsService: LiveNewsService = LiveNewsService()) {
        self.newsService = newsService
        fetch()
    }

    func fetch() {
        guard !isLoading else { return }
        isLoading = true
        lastError = nil

        newsService.fetchTopStories(limit: 20) { [weak self] result in
            guard let self = self else { return }
            self.isLoading = false
            switch result {
            case .success(let events):
                self.events = events.map(EventViewModel.init)
            case .failure(let error):
                self.lastError = error.localizedDescription
                if self.events.isEmpty {
                    self.events = EventViewModel.sample
                }
            }
        }
    }
}

struct EventViewModel: Identifiable {
    let id: String
    let title: String
    let summary: String
    let updatedAt: Date
    let serverScore: Double
    let source: String

    init(event: Event) {
        id = event.id
        title = event.title
        summary = event.summary
        updatedAt = event.updatedAt
        serverScore = event.serverScore
        source = event.source
    }

    fileprivate static let sample: [EventViewModel] = [
        EventViewModel(event: Event(
            id: "sample-1",
            title: "Stay tuned",
            summary: "Connect to the internet to fetch live headlines from Reddit, BBC, and NYTimes.",
            serverScore: 1.0,
            updatedAt: Date(),
            source: "DailyBrief"
        ))
    ]
}
