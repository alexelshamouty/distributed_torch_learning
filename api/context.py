from oslo_context import context

class RequestContext(context.RequestContext):
    def __init__(self, **kwargs):
        super(RequestContext, self).__init__(**kwargs)

    def get_current():
        return context.get_current()
