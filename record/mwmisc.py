from mwrecord import MwRecord
import mwglobals

class MwMISC(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
    
    def load(self):
        self.id = self.get_subrecord_string("NAME")
        self.model = self.get_subrecord_string("MODL")
        self.name = self.get_subrecord_string("FNAM")
        self.weight = self.get_subrecord_float("MCDT", start=0, length=4)
        self.value = self.get_subrecord_int("MCDT", start=4, length=4)
        self.is_key = self.get_subrecord_int("MCDT", start=8, length=4) == 1
        self.script = self.get_subrecord_string("SCRI")
        self.icon = self.get_subrecord_string("ITEX")
        mwglobals.object_ids[self.id] = self
    
    def record_details(self):
        return "|Name|    " + str(self) + MwRecord.format_record_details(self, [
        ("\n|Script|", "script"),
        ("\n|Weight|    {:.2f}", "weight"),
        ("\n|Value|", "value"),
        ("\n|Model|", "model"),
        ("\n|Icon|", "icon"),
        ("\n|Is Key|", "is_key", False)
        ])
    
    def __str__(self):
        return "{} [{}]".format(self.name, self.id)
    
    def diff(self, other):
        MwRecord.diff(self, other, ["model", "name", "weight", "value", "is_key", "script", "icon"])