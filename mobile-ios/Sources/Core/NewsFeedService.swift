import Foundation

public final class LiveNewsService {
    public struct Source {
        public enum Kind {
            case redditJSON(URL)
            case rss(URL)
        }

        public let name: String
        public let kind: Kind

        public init(name: String, kind: Kind) {
            self.name = name
            self.kind = kind
        }
    }

    private let sources: [Source]
    private let session: NetworkSession
    private let dateProvider: () -> Date
    private let queue = DispatchQueue(label: "live-news-service")

    public init(
        sources: [Source] = LiveNewsService.defaultSources,
        session: NetworkSession = URLSession.shared,
        dateProvider: @escaping () -> Date = Date.init
    ) {
        self.sources = sources
        self.session = session
        self.dateProvider = dateProvider
    }

    public func fetchTopStories(limit: Int = 12, completion: @escaping (Result<[Event], Error>) -> Void) {
        let group = DispatchGroup()
        var collected: [Event] = []
        var firstError: Error?

        for source in sources {
            group.enter()
            fetch(source: source) { result in
                switch result {
                case .success(let events):
                    self.queue.async {
                        collected.append(contentsOf: events)
                        group.leave()
                    }
                case .failure(let error):
                    self.queue.async {
                        if firstError == nil {
                            firstError = error
                        }
                        group.leave()
                    }
                }
            }
        }

        group.notify(queue: queue) {
            if collected.isEmpty, let error = firstError {
                DispatchQueue.main.async {
                    completion(.failure(error))
                }
                return
            }
            let deduped = Dictionary(grouping: collected, by: { $0.id }).compactMap { $0.value.first }
            let sorted = deduped.sorted(by: { $0.updatedAt > $1.updatedAt }).prefix(limit)
            DispatchQueue.main.async {
                completion(.success(Array(sorted)))
            }
        }
    }

    private func fetch(source: Source, completion: @escaping (Result<[Event], Error>) -> Void) {
        let request = URLRequest(url: source.url)
        session.makeDataTask(with: request) { data, _, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            guard let data = data else {
                completion(.success([]))
                return
            }
            let events: [Event]
            switch source.kind {
            case .redditJSON:
                events = self.parseReddit(data: data)
            case .rss:
                events = self.parseRSS(data: data)
            }
            completion(.success(events))
        }.resume()
    }

    private func parseReddit(data: Data) -> [Event] {
        guard let listing = try? JSONDecoder().decode(RedditListing.self, from: data) else { return [] }
        let now = dateProvider()
        return listing.data.children.map { child in
            let created = Date(timeIntervalSince1970: TimeInterval(child.data.createdUTC))
            let timestamp = child.data.createdUTC > 0 ? created : now
            let summary = (child.data.selftext?.isEmpty == false) ? child.data.selftext! : child.data.title
            return Event(
                id: "reddit-\(child.data.id)",
                title: child.data.title,
                summary: summary,
                serverScore: child.data.score.map { Double($0) } ?? 0,
                updatedAt: timestamp
            )
        }
    }

    private func parseRSS(data: Data) -> [Event] {
        let parser = RSSParser(data: data)
        return parser.parse().map { item in
            let title = item.title ?? "Untitled"
            let description = item.description ?? title
            let identifier = item.guid ?? title
            return Event(
                id: "rss-\(identifier)",
                title: title,
                summary: description,
                serverScore: 0.5,
                updatedAt: item.pubDate ?? dateProvider()
            )
        }
    }

    public static let defaultSources: [Source] = {
        return [
            Source(name: "Reddit World", kind: .redditJSON(URL(string: "https://www.reddit.com/r/worldnews/.json")!)),
            Source(name: "NYTimes World", kind: .rss(URL(string: "https://rss.nytimes.com/services/xml/rss/nyt/World.xml")!)),
            Source(name: "BBC World", kind: .rss(URL(string: "https://feeds.bbci.co.uk/news/world/rss.xml")!))
        ]
    }()
}

private extension LiveNewsService.Source {
    var url: URL {
        switch kind {
        case .redditJSON(let url):
            return url
        case .rss(let url):
            return url
        }
    }
}

private struct RedditListing: Decodable {
    struct ListingData: Decodable {
        struct Child: Decodable {
            struct ChildData: Decodable {
                let id: String
                let title: String
                let selftext: String?
                let score: Int?
                let createdUTC: Double
            }
            let data: ChildData
        }
        let children: [Child]
    }
    let data: ListingData
}

private final class RSSParser: NSObject, XMLParserDelegate {
    private let parser: XMLParser
    private var items: [RSSItem] = []
    private var currentItem: RSSItem?
    private var currentElement: String?
    private var currentValue: String = ""
    private let dateFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.dateFormat = "EEE, dd MMM yyyy HH:mm:ss zzz"
        return formatter
    }()

    init(data: Data) {
        self.parser = XMLParser(data: data)
        super.init()
        parser.delegate = self
    }

    func parse() -> [RSSItem] {
        parser.parse()
        return items
    }

    func parser(_ parser: XMLParser, didStartElement elementName: String, namespaceURI: String?, qualifiedName qName: String?, attributes attributeDict: [String : String] = [:]) {
        currentElement = elementName
        if elementName == "item" {
            currentItem = RSSItem()
        }
        currentValue = ""
    }

    func parser(_ parser: XMLParser, foundCharacters string: String) {
        currentValue += string
    }

    func parser(_ parser: XMLParser, didEndElement elementName: String, namespaceURI: String?, qualifiedName qName: String?) {
        guard let item = currentItem else { return }
        switch elementName {
        case "title":
            item.title = (item.title ?? "") + currentValue.trimmingCharacters(in: .whitespacesAndNewlines)
        case "description":
            item.description = (item.description ?? "") + currentValue.trimmingCharacters(in: .whitespacesAndNewlines)
        case "guid":
            item.guid = currentValue.trimmingCharacters(in: .whitespacesAndNewlines)
        case "pubDate":
            item.pubDate = dateFormatter.date(from: currentValue.trimmingCharacters(in: .whitespacesAndNewlines))
        case "item":
            if let completed = currentItem {
                items.append(completed)
            }
            currentItem = nil
        default:
            break
        }
    }
}

private final class RSSItem {
    var title: String?
    var description: String?
    var guid: String?
    var pubDate: Date?
}
