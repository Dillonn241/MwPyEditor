from mwrecord import MwRecord
import mwglobals

class MwBODY(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
    
    def load(self):
        self.id = self.get_subrecord_string("NAME")
        self.model = self.get_subrecord_string("MODL")
        self.race = self.get_subrecord_string("FNAM")
        self.part = mwglobals.BODY_PARTS[self.get_subrecord_int("BYDT", start=0, length=1, signed=False)]
        self.vampire = self.get_subrecord_int("BYDT", start=1, length=1, signed=False) == 1
        flags = self.get_subrecord_int("BYDT", start=2, length=1, signed=False)
        self.female = (flags & 0x1) == 0x1
        self.playable = (flags & 0x2) == 0x2
        self.part_type = mwglobals.BODY_TYPES[self.get_subrecord_int("BYDT", start=3, length=1, signed=False)]
        mwglobals.object_ids[self.id] = self
    
    def get_skin_type(self):
        if self.vampire:
            return "Vampire"
        return "Normal"
    
    def record_details(self):
        string = MwRecord.format_record_details(self, [
        ("|ID|", "id"),
        ("\n|Part|", "part"),
        ("\n|Part Type|", "part_type"),
        ("\n|Female|", "female", False),
        ("\n|Playable|", "playable", False),
        ("\n|Model|", "model")
        ])
        if self.part_type == "Skin":
            string += MwRecord.format_record_details(self, [
            ("\n|Skin Race|", "race"),
            ("\n|Skin Type|", "get_skin_type")
            ])
        return string
    
    def __str__(self):
        return self.id
    
    def diff(self, other):
        MwRecord.diff(self, other, ["model", "race", "part", "vampire", "female", "playable", "part_type"])