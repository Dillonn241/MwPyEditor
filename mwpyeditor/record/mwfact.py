from mwpyeditor.core import mwglobals
from mwpyeditor.core.mwrecord import MwRecord


class MwFACT(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
        self.id_ = ''
        self.name = ''
        self.favored_attribute_ids = []
        self.ranks = []
        self.favored_skill_ids = []
        self.hidden = False
        self.faction_reactions = []

    def load(self):
        self.id_ = self.parse_string('NAME')
        self.name = self.parse_string('FNAM')

        self.favored_attribute_ids = [self.parse_uint('FADT'),
                                      self.parse_uint('FADT', start=4)]

        self.ranks = [MwFACTRank(self.parse_string('RNAM', index=i),  # name
                                 [self.parse_uint('FADT', start=8 + 20 * i),  # attribute 1
                                  self.parse_uint('FADT', start=12 + 20 * i)],  # attribute 2
                                 [self.parse_uint('FADT', start=16 + 20 * i),  # skill 1
                                  self.parse_uint('FADT', start=20 + 20 * i)],  # skill 2
                                 self.parse_uint('FADT', start=24 + 20 * i))  # fact rep
                      for i in range(self.num_subrecords('RNAM'))]

        self.favored_skill_ids = [self.parse_int('FADT', start=208 + i * 4)
                                  for i in range(7)]

        flags = self.parse_uint('FADT', start=236)
        self.hidden = (flags & 0x1) == 0x1

        self.faction_reactions = {self.parse_string('ANAM', index=i):
                                  self.parse_int('INTV', index=i)
                                  for i in range(self.num_subrecords('ANAM'))}

        mwglobals.object_ids[self.id_] = self

    def get_favored_attributes(self):
        return [mwglobals.ATTRIBUTES[x] for x in self.favored_attribute_ids]

    def set_favored_attributes(self, array):
        self.favored_attribute_ids = [mwglobals.ATTRIBUTES.index(x) if x in mwglobals.ATTRIBUTES else 0 for x in array]

    def get_favored_skills(self):
        return [mwglobals.SKILLS[x] if x != -1 else "" for x in self.favored_skill_ids]

    def set_favored_skills(self, array):
        self.favored_skill_ids = [mwglobals.SKILLS.index(x) if x in mwglobals.SKILLS else -1 for x in array]

    def record_details(self):
        string = [MwRecord.format_record_details(self, [
            ("|Name|", "__str__"),
            ("\n|Hidden from PC|", 'hidden', False),
            ("\n|Favored Attributes|", 'get_favored_attributes'),
            ("\n|Favored Skills|", 'get_favored_skills'),
            ("\n|Faction Reactions|", 'faction_reactions', {})
        ])]
        if len(self.ranks) > 0:
            string.append("\n|Ranks|    Rank Name (Attrib 1, Attrib 2, Pri Skill, Fav Skill, Fact Rep)")
            for rank in self.ranks:
                string.append(f"\n{rank.record_details()}")
        return ''.join(string)

    def __str__(self):
        return f"{self.name} [{self.id_}]"

    def diff(self, other):
        return MwRecord.diff(self, other, ['name', 'get_favored_attributes', 'ranks', 'get_favored_skills', 'hidden',
                                           'faction_reactions'])


class MwFACTRank:
    def __init__(self, name, attributes, skills, fact_rep):
        self.name = name
        self.attributes = attributes
        self.skills = skills
        self.fact_rep = fact_rep

    def record_details(self):
        return f"""{self.name} ({self.attributes[0]}, {self.attributes[1]}, {self.skills[0]}, {self.skills[1]},
                {self.fact_rep})"""

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.record_details()
