import mwglobals
from mwrecord import MwRecord


class MwSOUN(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
    
    def load(self):
        self.id = self.get_subrecord_string("NAME")
        self.name = self.get_subrecord_string("FNAM")
        self.volume = self.get_subrecord_uint("DATA", start=0, length=1) / 255
        self.min_range = self.get_subrecord_uint("DATA", start=1, length=1)
        self.max_range = self.get_subrecord_uint("DATA", start=2, length=1)
        mwglobals.object_ids[self.id] = self
    
    def record_details(self):
        return "|Name|    " + str(self) + MwRecord.format_record_details(self, [
            ("\n|Volume|    {:.2f}", "volume"),
            ("\n|Range|", "min_range"), (" - {}", "max_range")
        ])
    
    def __str__(self):
        return "{} [{}]".format(self.name, self.id)
    
    def diff(self, other):
        MwRecord.diff(self, other, ["name", "volume", "min_range", "max_range"])
