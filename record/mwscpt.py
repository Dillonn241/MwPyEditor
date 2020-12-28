from mwrecord import MwRecord
import mwglobals

class MwSCPT(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
    
    def load(self):
        self.id = self.get_subrecord_string("SCHD", start=0, length=32)
        self.num_shorts = self.get_subrecord_int("SCHD", start=32, length=4)
        self.num_longs = self.get_subrecord_int("SCHD", start=36, length=4)
        self.num_floats = self.get_subrecord_int("SCHD", start=40, length=4)
        self.local_vars = self.get_subrecord_string("SCVR")
        if self.local_vars != None:
            self.local_vars = self.local_vars.split("\x00")
        self.text = self.get_subrecord_string("SCTX")
        mwglobals.object_ids[self.id] = self
    
    def record_details(self, full=False):
        string = MwRecord.format_record_details(self, [
        ("|ID|", "id"),
        ("\n|Num Shorts|", "num_shorts"),
        ("\n|Num Longs|", "num_longs"),
        ("\n|Num Floats|", "num_floats"),
        ("\n|Local Vars|", "local_vars", [])
        ]) + "\n" if full else ""
        return string + MwRecord.format_record_details(self, [
        ("|Text|", "text")
        ])
    
    def __str__(self):
        return self.id
    
    def diff(self, other):
        MwRecord.diff(self, other, ["num_shorts", "num_longs", "num_floats", "local_vars", "text"])