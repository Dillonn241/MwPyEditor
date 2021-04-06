from mwpyeditor.core import mwglobals
from mwpyeditor.core.mwrecord import MwRecord


class MwPROB(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
        self.id_ = ''
        self.model = ''
        self.name = None
        self.weight = 0.0
        self.value = 0
        self.quality = 0.0
        self.uses = 0
        self.icon = None
        self.script = None

    def load(self):
        self.id_ = self.parse_string('NAME')
        self.model = self.parse_string('MODL')
        self.name = self.parse_string('FNAM')

        self.weight = self.parse_float('PBDT')
        self.value = self.parse_uint('PBDT', start=4)
        self.quality = self.parse_float('PBDT', start=8)
        self.uses = self.parse_uint('PBDT', start=12)

        self.icon = self.parse_string('ITEX')
        self.script = self.parse_string('SCRI')

        mwglobals.object_ids[self.id_] = self

    def record_details(self):
        return MwRecord.format_record_details(self, [
            ("|Name|", '__str__'),
            ("\n|Model|", 'model'),
            ("\n|Weight|    {:.2f}", 'weight'),
            ("\n|Value|", 'value'),
            ("\n|Quality|    {:.2f}", 'quality'),
            ("\n|Uses|", 'uses'),
            ("\n|Icon|", 'icon'),
            ("\n|Script|", 'script')
        ])

    def __str__(self):
        return f"{self.name} [{self.id_}]"

    def diff(self, other):
        return MwRecord.diff(self, other, ['model', 'name', 'weight', 'value', 'quality', 'uses', 'icon', 'script'])
