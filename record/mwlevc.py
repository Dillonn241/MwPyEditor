from mwrecord import MwRecord
import mwglobals
from record.mwlevi import MwLEVIItem

class MwLEVC(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
    
    def load(self):
        self.id = self.get_subrecord_string("NAME")
        self.calc_less_than_pc_level = self.get_subrecord_int("DATA", start=0, length=1) == 1
        self.chance_none = self.get_subrecord_int("NNAM")
        self.creatures = []
        for i in range(self.num_subrecords("CNAM")):
            creature = MwLEVIItem()
            creature.id = self.get_subrecord_string("CNAM", index=i)
            creature.level = self.get_subrecord_int("INTV", index=i)
            self.creatures += [creature]
        mwglobals.object_ids[self.id] = self
    
    def record_details(self):
        return MwRecord.format_record_details(self, [
        ("|ID|", "id"),
        ("\n|Calculate from all levels <= PC's level|", "calc_less_than_pc_level", False),
        ("\n|Chance None|", "chance_none"),
        ("\n|Creatures|", "creatures", [])
        ])
    
    def __str__(self):
        return self.id
    
    def diff(self, other):
        MwRecord.diff(self, other, ["calc_less_than_pc_level", "chance_none"])
        
        creature_details1 = []
        creature_details2 = []
        for creature in self.creatures:
            creature_details1 += [str(creature)]
        for creature in other.creatures:
            creature_details2 += [str(creature)]
        
        for creature2 in creature_details2:
            if creature2 not in creature_details1:
                print(str(self) + ": Added", creature2)
        
        for creature1 in creature_details1:
            if creature1 not in creature_details2:
                print(str(self) + ": Removed", creature1)