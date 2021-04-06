import mwglobals
from mwrecord import MwRecord


class MwSTAT(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
        self.id_ = ''
        self.model = ''

    def load(self):
        self.id_ = self.parse_string('NAME')
        self.model = self.parse_string('MODL')

        mwglobals.object_ids[self.id_] = self

    def record_details(self):
        return MwRecord.format_record_details(self, [
            ("|ID|", 'id_'),
            ("\n|Model|", 'model')
        ])

    def __str__(self):
        return self.id_

    def diff(self, other):
        return MwRecord.diff(self, other, ['model'])
