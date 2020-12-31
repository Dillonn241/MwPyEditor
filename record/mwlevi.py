from mwrecord import MwRecord
import mwglobals

class MwLEVI(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
    
    def load(self):
        self.id = self.get_subrecord_string("NAME")
        self.calc_less_than_pc_level = self.get_subrecord_int("DATA", start=0, length=1) == 1
        self.calc_each_item = self.get_subrecord_int("DATA", start=1, length=1) == 1
        self.chance_none = self.get_subrecord_int("NNAM")
        self.items = []
        for i in range(self.num_subrecords("INAM")):
            item = MwLEVIItem()
            item.id = self.get_subrecord_string("INAM", index=i)
            item.level = self.get_subrecord_int("INTV", index=i)
            self.items += [item]
        mwglobals.object_ids[self.id] = self
    
    def record_details(self):
        return MwRecord.format_record_details(self, [
        ("|ID|", "id"),
        ("\n|Calculate from all levels <= PC's level|", "calc_less_than_pc_level", False),
        ("\n|Calculate for each item in count|", "calc_each_item", False),
        ("\n|Chance None|", "chance_none"),
        ("\n|Items|", "items", [])
        ])
    
    def __str__(self):
        return self.id
    
    def diff(self, other):
        MwRecord.diff(self, other, ["calc_less_than_pc_level", "calc_each_item", "chance_none"])
        
        item_details1 = []
        item_details2 = []
        for item in self.items:
            item_details1 += [str(item)]
        for item in other.items:
            item_details2 += [str(item)]
        
        for item2 in item_details2:
            if item2 not in item_details1:
                print(str(self) + ": Added", item2)
        
        for item1 in item_details1:
            if item1 not in item_details2:
                print(str(self) + ": Removed", item1)

class MwLEVIItem:
    def __str__(self):
        return "{} (Lvl {})".format(mwglobals.readable_object(self.id), self.level)
    
    def __repr__(self):
        return str(self)