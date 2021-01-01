import mwglobals
from mwrecord import MwRecord

class MwFACT(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
    
    def load(self):
        self.id = self.get_subrecord_string("NAME")
        self.name = self.get_subrecord_string("FNAM")
        
        self.ranks = []
        for i in range(self.num_subrecords("RNAM")):
            faction_rank = MwFACTRank()
            faction_rank.name = self.get_subrecord_string("RNAM", index=i)
            faction_rank.attributes = []
            faction_rank.attributes += [self.get_subrecord_int("FADT", start=8 + 20 * i, length=4)]
            faction_rank.attributes += [self.get_subrecord_int("FADT", start=12 + 20 * i, length=4)]
            faction_rank.skills = []
            faction_rank.skills += [self.get_subrecord_int("FADT", start=16 + 20 * i, length=4)]
            faction_rank.skills += [self.get_subrecord_int("FADT", start=20 + 20 * i, length=4)]
            faction_rank.fact_rep = self.get_subrecord_int("FADT", start=24 + 20 * i, length=4)
            self.ranks += [faction_rank]
        
        self.favored_attributes = []
        self.favored_attributes += [mwglobals.ATTRIBUTES[self.get_subrecord_int("FADT", start=0, length=4)]]
        self.favored_attributes += [mwglobals.ATTRIBUTES[self.get_subrecord_int("FADT", start=4, length=4)]]
        self.favored_skills = []
        for i in range(7):
            skill_id = self.get_subrecord_int("FADT", start=208 + i * 4, length=4)
            if skill_id < len(mwglobals.SKILLS):
                self.favored_skills += [mwglobals.SKILLS[skill_id]]
        
        flags = self.get_subrecord_int("FADT", start=236, length=4)
        self.hidden = (flags & 0x1) == 0x1
        
        self.faction_reactions = {}
        for i in range(self.num_subrecords("ANAM")):
            reaction_id = self.get_subrecord_string("ANAM", index=i)
            reaction_value = self.get_subrecord_int("INTV", index=i)
            self.faction_reactions[reaction_id] = reaction_value
        
        mwglobals.object_ids[self.id] = self
    
    def record_details(self):
        string = "|Name|    " + str(self) + MwRecord.format_record_details(self, [
        ("\n|Hidden from PC|", "hidden", False),
        ("\n|Favored Attributes|", "favored_attributes"),
        ("\n|Favored Skills|", "favored_skills"),
        ("\n|Faction Reactions|", "faction_reactions", {})
        ])
        if len(self.ranks) > 0:
            longest = 0
            for rank in self.ranks:
                length = len(rank.name)
                if length > longest:
                    longest = length
            longest += 2
            space = " " * (longest - 9)
            string += "\n|Ranks|\nRank Name" + space + "Attrib 1  Attrib 2  Pri Skill  Fav Skill  Fact Rep"
            for rank in self.ranks:
                string += "\n" + rank.record_details(longest=longest)
        return string
    
    def __str__(self):
        return "{} [{}]".format(self.name, self.id)
    
    def diff(self, other):
        MwRecord.diff(self, other, ["name", "ranks", "favored_attributes", "favored_skills", "hidden", "faction_reactions"])

class MwFACTRank:
    def record_details(self, longest=33):
        space = " " * (longest - len(self.name))
        return self.name + space + "{:^8}  {:^8}  {:^9}  {:^9}  {:^8}".format(self.attributes[0], self.attributes[1], self.skills[0], self.skills[1], self.fact_rep)
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.record_details()