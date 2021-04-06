import mwglobals
from mwrecord import MwRecord


class MwSOUN(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
        self.id_ = ''
        self.name = ''
        self.volume = 0
        self.min_range = 0
        self.max_range = 0

    def load(self):
        self.id_ = self.parse_string('NAME')
        self.name = self.parse_string('FNAM')

        self.volume = self.parse_uint('DATA', length=1)
        self.min_range = self.parse_uint('DATA', start=1, length=1)
        self.max_range = self.parse_uint('DATA', start=2, length=1)

        mwglobals.object_ids[self.id_] = self

    def get_volume_float(self):
        return self.volume / 255

    def record_details(self):
        return MwRecord.format_record_details(self, [
            ("|Name|", '__str__'),
            ("\n|Volume|", 'volume'), (" ({:.2f})", 'get_volume_float'),
            ("\n|Range|", 'min_range'), (" - {}", 'max_range')
        ])

    def __str__(self):
        return f"{self.name} [{self.id_}]"

    def diff(self, other):
        return MwRecord.diff(self, other, ['name', 'volume', 'min_range', 'max_range'])
