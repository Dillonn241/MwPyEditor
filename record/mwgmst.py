from mwrecord import MwRecord
import mwglobals

class MwGMST(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
    
    def load(self):
        self.name = self.get_subrecord_string("NAME")
        if "STRV" in self.subrecords:
            self.type = "String"
            self.value = self.get_subrecord_string("STRV")
        elif "INTV" in self.subrecords:
            self.type = "Integer"
            self.value = self.get_subrecord_int("INTV")
        elif "FLTV" in self.subrecords:
            self.type = "Float"
            self.value = self.get_subrecord_float("FLTV")
        else:
            self.value = ""
        mwglobals.game_settings[self.name] = self.value
    
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
    
    def compare(self, other):
        MwRecord.compare(self, other, ["type", "value"])