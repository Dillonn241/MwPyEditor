import mwglobals
from mwrecord import MwRecord

class MwREPA(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
    
    def load(self):
        self.id = self.get_subrecord_string("NAME")
        self.model = self.get_subrecord_string("MODL")
        self.name = self.get_subrecord_string("FNAM")
        self.weight = self.get_subrecord_float("RIDT", start=0, length=4)
        self.value = self.get_subrecord_int("RIDT", start=4, length=4)
        self.uses = self.get_subrecord_int("RIDT", start=8, length=4)
        self.quality = self.get_subrecord_float("RIDT", start=12, length=4)
        self.icon = self.get_subrecord_string("ITEX")
        self.script = self.get_subrecord_string("SCRI")
        mwglobals.object_ids[self.id] = self
    
    def record_details(self):
        return "|Name|    " + str(self) + MwRecord.format_record_details(self, [
        ("\n|Script|", "script"),
        ("\n|Weight|    {:.2f}", "weight"),
        ("\n|Value|", "value"),
        ("\n|Uses|", "uses"),
        ("\n|Quality|    {:.2f}", "quality"),
        ("\n|Model|", "model"),
        ("\n|Icon|", "icon")
        ])
    
    def __str__(self):
        return "{} [{}]".format(self.name, self.id)
    
    def diff(self, other):
        MwRecord.diff(self, other, ["model", "name", "weight", "value", "uses", "quality", "icon", "script"])