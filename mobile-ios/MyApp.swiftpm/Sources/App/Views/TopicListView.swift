import SwiftUI

struct TopicListView: View {
    let events: [EventViewModel]

    var body: some View {
        List {
            ForEach(events) { event in
                Section(header: Text(event.title)) {
                    Text(event.summary)
                    HStack {
                        Button("Save") {}
                        Button("Share") {}
                        Button("Mute") {}
                    }
                    .buttonStyle(.bordered)
                }
            }
        }
    }
}
