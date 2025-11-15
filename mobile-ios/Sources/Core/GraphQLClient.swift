import Foundation

public protocol NetworkSession {
    func makeDataTask(with request: URLRequest, completionHandler: @escaping (Data?, URLResponse?, Error?) -> Void) -> NetworkDataTask
}

public protocol NetworkDataTask {
    func resume()
}

extension URLSessionDataTask: NetworkDataTask {}

extension URLSession: NetworkSession {
    public func makeDataTask(with request: URLRequest, completionHandler: @escaping (Data?, URLResponse?, Error?) -> Void) -> NetworkDataTask {
        dataTask(with: request, completionHandler: completionHandler)
    }
}

public final class GraphQLClient {
    public enum ClientError: Error, Equatable {
        case encodingFailed
        case decodingFailed
    }

    private struct RequestPayload: Encodable {
        struct Variables: Encodable {
            let locale: String
            let topics: [String]
        }
        let query: String
        let variables: Variables
    }

    private let session: NetworkSession
    private let decoder: JSONDecoder
    private let dateProvider: () -> Date

    public init(
        session: NetworkSession = URLSession.shared,
        decoder: JSONDecoder = JSONDecoder(),
        dateProvider: @escaping () -> Date = Date.init
    ) {
        self.session = session
        self.decoder = decoder
        self.dateProvider = dateProvider
    }

    public func fetchSlates(
        locale: String,
        topics: [String],
        completion: @escaping (Result<[Event], Error>) -> Void
    ) {
        guard let request = makeRequest(locale: locale, topics: topics) else {
            completion(.failure(ClientError.encodingFailed))
            return
        }

        session.makeDataTask(with: request) { [weak self] data, _, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            guard let data = data,
                  let response = try? self?.decoder.decode(GraphQLResponse.self, from: data) else {
                completion(.failure(ClientError.decodingFailed))
                return
            }
            let now = self?.dateProvider() ?? Date()
           let events = response.data.slates.flatMap { slate in
               slate.events.map { payload in
                   Event(
                       id: payload.id,
                       title: payload.title,
                       summary: payload.summary ?? "",
                       serverScore: payload.serverScore,
                        updatedAt: now,
                        source: "GraphQL"
                    )
                }
            }
            completion(.success(events))
        }.resume()
    }

    private func makeRequest(locale: String, topics: [String]) -> URLRequest? {
        let payload = RequestPayload(
            query: Self.query,
            variables: .init(locale: locale, topics: topics)
        )
        guard let body = try? JSONEncoder().encode(payload) else {
            return nil
        }
        var request = URLRequest(url: Self.endpoint)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = body
        return request
    }

    private static let endpoint = URL(string: "https://api.dailybrief.ai/graphql")!
    private static let query = """
        query SlateQuery($locale: String!, $topics: [String!]!) {
          slates(locale: $locale, topics: $topics) {
            events { id title summary serverScore }
          }
        }
        """
}
