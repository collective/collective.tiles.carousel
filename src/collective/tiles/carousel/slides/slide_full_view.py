from Products.Five import BrowserView


class SlideFullView(BrowserView):
    def __call__(self, item, data):
        self.update(item, data)
        return self.index()

    def update(self, item, data):
        self.item = item
