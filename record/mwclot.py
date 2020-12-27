from mwrecord import MwRecord
import mwglobals
from record.mwarmo import load_body_parts

class MwCLOT(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
    
    def load(self):
        self.id = self.get_subrecord_string("NAME")
        self.model = self.get_subrecord_string("MODL")
        self.name = self.get_subrecord_string("FNAM")
        self.type = mwglobals.CLOT_TYPES[self.get_subrecord_int("CTDT", start=0, length=4)]
        self.weight = self.get_subrecord_float("CTDT", start=4, length=4)
        self.value = self.get_subrecord_int("CTDT", start=8, length=2)
        self.enchantment = self.get_subrecord_int("CTDT", start=10, length=2)
        
        self.script = self.get_subrecord_string("SCRI")
        self.icon = self.get_subrecord_string("ITEX")
        
        load_body_parts(self)
        
        self.enchanting = self.get_subrecord_string("ENAM")
        mwglobals.object_ids[self.id] = self
    
    def is_glove(self):
        return self.type == "Left Glove" or self.type == "Right Glove"
    
    def record_details(self):
        return "|Name|    " + str(self) + MwRecord.format_record_details(self, [
        ("\n|Type|", "type"),
        ("\n|Script|", "script"),
        ("\n|Weight|    {:.2f}", "weight"),
        ("\n|Value|", "value"),
        ("\n|Model|", "model"),
        ("\n|Icon|", "icon"),
        ("\n|Enchantment|", "enchantment"),
        ("\n|Enchanting|", "enchanting"),
        ("\n|Body Parts|", "body_parts")
        ])
    
    def __str__(self):
        return "{} [{}]".format(self.name, self.id)
    
    def compare(self, other):
        MwRecord.compare(self, other, ["model", "name", "type", "weight", "value", "enchantment", "script", "icon", "body_parts", "enchanting"])

class MwARMORBodyPart:
    def __str__(self):
        return "{} {} {}".format(self.type, self.male_name, self.female_name)