class Queue:
    def __init__(self, values=[]):
        self.values = values

    def enqueue(self, value):
        self.values.append(value)

    def dequeue(self):
        return self.values.pop()

    def peek(self):
        return self.queue[self.size() - 1]

    def isEmpty(self):
        return self.size() == 0

    def size(self):
        return len(self.values)