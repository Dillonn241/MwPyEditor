import mwglobals
from mwrecord import MwRecord

class MwDIAL(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
        self.infos = []
    
    def load(self):
        self.name = self.get_subrecord_string("NAME")
        self.type = mwglobals.DIAL_TYPES[self.get_subrecord_int("DATA", length=1, signed=False)]
    
    def save(self):
        self.set_subrecord_string(self.name, "NAME")
    
    def filter_infos(self, actor="", race="", class_="", faction="", cell="", pc_faction=""):
        return [x for x in self.infos if x.filter(actor=actor, race=race, class_=class_, faction=faction, cell=cell, pc_faction=pc_faction)]
    
    def record_details(self):
        string = str(self)
        for info in self.infos:
            string += "\n\n" + info.record_details()
        return string
    
    def __str__(self):
        return "{} <{}>".format(self.name, self.type)
    
    def get_id(self):
        return str(self)
    
    def diff(self, other):
        MwRecord.diff(self, other)