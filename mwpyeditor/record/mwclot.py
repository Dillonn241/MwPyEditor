from mwpyeditor.core import mwglobals
from mwpyeditor.core.mwrecord import MwRecord
from mwpyeditor.record.mwarmo import load_body_parts


class MwCLOT(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
        self.id_ = ''
        self.model = ''
        self.name = None
        self.type_id = 0
        self.weight = 0.0
        self.value = 0
        self.enchantment = 0
        self.script = None
        self.icon = None
        self.body_parts = []
        self.enchanting = None

    def load(self):
        self.id_ = self.parse_string('NAME')
        self.model = self.parse_string('MODL')
        self.name = self.parse_string('FNAM')

        self.type_id = self.parse_uint('CTDT')
        self.weight = self.parse_float('CTDT', start=4)
        self.value = self.parse_uint('CTDT', start=8, length=2)
        self.enchantment = self.parse_uint('CTDT', start=10, length=2)

        self.script = self.parse_string('SCRI')
        self.icon = self.parse_string('ITEX')

        load_body_parts(self)

        self.enchanting = self.parse_string('ENAM')

        mwglobals.object_ids[self.id_] = self

    def get_type(self):
        if 0 <= self.type_id < len(mwglobals.CLOT_TYPES):
            return mwglobals.CLOT_TYPES[self.type_id]

    def set_type(self, value):
        if value in mwglobals.CLOT_TYPES:
            self.type_id = mwglobals.CLOT_TYPES.index(value)

    def is_glove(self):
        return self.type_id == 5 or self.type_id == 6  # Right Glove or Left Glove

    def record_details(self):
        return MwRecord.format_record_details(self, [
            ("|Name|", '__str__'),
            ("\n|Type|", 'get_type'),
            ("\n|Script|", 'script'),
            ("\n|Weight|    {:.2f}", 'weight'),
            ("\n|Value|", 'value'),
            ("\n|Model|", 'model'),
            ("\n|Icon|", 'icon'),
            ("\n|Enchantment|", 'enchantment'),
            ("\n|Enchanting|", 'enchanting'),
            ("\n|Body Parts|", 'body_parts')
        ])

    def __str__(self):
        return f"{self.name} [{self.id_}]"

    def diff(self, other):
        return MwRecord.diff(self, other, ['model', 'name', 'get_type', 'weight', 'value', 'enchantment', 'script',
                                           'icon', 'body_parts', 'enchanting'])
