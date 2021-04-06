from mwpyeditor.core import mwglobals
from mwpyeditor.core.mwrecord import MwRecord


class MwBODY(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
        self.id_ = ''
        self.model = ''
        self.race = ''
        self.part_id = 0
        self.vampire = False
        self.female = False
        self.playable = False
        self.part_type_id = 0

    def load(self):
        self.id_ = self.parse_string('NAME')
        self.model = self.parse_string('MODL')
        self.race = self.parse_string('FNAM')

        self.part_id = self.parse_uint('BYDT', length=1)
        self.vampire = self.parse_uint('BYDT', start=1, length=1) == 1
        flags = self.parse_uint('BYDT', start=2, length=1)
        self.female = (flags & 0x1) == 0x1
        self.playable = (flags & 0x2) == 0x2
        self.part_type_id = self.parse_uint('BYDT', start=3, length=1)

        mwglobals.object_ids[self.id_] = self

    def get_part(self):
        if 0 <= self.part_id < len(mwglobals.BODY_PARTS):
            return mwglobals.BODY_PARTS[self.part_id]

    def set_part(self, value):
        if value in mwglobals.BODY_PARTS:
            self.part_id = mwglobals.BODY_PARTS.index(value)

    def get_part_type(self):
        if 0 <= self.part_type_id < len(mwglobals.BODY_TYPES):
            return mwglobals.BODY_TYPES[self.part_type_id]

    def set_part_type(self, value):
        if value in mwglobals.BODY_TYPES:
            self.part_type_id = mwglobals.BODY_TYPES.index(value)

    def get_skin_type(self):
        return "Vampire" if self.vampire else "Normal"

    def record_details(self):
        string = MwRecord.format_record_details(self, [
            ("|ID|", 'id_'),
            ("\n|Part|", 'get_part'),
            ("\n|Part Type|", 'get_part_type'),
            ("\n|Female|", 'female', False),
            ("\n|Playable|", 'playable', False),
            ("\n|Model|", 'model')
        ])
        if self.part_type_id == mwglobals.BODY_TYPES[0]:  # Skin
            string += MwRecord.format_record_details(self, [
                ("\n|Skin Race|", 'race'),
                ("\n|Skin Type|", 'get_skin_type')
            ])
        return string

    def __str__(self):
        return self.id_

    def diff(self, other):
        return MwRecord.diff(self, other, ['model', 'race', 'get_part', 'vampire', 'female', 'playable',
                                           'get_part_type'])
