import SwiftUI

struct TopicListView: View {
    let events: [EventViewModel]
    let isLoading: Bool
    let errorMessage: String?
    let refresh: () -> Void

    private var groupedEvents: [(key: String, value: [EventViewModel])] {
        Dictionary(grouping: events, by: { $0.source })
            .map { ($0.key, $0.value) }
            .sorted(by: { $0.key < $1.key })
    }

    var body: some View {
        NavigationStack {
            List {
                if let message = errorMessage {
                    Label(message, systemImage: "exclamationmark.triangle")
                        .foregroundColor(.orange)
                }

                ForEach(groupedEvents, id: \.key) { source, items in
                    Section(header: Text(source)) {
                        ForEach(items) { event in
                            VStack(alignment: .leading, spacing: 8) {
                                Text(event.title)
                                    .font(.headline)
                                Text(event.summary)
                                    .font(.subheadline)
                                    .foregroundStyle(.secondary)
                                HStack {
                                    Button("Save") {}
                                    Button("Share") {}
                                    Button("Mute") {}
                                }
                                .buttonStyle(.bordered)
                            }
                            .padding(.vertical, 4)
                        }
                    }
                }
            }
            .navigationTitle("All Sources")
            .refreshable { refresh() }
            .overlay(alignment: .center) {
                if isLoading {
                    ProgressView()
                }
            }
        }
    }
}
