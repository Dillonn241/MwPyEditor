from mwpyeditor.core import mwglobals
from mwpyeditor.core.mwrecord import MwRecord


class MwCONT(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
        self.id_ = ''
        self.model = ''
        self.name = None
        self.max_weight = 0.0
        self.organic = False
        self.respawns = False
        self.script = None
        self.items = []

    def load(self):
        self.id_ = self.parse_string('NAME')
        self.model = self.parse_string('MODL')
        self.name = self.parse_string('FNAM')
        self.max_weight = self.parse_float('CNDT')
        flags = self.parse_uint('FLAG')
        self.organic = (flags & 0x1) == 0x1
        self.respawns = (flags & 0x2) == 0x2
        self.script = self.parse_string('SCRI')

        self.items = {self.parse_string('NPCO', index=i, start=4, length=32):
                      self.parse_uint('NPCO', index=i)
                      for i in range(self.num_subrecords('NPCO'))}

        mwglobals.object_ids[self.id_] = self

    def save(self):
        self.clear_subrecords()
        self.add_string(self.id_, 'NAME')
        self.add_string(self.model, 'MODL')
        self.add_string(self.name, 'FNAM')
        self.add_float(self.max_weight, 'CNDT')
        flags = 0x8  # unknown flag 0x8 always set
        if self.organic:
            flags |= 0x1
        if self.respawns:
            flags |= 0x2
        self.add_uint(flags, 'FLAG')
        self.add_string(self.script, 'SCRI')

        for item in self.items:
            sub_npco = self.add_subrecord("NPCO")
            sub_npco.add_uint(self.items[item])
            sub_npco.add_string(item, length=32)

        self.save_deleted()

    def record_details(self):
        return MwRecord.format_record_details(self, [
            ("|Name|", '__str__'),
            ("\n|Model|", 'model'),
            ("\n|Max Weight|    {:.2f}", 'max_weight'),
            ("\n|Organic|", 'organic', False),
            ("\n|Respawns|", 'respawns', False),
            ("\n|Script|", 'script'),
            ("\n|Items|", 'items')
        ])

    def __str__(self):
        return f"{self.name} [{self.id_}]"

    def diff(self, other):
        return MwRecord.diff(self, other, ['model', 'name', 'max_weight', 'organic', 'respawns', 'script', 'items'])
