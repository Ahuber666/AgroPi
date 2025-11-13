import SwiftUI

struct TopBriefView: View {
    let events: [EventViewModel]

    var body: some View {
        NavigationStack {
            List(events.prefix(3)) { event in
                NavigationLink(value: event.id) {
                    VStack(alignment: .leading, spacing: 4) {
                        Text(event.title).font(.headline)
                        Text(event.summary).font(.subheadline).foregroundStyle(.secondary)
                    }
                }
            }
            .navigationTitle("Top Brief")
        }
    }
}
