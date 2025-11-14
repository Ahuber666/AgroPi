import Core
import Foundation

final class SlateViewModel: ObservableObject {
    @Published var events: [EventViewModel] = []
    private let newsService: LiveNewsService

    init(newsService: LiveNewsService = LiveNewsService()) {
        self.newsService = newsService
        fetch()
    }

    func fetch() {
        newsService.fetchTopStories(limit: 12) { [weak self] result in
            DispatchQueue.main.async {
                switch result {
                case .success(let events):
                    self?.events = events.map(EventViewModel.init)
                case .failure:
                    self?.events = []
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

    init(event: Event) {
        id = event.id
        title = event.title
        summary = event.summary
        updatedAt = event.updatedAt
        serverScore = event.serverScore
    }
}
