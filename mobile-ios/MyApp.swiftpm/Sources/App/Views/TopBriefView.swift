import SwiftUI

struct TopBriefView: View {
    let events: [EventViewModel]
    let isLoading: Bool
    let errorMessage: String?
    let refresh: () -> Void

    var body: some View {
        NavigationStack {
            List {
                if let message = errorMessage {
                    Label(message, systemImage: "exclamationmark.triangle")
                        .foregroundColor(.orange)
                }

                if events.isEmpty && !isLoading {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("No stories yet")
                            .font(.headline)
                        Text("Pull to refresh or check your connection to load the latest articles.")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                    .padding(.vertical, 16)
                } else {
                    ForEach(events.prefix(3)) { event in
                        EventCardView(event: event)
                    }
                }
            }
            .listStyle(.insetGrouped)
            .navigationTitle("Top Brief")
            .refreshable { refresh() }
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button(action: refresh) {
                        Label("Refresh", systemImage: "arrow.clockwise")
                    }
                    .disabled(isLoading)
                }
            }
            .overlay(alignment: .center) {
                if isLoading {
                    ProgressView("Loading headlines…")
                        .progressViewStyle(.circular)
                }
            }
        }
    }
}

struct EventCardView: View {
    let event: EventViewModel
    private static let formatter: RelativeDateTimeFormatter = {
        let formatter = RelativeDateTimeFormatter()
        formatter.unitsStyle = .short
        return formatter
    }()

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(event.title)
                .font(.headline)
            Text(event.summary)
                .font(.subheadline)
                .foregroundStyle(.secondary)
                .lineLimit(3)
            HStack {
                Label(event.source, systemImage: "dot.radiowaves.left.and.right")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                Spacer()
                Text(Self.formatter.localizedString(for: event.updatedAt, relativeTo: Date()))
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
        }
        .padding(.vertical, 6)
    }
}
