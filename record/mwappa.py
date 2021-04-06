from core import mwglobals
from core.mwrecord import MwRecord


class MwAPPA(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
        self.id_ = ''
        self.model = ''
        self.name = ''
        self.type_id = 0
        self.quality = 0.0
        self.weight = 0.0
        self.value = 0
        self.icon = None
        self.script = None

    def load(self):
        self.id_ = self.parse_string('NAME')
        self.model = self.parse_string('MODL')
        self.name = self.parse_string('FNAM')

        self.type_id = self.parse_int('AADT')
        self.quality = self.parse_float('AADT', start=4)
        self.weight = self.parse_float('AADT', start=8)
        self.value = self.parse_int('AADT', start=12)

        self.icon = self.parse_string('ITEX')
        self.script = self.parse_string('SCRI')

        mwglobals.object_ids[self.id_] = self

    def get_type(self):
        if 0 <= self.type_id < len(mwglobals.APPA_TYPES):
            return mwglobals.APPA_TYPES[self.type_id]

    def set_type(self, value):
        if value in mwglobals.APPA_TYPES:
            self.type_id = mwglobals.APPA_TYPES.index(value)

    def wiki_entry(self):
        return f"""|-\n
                |[[File:TD3-icon-tool-{self.icon}.png]]\n
                |'''{{{{Anchor|{self.name}}}}}'''<br>{{{{Small|{self.id_}}}}}\n
                |{mwglobals.decimal_format(self.weight)}||{self.value}||{mwglobals.decimal_format(self.quality)}"""

    def record_details(self):
        return MwRecord.format_record_details(self, [
            ("|Name|", '__str__'),
            ("\n|Model|", 'model'),
            ("\n|Type|", 'get_type'),
            ("\n|Quality|    {:.2f}", 'quality'),
            ("\n|Weight|    {:.2f}", 'weight'),
            ("\n|Value|", 'value'),
            ("\n|Icon|", 'icon'),
            ("\n|Script|", 'script')
        ])

    def __str__(self):
        return f"{self.name} [{self.id_}]"

    def diff(self, other):
        return MwRecord.diff(self, other, ['model', 'name', 'get_type', 'quality', 'weight', 'value', 'icon', 'script'])
