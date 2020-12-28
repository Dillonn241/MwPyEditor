from mwrecord import MwRecord
import mwglobals

class MwSNDG(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
    
    def load(self):
        self.id = self.get_subrecord_string("NAME")
        self.type = mwglobals.SNDG_TYPES[self.get_subrecord_int("DATA")]
        self.sound_id = self.get_subrecord_string("SNAM")
        self.creature = self.get_subrecord_string("CNAM")
    
    def record_details(self):
        return MwRecord.format_record_details(self, [
        ("|ID|", "id"),
        ("\n|Creature|", "creature"),
        ("\n|Type|", "type"),
        ("\n|SoundID|", "sound_id")
        ])
    
    def __str__(self):
        return self.id
    
    def diff(self, other):
        MwRecord.diff(self, other, ["type", "sound_id", "creature"])