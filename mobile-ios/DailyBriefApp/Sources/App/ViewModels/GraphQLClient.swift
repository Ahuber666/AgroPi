import Foundation

final class GraphQLClient {
    static let shared = GraphQLClient()
    private init() {}

    func fetch(locale: String, topics: [String], completion: @escaping (Result<[EventViewModel], Error>) -> Void) {
        let query = """
        query SlateQuery($locale: String!, $topics: [String!]!) {
          slates(locale: $locale, topics: $topics) {
            events { id title summary serverScore }
          }
        }
        """
        let payload: [String: Any] = [
            "query": query,
            "variables": ["locale": locale, "topics": topics]
        ]

        guard let body = try? JSONSerialization.data(withJSONObject: payload) else {
            completion(.failure(NSError(domain: "serialization", code: -1)))
            return
        }

        var request = URLRequest(url: URL(string: "https://api.dailybrief.ai/graphql")!)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = body

        URLSession.shared.dataTask(with: request) { data, _, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            guard let data = data,
                  let response = try? JSONDecoder().decode(GraphQLResponse.self, from: data) else {
                completion(.failure(NSError(domain: "decode", code: -2)))
                return
            }
            let events = response.data.slates.flatMap { $0.events }.map { event in
                EventViewModel(
                    id: event.id,
                    title: event.title,
                    summary: event.summary ?? "",
                    updatedAt: Date(),
                    serverScore: event.serverScore
                )
            }
            completion(.success(events))
        }.resume()
    }
}

struct GraphQLResponse: Decodable {
    let data: SlateData
}

struct SlateData: Decodable {
    let slates: [Slate]
}

struct Slate: Decodable {
    let events: [EventPayload]
}

struct EventPayload: Decodable {
    let id: String
    let title: String
    let summary: String?
    let serverScore: Double
}
