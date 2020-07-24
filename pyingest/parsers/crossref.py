from habanero import Crossref


class CrossrefParser(object):

    def __init__(self, doi=None, parms=None):
        cr = Crossref()
        if doi:
            self.raw_data = cr.works(ids=doi,format="json")
            self.record = self.raw_data['message']
        elif parms:
            self.raw_data = cr.works(filter=parms, cursor="*", limit=500,format="json")
            self.record = None
            self.record_list = []


    def parse(self):

        if
