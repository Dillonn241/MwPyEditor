from mwrecord import MwRecord


class MwSSCR(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
    
    def load(self):
        self.id = self.get_subrecord_string("NAME")
    
    def record_details(self):
        return MwRecord.format_record_details(self, [
            ("|ID|", "id")
        ])
    
    def __str__(self):
        return self.id
    
    def diff(self, other):
        MwRecord.diff(self, other)
