from core import mwglobals
from core.mwrecord import MwRecord


class MwBSGN(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
        self.id_ = ''
        self.name = None
        self.spells = []
        self.texture = None
        self.description = None

    def load(self):
        self.id_ = self.parse_string('NAME')
        self.name = self.parse_string('FNAM')
        self.spells = self.parse_string_array('NPCS')
        self.texture = self.parse_string('TNAM')
        self.description = self.parse_string('DESC')

        mwglobals.object_ids[self.id_] = self

    def record_details(self):
        return MwRecord.format_record_details(self, [
            ("|Name|", '__str__'),
            ("\n|Spells|", 'spells', []),
            ("\n|Texture|", 'texture'),
            ("\n|Description|", 'description')
        ])

    def __str__(self):
        return f"{self.name} [{self.id_}]"

    def diff(self, other):
        return MwRecord.diff(self, other, ['name', 'spells', 'texture', 'description'])
