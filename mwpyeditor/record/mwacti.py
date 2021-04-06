from mwpyeditor.core import mwglobals
from mwpyeditor.core.mwrecord import MwRecord


class MwACTI(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
        self.id_ = ''
        self.model = ''
        self.name = ''
        self.script = None

    def load(self):
        self.id_ = self.parse_string('NAME')
        self.model = self.parse_string('MODL')
        self.name = self.parse_string('FNAM')
        self.script = self.parse_string('SCRI')

        mwglobals.object_ids[self.id_] = self

    def save(self):
        self.clear_subrecords()
        self.add_string(self.id_, 'NAME')
        self.add_string(self.model, 'MODL')
        self.add_string(self.name, 'FNAM')
        self.add_string(self.script, 'SCRI')
        self.save_deleted()

    def record_details(self):
        return MwRecord.format_record_details(self, [
            ("|Name|", '__str__'),
            ("\n|Model|", 'model'),
            ("\n|Script|", 'script')
        ])

    def __str__(self):
        return f"{self.name} [{self.id_}]"

    def diff(self, other, attr_names=None):
        return MwRecord.diff(self, other, attr_names or ['model', 'name', 'script'])
