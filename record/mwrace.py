from core import mwglobals
from core.mwrecord import MwRecord


class MwRACE(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
        self.id_ = ''
        self.name = ''
        self.skill_bonus_ids = []
        self.male_attributes = []
        self.female_attributes = []
        self.male_height = 0.0
        self.female_height = 0.0
        self.male_weight = 0.0
        self.female_weight = 0.0
        self.playable = False
        self.beast_race = False
        self.specials = []
        self.description = None

    def load(self):
        self.id_ = self.parse_string('NAME')
        self.name = self.parse_string('FNAM')
        self.skill_bonus_ids = [(self.parse_int('RADT', start=i * 8),
                                 self.parse_int('RADT', start=4 + i * 8))
                                for i in range(7)]

        self.male_attributes = []
        self.female_attributes = []
        for i in range(8):  # len(mwglobals.ATTRIBUTES)
            self.male_attributes.append(self.parse_uint('RADT', start=56 + i * 8))
            self.female_attributes.append(self.parse_uint('RADT', start=60 + i * 8))

        self.male_height = self.parse_float('RADT', start=120)
        self.female_height = self.parse_float('RADT', start=124)
        self.male_weight = self.parse_float('RADT', start=128)
        self.female_weight = self.parse_float('RADT', start=132)
        flags = self.parse_uint('RADT', start=136)
        self.playable = (flags & 0x1) == 0x1
        self.beast_race = (flags & 0x2) == 0x2

        self.specials = self.parse_string_array('NPCS')
        self.description = self.parse_string('DESC')

        mwglobals.object_ids[self.id_] = self

    def get_skill_bonuses(self):
        return [self.get_skill_bonus(i) for i in range(len(self.skill_bonus_ids))]

    def set_skill_bonuses(self, skill_tuples):
        for i in range(len(self.skill_bonus_ids)):
            self.set_skill_bonus(skill_tuples[i], i)

    def get_skill_bonus(self, index):
        skill_id = self.skill_bonus_ids[index][0]
        skill_name = mwglobals.SKILLS[skill_id] if skill_id != -1 else None
        skill_bonus = self.skill_bonus_ids[index][1]
        return skill_name, skill_bonus

    def set_skill_bonus(self, skill_tuple, index):
        skill_id = mwglobals.SKILLS.index(skill_tuple[0]) if skill_tuple[0] in mwglobals.SKILLS else -1
        self.skill_bonus_ids[index] = (skill_id, skill_tuple[1])

    def skill_bonus_from_id(self, skill_id):
        for skill_tuple in self.skill_bonus_ids:
            if skill_tuple[0] == skill_id:
                return skill_tuple[1]
        return 0

    def skill_bonus_from_name(self, skill_name):
        if skill_name in mwglobals.SKILLS:
            skill_id = mwglobals.SKILLS.index(skill_name)
            return self.get_skill_bonus(skill_id)
        return 0

    def attribute_base_from_id(self, attribute_id, female):
        return self.female_attributes[attribute_id] if female else self.male_attributes[attribute_id]

    def attribute_base_from_name(self, attribute_name, female):
        if attribute_name in mwglobals.ATTRIBUTES:
            attribute_id = mwglobals.ATTRIBUTES.index(attribute_name)
            return self.attribute_base_from_id(attribute_id, female)

    def get_height(self, female):
        return self.female_height if female else self.male_height

    def get_weight(self, female):
        return self.female_weight if female else self.male_weight

    def record_details(self):
        return MwRecord.format_record_details(self, [
            ("|Name|", '__str__'),
            ("\n|Skill Bonuses|", 'get_skill_bonuses'),
            ("\n|Male Attributes|", 'male_attributes'),
            ("\n|Female Attributes|", 'female_attributes'),
            ("\n|Male Height|", 'male_height'),
            ("\n|Female Height|", 'female_height'),
            ("\n|Male Weight|", 'male_weight'),
            ("\n|Female Weight|", 'female_weight'),
            ("\n|Playable|", 'playable', False),
            ("\n|Beast Race|", 'beast_race', False),
            ("\n|Specials|", 'specials', []),
            ("\n|Description|", 'description')
        ])

    def __str__(self):
        return f"{self.name} [{self.id_}]"

    def diff(self, other):
        return MwRecord.diff(self, other, ['name', 'get_skill_bonuses', 'male_attributes', 'female_attributes',
                                           'male_height', 'female_height', 'male_weight', 'female_weight', 'playable',
                                           'beast_race', 'specials', 'description'])
