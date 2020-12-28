from mwrecord import MwRecord
import mwglobals

class MwTES3(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
    
    def load(self):
        self.version = self.get_subrecord_float("HEDR", start=0, length=4)
        flags = self.get_subrecord_int("HEDR", start=4, length=4)
        self.treat_as_master = (flags & 0x1) == 0x1
        self.author = self.get_subrecord_string("HEDR", start=8, length=32)
        self.description = self.get_subrecord_string("HEDR", start=40, length=256)
        self.num_records = self.get_subrecord_int("HEDR", start=296, length=4)
        
        self.masters = {}
        for i in range(self.num_subrecords("MAST")):
            master_name = self.get_subrecord_string("MAST", index=i)
            master_size = self.get_subrecord_int("DATA", index=i)
            self.masters[master_name] = master_size
    
    def save(self):
        self.set_subrecord_float(self.version, "HEDR", start=0, length=4)
        flags = 0x0
        if self.treat_as_master:
            flags |= 0x1
        self.set_subrecord_int(flags, "HEDR", start=4, length=4)
        self.set_subrecord_string(self.author, "HEDR", start=8, length=32)
        self.set_subrecord_string(self.description, "HEDR", start=40, length=256)
        self.num_records = len([x for x in mwglobals.ordered_records if x.file_name == self.file_name]) - 1
        self.set_subrecord_int(self.num_records, "HEDR", start=296, length=4)
    
    def requires_expansions(self):
        if self.version == 1.3:
            return True
        return False
    
    def record_details(self):
        return MwRecord.format_record_details(self, [
        ("|Version|    {:.2f}", "version"),
        ("\n|Treat as Master|", "treat_as_master"),
        ("\n|Author|", "author"),
        ("\n|Description|", "description"),
        ("\n|Num Records|", "num_records"),
        ("\n|Masters|", "masters", [])
        ])
    
    def __str__(self):
        return self.description
    
    def get_id(self):
        return "TES3"
    
    def diff(self, other):
        MwRecord.diff(self, other, ["version", "treat_as_master", "author", "description", "num_records", "masters"])