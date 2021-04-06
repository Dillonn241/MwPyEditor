from mwpyeditor.core import mwglobals
from mwpyeditor.core.mwrecord import MwRecord


class MwDOOR(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
        self.id_ = ''
        self.model = ''
        self.name = None
        self.script = None
        self.sound_open = None
        self.sound_close = None

    def load(self):
        self.id_ = self.parse_string('NAME')
        self.model = self.parse_string('MODL')
        self.name = self.parse_string('FNAM')
        self.script = self.parse_string('SCRI')
        self.sound_open = self.parse_string('SNAM')
        self.sound_close = self.parse_string('ANAM')

        mwglobals.object_ids[self.id_] = self

    def save(self):
        self.clear_subrecords()
        self.add_string(self.id_, 'NAME')
        self.add_string(self.model, 'MODL')
        self.add_string(self.name, 'FNAM')
        self.add_string(self.script, 'SCRI')
        self.add_string(self.sound_open, 'SNAM')
        self.add_string(self.sound_close, 'ANAM')
        self.save_deleted()

    def record_details(self):
        return MwRecord.format_record_details(self, [
            ("|Name|", '__str__'),
            ("\n|Model|", 'model'),
            ("\n|Script|", 'script'),
            ("\n|Open Sound ID|", 'sound_open'),
            ("\n|Close Sound ID|", 'sound_close')
        ])

    def __str__(self):
        return f"{self.name} [{self.id_}]"

    def diff(self, other):
        return MwRecord.diff(self, other, ['model', 'name', 'script', 'sound_open', 'sound_close'])
