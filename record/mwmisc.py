import mwglobals
from mwrecord import MwRecord


class MwMISC(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
        self.id_ = ''
        self.model = ''
        self.name = None
        self.weight = 0.0
        self.value = 0
        self.is_key = False
        self.script = None
        self.icon = None

    def load(self):
        self.id_ = self.parse_string('NAME')
        self.model = self.parse_string('MODL')
        self.name = self.parse_string('FNAM')
        self.weight = self.parse_float('MCDT')
        self.value = self.parse_uint('MCDT', start=4)
        self.is_key = self.parse_uint('MCDT', start=8) == 1
        self.script = self.parse_string('SCRI')
        self.icon = self.parse_string('ITEX')

        mwglobals.object_ids[self.id_] = self

    def record_details(self):
        return MwRecord.format_record_details(self, [
            ("|Name|", '__str__'),
            ("\n|Model|", 'model'),
            ("\n|Weight|    {:.2f}", 'weight'),
            ("\n|Value|", 'value'),
            ("\n|Is Key|", 'is_key', False),
            ("\n|Script|", 'script'),
            ("\n|Icon|", 'icon')
        ])

    def __str__(self):
        return f"{self.name} [{self.id_}]"

    def diff(self, other):
        return MwRecord.diff(self, other, ['model', 'name', 'weight', 'value', 'is_key', 'script', 'icon'])
