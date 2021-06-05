class NQRendererText(NQRenderer):
    def render(self, result):
        return result.get('text')
