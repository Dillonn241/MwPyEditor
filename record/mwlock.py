from core import mwglobals
from core.mwrecord import MwRecord


class MwLOCK(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
        self.id_ = ''
        self.model = ''
        self.name = None
        self.weight = 0.0
        self.value = 0
        self.quality = 0.0
        self.uses = 0
        self.script = None
        self.icon = None

    def load(self):
        self.id_ = self.parse_string('NAME')
        self.model = self.parse_string('MODL')
        self.name = self.parse_string('FNAM')

        self.weight = self.parse_float('LKDT')
        self.value = self.parse_int('LKDT', start=4)
        self.quality = self.parse_float('LKDT', start=8)
        self.uses = self.parse_int('LKDT', start=12)

        self.script = self.parse_string('SCRI')
        self.icon = self.parse_string('ITEX')

        mwglobals.object_ids[self.id_] = self

    def record_details(self):
        return MwRecord.format_record_details(self, [
            ("|Name|", "__str__"),
            ("\n|Model|", "model"),
            ("\n|Weight|    {:.2f}", "weight"),
            ("\n|Value|", "value"),
            ("\n|Quality|    {:.2f}", "quality"),
            ("\n|Uses|", "uses"),
            ("\n|Script|", "script"),
            ("\n|Icon|", "icon")
        ])

    def __str__(self):
        return "{} [{}]".format(self.name, self.id_)

    def diff(self, other):
        return MwRecord.diff(self, other, ["model", "name", "weight", "value", "quality", "uses", "script", "icon"])
