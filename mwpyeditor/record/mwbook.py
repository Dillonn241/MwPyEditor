from mwpyeditor.core import mwglobals
from mwpyeditor.core.mwrecord import MwRecord


class MwBOOK(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
        self.id_ = ''
        self.model = ''
        self.name = None
        self.weight = 0.0
        self.value = 0
        self.scroll = False
        self.skill_id = -1
        self.enchantment = 0
        self.icon = None
        self.script = None
        self.enchanting = None
        self.text = None

    def load(self):
        self.id_ = self.parse_string('NAME')
        self.model = self.parse_string('MODL')
        self.name = self.parse_string('FNAM')

        self.weight = self.parse_float('BKDT')
        self.value = self.parse_uint('BKDT', start=4)
        flags = self.parse_uint('BKDT', start=8)
        self.scroll = (flags & 0x1) == 0x1
        self.skill_id = self.parse_int('BKDT', start=12)
        self.enchantment = self.parse_uint('BKDT', start=16)

        self.icon = self.parse_string('ITEX')
        self.script = self.parse_string('SCRI')
        self.enchanting = self.parse_string('ENAM')
        self.text = self.parse_string('TEXT')

        mwglobals.object_ids[self.id_] = self

    def get_skill(self):
        if 0 <= self.skill_id < len(mwglobals.SKILLS):
            return mwglobals.SKILLS[self.skill_id]

    def set_skill(self, value):
        if value in mwglobals.SKILLS:
            self.skill_id = mwglobals.SKILLS.index(value)

    def record_details(self):
        return MwRecord.format_record_details(self, [
            ("|Name|", '__str__'),
            ("\n|Model|", 'model'),
            ("\n|Weight|    {:.2f}", 'weight'),
            ("\n|Value|", 'value'),
            ("\n|Scroll|", 'scroll', False),
            ("\n|Skill|", 'get_skill'),
            ("\n|Enchantment|", 'enchantment'),
            ("\n|Icon|", 'icon'),
            ("\n|Script|", 'script'),
            ("\n|Enchanting|", 'enchanting'),
            ("\n|Text|", 'text')
        ])

    def __str__(self):
        return f"{self.name} [{self.id_}]"

    def diff(self, other):
        return MwRecord.diff(self, other, ['model', 'name', 'weight', 'value', 'scroll', 'skill_id', 'enchantment',
                                           'icon', 'script', 'enchanting', 'text'])
