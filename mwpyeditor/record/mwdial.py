from mwpyeditor.core import mwglobals
from mwpyeditor.core.mwrecord import MwRecord


class MwDIAL(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
        self.id_ = ''
        self.type_id = 0
        self.infos = []

    def load(self):
        self.id_ = self.parse_string('NAME')
        self.type_id = self.parse_uint('DATA', length=1)

        mwglobals.dial_infos[self.id_] = []

    def save(self):
        self.clear_subrecords()
        self.add_string(self.id_, 'NAME')
        self.add_uint(self.type_id, 'DATA', length=1)
        self.save_deleted()

    def get_type(self):
        if 0 <= self.type_id < len(mwglobals.DIAL_TYPES):
            return mwglobals.DIAL_TYPES[self.type_id]

    def set_type(self, value):
        if value in mwglobals.DIAL_TYPES:
            self.type_id = mwglobals.DIAL_TYPES.index(value)

    def filter_infos(self, actor='', race='', class_='', faction='', cell='', pc_faction=''):
        return [x for x in self.infos if x.filter(actor=actor, race=race, class_=class_, faction=faction, cell=cell,
                                                  pc_faction=pc_faction)]

    def record_details(self):
        return str(self)

    def __str__(self):
        return f"{self.id_} <{self.get_type()}>"

    def __repr__(self):
        return str(self)

    def diff(self, other):
        return MwRecord.diff(self, other)
