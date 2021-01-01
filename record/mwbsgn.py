import mwglobals
from mwrecord import MwRecord

class MwBSGN(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
    
    def load(self):
        self.id = self.get_subrecord_string("NAME")
        self.name = self.get_subrecord_string("FNAM")
        self.texture = self.get_subrecord_string("TNAM")
        self.description = self.get_subrecord_string("DESC")
        self.spells = []
        for i in range(self.num_subrecords("NPCS")):
            self.spells += [self.get_subrecord_string("NPCS", index=i)]
        mwglobals.object_ids[self.id] = self
    
    def record_details(self):
        return "|Name|    " + str(self) + MwRecord.format_record_details(self, [
        ("\n|Texture|", "texture"),
        ("\n|Description|", "description"),
        ("\n|Spells|", "spells", [])
        ])
    
    def __str__(self):
        return "{} [{}]".format(self.name, self.id)
    
    def diff(self, other):
        MwRecord.diff(self, other, ["name", "texture", "description", "spells"])