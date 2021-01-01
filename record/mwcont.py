import mwglobals
from mwrecord import MwRecord

class MwCONT(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
    
    def load(self):
        self.id = self.get_subrecord_string("NAME")
        self.model = self.get_subrecord_string("MODL")
        self.name = self.get_subrecord_string("FNAM")
        
        self.max_weight = self.get_subrecord_float("CNDT", start=0, length=4)
        flags = self.get_subrecord_int("FLAG")
        self.organic = (flags & 0x1) == 0x1
        self.respawns = (flags & 0x2) == 0x2
        
        self.items = {}
        for i in range(self.num_subrecords("NPCO")):
            count = self.get_subrecord_int("NPCO", index=i, start=0, length=4)
            name = self.get_subrecord_string("NPCO", index=i, start=4, length=32)
            self.items[name] = count
        self.script = self.get_subrecord_string("SCRI")
        mwglobals.object_ids[self.id] = self
    
    def record_details(self):
        return "|Name|    " + str(self) + MwRecord.format_record_details(self, [
        ("\n|Script|", "script"),
        ("\n|Organic|", "organic", False),
        ("\n|Respawns|", "respawns", False),
        ("\n|Max Weight|    {:.2f}", "max_weight"),
        ("\n|Model|", "model"),
        ("\n|Items|", "items")
        ])
    
    def __str__(self):
        return "{} [{}]".format(self.name, self.id)
    
    def diff(self, other):
        MwRecord.diff(self, other, ["model", "name", "max_weight", "organic", "respawns", "items", "script"])