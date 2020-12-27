from mwrecord import MwRecord
import mwglobals

class MwDOOR(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
    
    def load(self):
        self.id = self.get_subrecord_string("NAME")
        self.model = self.get_subrecord_string("MODL")
        self.name = self.get_subrecord_string("FNAM")
        self.script = self.get_subrecord_string("SCRI")
        self.sound_open = self.get_subrecord_string("SNAM")
        self.sound_close = self.get_subrecord_string("ANAM")
        mwglobals.object_ids[self.id] = self
    
    def record_details(self):
        return "|Name|    " + str(self) + MwRecord.format_record_details(self, [
        ("\n|Script|", "script"),
        ("\n|Model|", "model"),
        ("\n|Open Sound ID|", "sound_open"),
        ("\n|Close Sound ID|", "sound_close")
        ])
    
    def __str__(self):
        return "{} [{}]".format(self.name, self.id)
    
    def compare(self, other):
        MwRecord.compare(self, other, ["model", "name", "script", "sound_open", "sound_close"])