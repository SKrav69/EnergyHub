class EventBus:
    def __init__(self):
        self.subscribers = []

    def subscribe(self, handler):
        self.subscribers.append(handler)

    def publish(self, event):
        for handler in self.subscribers:
            handler(event)