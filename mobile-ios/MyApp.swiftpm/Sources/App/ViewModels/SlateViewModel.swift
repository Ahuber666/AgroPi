import Combine
import Core
import Foundation

final class SlateViewModel: ObservableObject {
    @Published var events: [EventViewModel] = []
    private let client: GraphQLClient
    private var cancellables = Set<AnyCancellable>()

    init(client: GraphQLClient = GraphQLClient()) {
        self.client = client
        fetch()
    }

    func fetch() {
        client.fetchSlates(locale: "en-US", topics: ["world"]) { [weak self] result in
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
        self.id = event.id
        self.title = event.title
        self.summary = event.summary
        self.updatedAt = event.updatedAt
        self.serverScore = event.serverScore
    }
}
