from mwrecord import MwRecord
import mwglobals

class MwINGR(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
    
    def load(self):
        self.id = self.get_subrecord_string("NAME")
        self.model = self.get_subrecord_string("MODL")
        self.name = self.get_subrecord_string("FNAM")
        self.weight = self.get_subrecord_float("IRDT", start=0, length=4)
        self.value = self.get_subrecord_int("IRDT", start=4, length=4)
        self.effects = []
        self.skill_attributes = []
        for i in range(4):
            effect_id = self.get_subrecord_int("IRDT", start=8 + i * 4, length=4)
            self.effects += [None]
            self.skill_attributes += [None]
            if effect_id != -1:
                self.effects[i] = mwglobals.MAGIC_NAMES[effect_id]
                skill_id = self.get_subrecord_int("IRDT", start=24 + i * 4, length=4)
                if skill_id != -1:
                    self.skill_attributes[i] = mwglobals.SKILLS[skill_id]
                else:
                    attribute_id = self.get_subrecord_int("IRDT", start=40 + i * 4, length=4)
                    if attribute_id != -1:
                        self.skill_attributes[i] = mwglobals.ATTRIBUTES[attribute_id]
        self.script = self.get_subrecord_string("SCRI")
        self.icon = self.get_subrecord_string("ITEX")
        mwglobals.object_ids[self.id] = self
    
    def record_details(self):
        string = "|Name|    " + str(self) + MwRecord.format_record_details(self, [
        ("\n|Script|", "script"),
        ("\n|Weight|    {:.2f}", "weight"),
        ("\n|Value|", "value"),
        ("\n|Model|", "model"),
        ("\n|Icon|", "icon"),
        ])
        for i in range(4):
            if self.effects[i] != None:
                string += "\n|Effect " + str(i + 1) + "|    " + self.effects[i]
                if self.skill_attributes[i] != None:
                    string += " " + str(self.skill_attributes[i])
        return string
    
    def __str__(self):
        return "{} [{}]".format(self.name, self.id)
    
    def diff(self, other):
        MwRecord.diff(self, other, ["model", "name", "weight", "value", "effects", "skill_attributes", "script", "icon"])