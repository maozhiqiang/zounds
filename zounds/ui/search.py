import tornado
from baseapp import BaseZoundsApp, RequestContext


class ZoundsSearch(BaseZoundsApp):
    def __init__(
            self,
            base_path=r'/zounds/',
            model=None,
            visualization_feature=None,
            audio_feature=None,
            search=None,
            n_results=10):
        super(ZoundsSearch, self).__init__(
                base_path=base_path,
                model=model,
                visualization_feature=visualization_feature,
                audio_feature=audio_feature,
                html='search.html',
                javascript='search.js')
        self.n_results = n_results
        self.search = search

    def custom_routes(self):
        return [
            (r'/zounds/search', self.search_handler())
        ]

    def search_handler(self):
        app = self

        class SearchHandler(tornado.web.RequestHandler):
            def get(self):
                results = self.search.random_search(n_results=self.n_results)
                context = RequestContext(value=results)
                output = app.serialize(context)
                self.set_header('Content-Type', output.content_type)
                self.write(output.data)

        return SearchHandler
