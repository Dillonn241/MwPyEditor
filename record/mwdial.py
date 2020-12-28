from mwrecord import MwRecord
import mwglobals

class MwDIAL(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
        self.infos = []
    
    def load(self):
        self.name = self.get_subrecord_string("NAME")
        self.type = mwglobals.DIAL_TYPES[self.get_subrecord_int("DATA", length=1, signed=False)]
    
    def save(self):
        self.set_subrecord_string(self.name, "NAME")
    
    def filter_infos(self, actor=None, race=None, class_=None, faction=None, cell=None, pc_faction=None):
        filtered_infos = []
        for info in self.infos:
            if actor != None and actor != info.actor:
                continue
            if race != None and race != info.race:
                continue
            if class_ != None and class_ != info.class_:
                continue
            if faction != None and faction != info.faction:
                continue
            if cell != None and cell != info.cell:
                continue
            if pc_faction != None and pc_faction != info.pc_faction:
                continue
            filtered_infos += [info]
        return filtered_infos
    
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