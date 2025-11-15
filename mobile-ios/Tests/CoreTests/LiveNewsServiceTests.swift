import XCTest
@testable import Core

final class LiveNewsServiceTests: XCTestCase {
    func testAggregatesEventsFromMultipleSources() {
        let session = ResponseSessionStub()
        session.responses = [
            URL(string: "https://www.reddit.com/r/worldnews/.json")!: .success(Self.redditSample),
            URL(string: "https://feeds.bbci.co.uk/news/world/rss.xml")!: .success(Self.rssSample)
        ]
        let sources = [
            LiveNewsService.Source(name: "reddit", kind: .redditJSON(URL(string: "https://www.reddit.com/r/worldnews/.json")!)),
            LiveNewsService.Source(name: "bbc", kind: .rss(URL(string: "https://feeds.bbci.co.uk/news/world/rss.xml")!))
        ]
        let service = LiveNewsService(sources: sources, session: session, dateProvider: { Date(timeIntervalSince1970: 0) })
        let expectation = expectation(description: "aggregated")

        service.fetchTopStories(limit: 5) { result in
            switch result {
            case .success(let events):
                XCTAssertEqual(events.count, 2)
                XCTAssertTrue(events.contains(where: { $0.title == "Reddit Story" && $0.source == "reddit" }))
                XCTAssertTrue(events.contains(where: { $0.title == "BBC Story" && $0.source == "bbc" }))
            case .failure(let error):
                XCTFail("Unexpected error: \(error)")
            }
            expectation.fulfill()
        }

        waitForExpectations(timeout: 1)
    }

    func testReturnsErrorWhenAllSourcesFail() {
        let session = ResponseSessionStub()
        session.responses = [
            URL(string: "https://www.reddit.com/r/worldnews/.json")!: .failure(URLError(.badURL)),
            URL(string: "https://feeds.bbci.co.uk/news/world/rss.xml")!: .failure(URLError(.timedOut))
        ]
        let sources = [
            LiveNewsService.Source(name: "reddit", kind: .redditJSON(URL(string: "https://www.reddit.com/r/worldnews/.json")!)),
            LiveNewsService.Source(name: "bbc", kind: .rss(URL(string: "https://feeds.bbci.co.uk/news/world/rss.xml")!))
        ]
        let service = LiveNewsService(sources: sources, session: session)
        let expectation = expectation(description: "errors")

        service.fetchTopStories(limit: 5) { result in
            switch result {
            case .success:
                XCTFail("Expected failure")
            case .failure(let error):
                XCTAssertNotNil(error)
            }
            expectation.fulfill()
        }

        waitForExpectations(timeout: 1)
    }
}

private final class ResponseSessionStub: NetworkSession {
    var responses: [URL: Result<Data, Error>] = [:]

    func makeDataTask(with request: URLRequest, completionHandler: @escaping (Data?, URLResponse?, Error?) -> Void) -> NetworkDataTask {
        if let url = request.url, let response = responses[url] {
            switch response {
            case .success(let data):
                completionHandler(data, nil, nil)
            case .failure(let error):
                completionHandler(nil, nil, error)
            }
        } else {
            completionHandler(nil, nil, URLError(.badURL))
        }
        return NetworkDataTaskStub()
    }
}

private struct NetworkDataTaskStub: NetworkDataTask {
    func resume() {}
}

private extension LiveNewsServiceTests {
    static var redditSample: Data {
        let json = """
        {
          "data": {
            "children": [
              {
                "data": {
                  "id": "abc",
                  "title": "Reddit Story",
                  "selftext": "A breaking reddit post",
                  "score": 10,
                  "createdUTC": 0
                }
              }
            ]
          }
        }
        """
        return Data(json.utf8)
    }

    static var rssSample: Data {
        let xml = """
        <rss><channel>
        <item>
            <title>BBC Story</title>
            <description>BBC summary</description>
            <guid>bbc-1</guid>
            <pubDate>Fri, 14 Nov 2025 10:00:00 GMT</pubDate>
        </item>
        </channel></rss>
        """
        return Data(xml.utf8)
    }
}
