from mwrecord import MwRecord
import mwglobals

class MwRACE(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
    
    def load(self):
        self.id = self.get_subrecord_string("NAME")
        self.name = self.get_subrecord_string("FNAM")
        
        self.skill_bonuses = {}
        for i in range(7):
            skill_id = self.get_subrecord_int("RADT", start=i * 8, length=4)
            if skill_id != -1:
                bonus = self.get_subrecord_int("RADT", start=4 + i * 8, length=4)
                self.skill_bonuses[mwglobals.SKILLS[skill_id]] = bonus
        self.male_attributes = {}
        self.female_attributes = {}
        for i in range(len(mwglobals.ATTRIBUTES)):
            attribute = mwglobals.ATTRIBUTES[i]
            male_value = self.get_subrecord_int("RADT", start=56 + i * 8, length=4)
            female_value = self.get_subrecord_int("RADT", start=60 + i * 8, length=4)
            self.male_attributes[attribute] = male_value
            self.female_attributes[attribute] = female_value
        self.male_height = self.get_subrecord_float("RADT", start=120, length=4)
        self.female_height = self.get_subrecord_float("RADT", start=124, length=4)
        self.male_weight = self.get_subrecord_float("RADT", start=128, length=4)
        self.female_weight = self.get_subrecord_float("RADT", start=132, length=4)
        
        flags = self.get_subrecord_int("RADT", start=136, length=4)
        self.playable = (flags & 0x1) == 0x1
        self.beast_race = (flags & 0x2) == 0x2
        
        self.specials = []
        for i in range(self.num_subrecords("NPCS")):
            self.specials += self.get_subrecord_string("NPCS", index=i)
        
        self.description = self.get_subrecord_string("DESC")
        mwglobals.object_ids[self.id] = self
    
    def get_skill_bonus(self, skill):
        if skill in self.skill_bonuses:
            return self.skill_bonuses[skill]
        return 0
    
    def get_sex_attribute(self, attribute, female):
        return self.female_attributes[attribute] if female else self.male_attributes[attribute]
    
    def get_height(self, female):
        return self.female_height if female else self.male_height
    
    def get_weight(self, female):
        return self.female_weight if female else self.male_weight
    
    def record_details(self):
        return "|Name|    " + str(self) + MwRecord.format_record_details(self, [
        ("\n|Skill Bonuses|", "skill_bonuses"),
        ("\n|Male Attributes|", "male_attributes"),
        ("\n|Female Attributes|", "female_attributes"),
        ("\n|Male Height|", "male_height"),
        ("\n|Female Height|", "female_height"),
        ("\n|Male Weight|", "male_weight"),
        ("\n|Female Weight|", "female_weight"),
        ("\n|Playable|", "playable", False),
        ("\n|Beast Race|", "beast_race", False),
        ("\n|Specials|", "specials", []),
        ("\n|Description|", "description")
        ])
    
    def __str__(self):
        return "{} [{}]".format(self.name, self.id)
    
    def diff(self, other):
        MwRecord.diff(self, other, ["name", "skill_bonuses", "male_attributes", "female_attributes", "male_height", "female_height", "male_weight", "female_weight", "playable", "beast_race", "specials", "description"])