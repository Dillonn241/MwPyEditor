import mwglobals
from mwrecord import MwRecord

class MwLOCK(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
    
    def load(self):
        self.id = self.get_subrecord_string("NAME")
        self.model = self.get_subrecord_string("MODL")
        self.name = self.get_subrecord_string("FNAM")
        self.weight = self.get_subrecord_float("LKDT", start=0, length=4)
        self.value = self.get_subrecord_int("LKDT", start=4, length=4)
        self.quality = self.get_subrecord_float("LKDT", start=8, length=4)
        self.uses = self.get_subrecord_int("LKDT", start=12, length=4)
        self.script = self.get_subrecord_string("SCRI")
        self.icon = self.get_subrecord_string("ITEX")
        mwglobals.object_ids[self.id] = self
    
    def record_details(self):
        return "|Name|    " + str(self) + MwRecord.format_record_details(self, [
        ("\n|Script|", "script"),
        ("\n|Weight|    {:.2f}", "weight"),
        ("\n|Value|", "value"),
        ("\n|Quality|    {:.2f}", "quality"),
        ("\n|Uses|", "uses"),
        ("\n|Model|", "model"),
        ("\n|Icon|", "icon")
        ])
    
    def __str__(self):
        return "{} [{}]".format(self.name, self.id)
    
    def diff(self, other):
        MwRecord.diff(self, other, ["model", "name", "weight", "value", "quality", "uses", "script", "icon"])