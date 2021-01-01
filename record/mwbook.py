import mwglobals
from mwrecord import MwRecord

class MwBOOK(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
    
    def load(self):
        self.id = self.get_subrecord_string("NAME")
        self.model = self.get_subrecord_string("MODL")
        self.name = self.get_subrecord_string("FNAM")
        self.weight = self.get_subrecord_float("BKDT", start=0, length=4)
        self.value = self.get_subrecord_int("BKDT", start=4, length=4)
        self.scroll = self.get_subrecord_int("BKDT", start=8, length=4) == 1
        skill_id = self.get_subrecord_int("BKDT", start=12, length=4)
        self.skill = mwglobals.SKILLS[skill_id] if skill_id != -1 else None
        self.enchantment = self.get_subrecord_int("BKDT", start=16, length=4)
        self.icon = self.get_subrecord_string("ITEX")
        self.script = self.get_subrecord_string("SCRI")
        self.enchanting = self.get_subrecord_string("ENAM")
        self.text = self.get_subrecord_string("TEXT")
        mwglobals.object_ids[self.id] = self
    
    def record_details(self):
        return "|Name|    " + str(self) + MwRecord.format_record_details(self, [
        ("\n|Script|", "script"),
        ("\n|Weight|    {:.2f}", "weight"),
        ("\n|Value|", "value"),
        ("\n|Skill|", "skill"),
        ("\n|Model|", "model"),
        ("\n|Icon|", "icon"),
        ("\n|Scroll|", "scroll", False),
        ("\n|Enchantment|", "enchantment"),
        ("\n|Enchanting|", "enchanting"),
        ("\n|Text|", "text")
        ])
    
    def __str__(self):
        return "{} [{}]".format(self.name, self.id)
    
    def diff(self, other):
        MwRecord.diff(self, other, ["model", "name", "weight", "value", "scroll", "skill", "enchantment", "icon", "script", "enchanting", "text"])