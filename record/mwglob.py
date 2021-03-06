import mwglobals
from mwrecord import MwRecord


class MwGLOB(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
    
    def load(self):
        self.name = self.get_subrecord_string("NAME")
        prefix = self.get_subrecord_string("FNAM")
        if prefix == "s":
            self.type = "Short"
            self.value = int(self.get_subrecord_float("FLTV"))
            if self.value > 2 ** 15 - 1:
                self.value = 0
            elif self.value < -2 ** 15:
                self.value = 0
        elif prefix == "l":
            self.type = "Long"
            self.value = int(self.get_subrecord_float("FLTV"))
        elif prefix == "f":
            self.type = "Float"
            self.value = self.get_subrecord_float("FLTV")
        
        mwglobals.object_ids[self.name] = self
    
    def record_details(self):
        return MwRecord.format_record_details(self, [
            ("|Name|", "name"),
            ("\n|Type|", "type"),
            ("\n|Value|    {:.4f}", "value")
        ])
    
    def __str__(self):
        return "{} = {}".format(self.name, self.value)
    
    def get_id(self):
        return self.name
    
    def diff(self, other):
        MwRecord.diff(self, other, ["type", "value"])
