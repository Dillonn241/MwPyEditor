from mwrecord import MwRecord
import mwglobals

class MwSTAT(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
    
    def load(self):
        self.id = self.get_subrecord_string("NAME")
        self.model = self.get_subrecord_string("MODL")
        mwglobals.object_ids[self.id] = self
    
    def record_details(self):
        return MwRecord.format_record_details(self, [
        ("|ID|", "id"),
        ("\n|Model|", "model")
        ])
    
    def __str__(self):
        return self.id
    
    def compare(self, other):
        MwRecord.compare(self, other, ["model"])