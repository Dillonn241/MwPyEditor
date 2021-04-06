from mwrecord import MwRecord


class MwSSCR(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
        self.data = ''
        self.id_ = None

    def load(self):
        self.data = self.parse_string('DATA')
        self.id_ = self.parse_string('NAME')

    def record_details(self):
        return MwRecord.format_record_details(self, [
            ("|ID|", 'id_')
        ])

    def __str__(self):
        return self.id_

    def diff(self, other):
        return MwRecord.diff(self, other)
