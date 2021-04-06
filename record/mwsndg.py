import mwglobals
from mwrecord import MwRecord


class MwSNDG(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
        self.id_ = ''
        self.type_id = 0
        self.creature = None
        self.sound_id = None

    def load(self):
        self.id_ = self.parse_string('NAME')
        self.type_id = self.parse_uint('DATA')
        self.creature = self.parse_string('CNAM')
        self.sound_id = self.parse_string('SNAM')

    def get_type(self):
        if 0 <= self.type_id < len(mwglobals.SNDG_TYPES):
            return mwglobals.SNDG_TYPES[self.type_id]

    def set_type(self, value):
        if value in mwglobals.SNDG_TYPES:
            self.type_id = mwglobals.SNDG_TYPES.index(value)

    def record_details(self):
        return MwRecord.format_record_details(self, [
            ("|ID|", 'id_'),
            ("\n|Type|", 'get_type'),
            ("\n|Creature|", 'creature'),
            ("\n|SoundID|", 'sound_id')
        ])

    def __str__(self):
        return self.id_

    def diff(self, other):
        return MwRecord.diff(self, other, ['get_type', 'creature', 'sound_id'])
