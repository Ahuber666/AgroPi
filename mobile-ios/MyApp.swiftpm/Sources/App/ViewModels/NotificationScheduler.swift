import Foundation
import UserNotifications

final class NotificationScheduler {
    func register() {
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound, .badge]) { _, _ in }
    }

    func scheduleDailyBrief() async {
        let content = UNMutableNotificationContent()
        content.title = "Daily Brief Ready"
        content.body = "Tap to read today's top stories"
        var date = DateComponents()
        date.hour = 7
        date.minute = 0
        let trigger = UNCalendarNotificationTrigger(dateMatching: date, repeats: true)
        let request = UNNotificationRequest(identifier: "daily-brief", content: content, trigger: trigger)
        try? await UNUserNotificationCenter.current().add(request)
    }
}
