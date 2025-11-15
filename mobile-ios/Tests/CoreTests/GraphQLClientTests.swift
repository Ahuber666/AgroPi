import XCTest
@testable import Core

final class GraphQLClientTests: XCTestCase {
    func testFetchSlatesReturnsEventsOnSuccess() {
        let session = NetworkSessionStub()
        session.stubbedData = GraphQLClientTests.sampleResponse
        let expectation = expectation(description: "fetch completes")
        let client = GraphQLClient(session: session, dateProvider: { Date(timeIntervalSince1970: 0) })

        client.fetchSlates(locale: "en-US", topics: ["world"]) { result in
            switch result {
            case .success(let events):
                XCTAssertEqual(events.count, 1)
                XCTAssertEqual(events.first?.title, "Breaking Story")
                XCTAssertEqual(events.first?.updatedAt, Date(timeIntervalSince1970: 0))
                XCTAssertEqual(events.first?.source, "GraphQL")
            case .failure(let error):
                XCTFail("Unexpected error: \(error)")
            }
            expectation.fulfill()
        }

        waitForExpectations(timeout: 1)
    }

    func testFetchSlatesPropagatesNetworkError() {
        let session = NetworkSessionStub()
        session.stubbedError = URLError(.notConnectedToInternet)
        let expectation = expectation(description: "network error")
        let client = GraphQLClient(session: session)

        client.fetchSlates(locale: "en-US", topics: ["world"]) { result in
            switch result {
            case .success:
                XCTFail("Expected failure")
            case .failure(let error):
                XCTAssertTrue(error is URLError)
            }
            expectation.fulfill()
        }

        waitForExpectations(timeout: 1)
    }

    func testFetchSlatesHandlesDecodingIssues() {
        let session = NetworkSessionStub()
        session.stubbedData = Data("{bad json}".utf8)
        let expectation = expectation(description: "decoding error")
        let client = GraphQLClient(session: session)

        client.fetchSlates(locale: "en-US", topics: ["world"]) { result in
            switch result {
            case .success:
                XCTFail("Expected decoding failure")
            case .failure(let error):
                XCTAssertEqual(error as? GraphQLClient.ClientError, .decodingFailed)
            }
            expectation.fulfill()
        }

        waitForExpectations(timeout: 1)
    }
}

private final class NetworkSessionStub: NetworkSession {
    var capturedRequest: URLRequest?
    var stubbedData: Data?
    var stubbedError: Error?

    func makeDataTask(with request: URLRequest, completionHandler: @escaping (Data?, URLResponse?, Error?) -> Void) -> NetworkDataTask {
        capturedRequest = request
        completionHandler(stubbedData, nil, stubbedError)
        return NetworkDataTaskStub()
    }
}

private struct NetworkDataTaskStub: NetworkDataTask {
    func resume() {}
}

private extension GraphQLClientTests {
    static var sampleResponse: Data {
        let json = """
        {"data":{"slates":[{"events":[{"id":"evt","title":"Breaking Story","summary":"Details","serverScore":0.9}]}]}}
        """
        return Data(json.utf8)
    }
}
