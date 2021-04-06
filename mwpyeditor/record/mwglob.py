from mwpyeditor.core import mwglobals
from mwpyeditor.core.mwrecord import MwRecord


class MwGLOB(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
        self.id_ = ''
        self.type = ''
        self.value = 0.0

    def load(self):
        self.id_ = self.parse_string('NAME')
        self.type = self.parse_string('FNAM')
        self.value = self.parse_float('FLTV')
        if type == 's':
            self.value = int(self.value)
            if self.value > 2 ** 15 - 1:
                self.value = 0
            elif self.value < -2 ** 15:
                self.value = 0
        elif type == 'l':
            self.value = int(self.value)

        mwglobals.object_ids[self.id_] = self

    def save(self):
        self.clear_subrecords()
        self.add_string(self.id_, 'NAME')
        self.add_string(self.type, 'FNAM', terminator=False)
        self.add_float(self.value, 'FLTV')
        self.save_deleted()

    def record_details(self):
        return MwRecord.format_record_details(self, [
            ("|ID|", 'id_'),
            ("\n|Type|", 'type'),
            ("\n|Value|    {:.4f}", 'value')
        ])

    def __str__(self):
        return f"{self.id_} = {self.value}"

    def diff(self, other):
        return MwRecord.diff(self, other, ['type', 'value'])
