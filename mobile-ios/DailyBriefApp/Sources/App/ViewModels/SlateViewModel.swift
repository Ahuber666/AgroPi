import Combine
import Foundation

final class SlateViewModel: ObservableObject {
    @Published var events: [EventViewModel] = []
    private var cancellables = Set<AnyCancellable>()

    init() {
        fetch()
    }

    func fetch() {
        GraphQLClient.shared.fetch(locale: "en-US", topics: ["world"]) { [weak self] result in
            DispatchQueue.main.async {
                switch result {
                case .success(let events):
                    self?.events = events
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
}
