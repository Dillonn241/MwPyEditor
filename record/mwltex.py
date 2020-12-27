from mwrecord import MwRecord

class MwLTEX(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
    
    def load(self):
        self.id = self.get_subrecord_string("NAME")
        self.index = self.get_subrecord_int("INTV")
        self.texture = self.get_subrecord_string("DATA")
    
    def record_details(self):
        return MwRecord.format_record_details(self, [
        ("|ID|", "id"),
        ("\n|Index|", "index"),
        ("\n|Texture|", "texture")
        ])
    
    def __str__(self):
        return self.id
    
    def compare(self, other):
        MwRecord.compare(self, other, ["index", "texture"])