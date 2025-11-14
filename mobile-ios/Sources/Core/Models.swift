import Foundation

public struct Event: Identifiable, Equatable, Codable {
    public let id: String
    public let title: String
    public let summary: String
    public let serverScore: Double
    public let updatedAt: Date

    public init(id: String, title: String, summary: String, serverScore: Double, updatedAt: Date) {
        self.id = id
        self.title = title
        self.summary = summary
        self.serverScore = serverScore
        self.updatedAt = updatedAt
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
