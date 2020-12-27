from mwrecord import MwRecord
import mwglobals

class MwSKIL(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
    
    def load(self):
        self.name = mwglobals.SKILLS[self.get_subrecord_int("INDX")]
        self.governing_attribute = mwglobals.ATTRIBUTES[self.get_subrecord_int("SKDT", start=0, length=4)]
        self.specialization = mwglobals.SPECIALIZATIONS[self.get_subrecord_int("SKDT", start=4, length=4)]
        self.use_values = []
        for i in range(4):
            self.use_values += [self.get_subrecord_float("SKDT", start=8 + i * 4, length=4)]
        self.description = self.get_subrecord_string("DESC")
    
    def record_details(self):
        return MwRecord.format_record_details(self, [
        ("|Name|", "name"),
        ("\n|Governing Attribute|", "governing_attribute"),
        ("\n|Specialization|", "specialization"),
        ("\n|Use Values|", "use_values"),
        ("\n|Description|", "description")
        ])
    
    def __str__(self):
        return self.name
    
    def get_id(self):
        return self.name
    
    def compare(self, other):
        MwRecord.compare(self, other, ["governing_attribute", "specialization", "use_values", "description"])