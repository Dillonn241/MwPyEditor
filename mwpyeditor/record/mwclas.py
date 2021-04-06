from mwpyeditor.core import mwglobals
from mwpyeditor.core.mwrecord import MwRecord


class MwCLAS(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
        self.id_ = ''
        self.name = ''
        self.primary_attribute_ids = []
        self.specialization_id = []
        self.minor_skill_ids = []
        self.major_skill_ids = []
        self.playable = False
        self.service_weapons = False
        self.service_armor = False
        self.service_clothing = False
        self.service_books = False
        self.service_ingredients = False
        self.service_picks = False
        self.service_probes = False
        self.service_lights = False
        self.service_apparatus = False
        self.service_repair_items = False
        self.service_miscellaneous = False
        self.service_spells = False
        self.service_magic_items = False
        self.service_potions = False
        self.service_training = False
        self.service_spellmaking = False
        self.service_enchanting = False
        self.service_repair = False
        self.description = None

    def load(self):
        self.id_ = self.parse_string('NAME')
        self.name = self.parse_string('FNAM')

        self.primary_attribute_ids = [self.parse_uint('CLDT'),
                                      self.parse_uint('CLDT', start=4)]
        self.specialization_id = self.parse_uint('CLDT', start=8)

        self.minor_skill_ids = []
        self.major_skill_ids = []
        for i in range(5):
            self.minor_skill_ids.append(self.parse_uint('CLDT', start=12 + 8 * i))
            self.major_skill_ids.append(self.parse_uint('CLDT', start=16 + 8 * i))

        flags = self.parse_uint('CLDT', start=52)
        self.playable = (flags & 0x1) == 0x1
        ai_flags = self.parse_uint('CLDT', start=56)
        self.service_weapons = (ai_flags & 0x1) == 0x1
        self.service_armor = (ai_flags & 0x2) == 0x2
        self.service_clothing = (ai_flags & 0x4) == 0x4
        self.service_books = (ai_flags & 0x8) == 0x8
        self.service_ingredients = (ai_flags & 0x10) == 0x10
        self.service_picks = (ai_flags & 0x20) == 0x20
        self.service_probes = (ai_flags & 0x40) == 0x40
        self.service_lights = (ai_flags & 0x80) == 0x80
        self.service_apparatus = (ai_flags & 0x100) == 0x100
        self.service_repair_items = (ai_flags & 0x200) == 0x200
        self.service_miscellaneous = (ai_flags & 0x400) == 0x400
        self.service_spells = (ai_flags & 0x800) == 0x800
        self.service_magic_items = (ai_flags & 0x1000) == 0x1000
        self.service_potions = (ai_flags & 0x2000) == 0x2000
        self.service_training = (ai_flags & 0x4000) == 0x4000
        self.service_spellmaking = (ai_flags & 0x8000) == 0x8000
        self.service_enchanting = (ai_flags & 0x10000) == 0x10000
        self.service_repair = (ai_flags & 0x20000) == 0x20000

        self.description = self.parse_string('DESC')

        mwglobals.object_ids[self.id_] = self

    def get_primary_attributes(self):
        return [mwglobals.ATTRIBUTES[x] for x in self.primary_attribute_ids]

    def set_primary_attributes(self, array):
        self.primary_attribute_ids = [mwglobals.ATTRIBUTES.index(x) if x in mwglobals.ATTRIBUTES else 0 for x in array]

    def get_specialization(self):
        return mwglobals.SPECIALIZATIONS[self.specialization_id]

    def set_specialization(self, value):
        if value in mwglobals.SPECIALIZATIONS:
            self.specialization_id = mwglobals.SPECIALIZATIONS.index(value)

    def get_minor_skills(self):
        return [mwglobals.SKILLS[x] for x in self.minor_skill_ids]

    def set_minor_skills(self, array):
        self.minor_skill_ids = [mwglobals.SKILLS.index(x) if x in mwglobals.SKILLS else 0 for x in array]

    def get_major_skills(self):
        return [mwglobals.SKILLS[x] for x in self.major_skill_ids]

    def set_major_skills(self, array):
        self.major_skill_ids = [mwglobals.SKILLS.index(x) if x in mwglobals.SKILLS else 0 for x in array]

    def buys_sells(self):
        types = []
        if self.service_weapons:
            types.append('WEAP')
        if self.service_armor:
            types.append('ARMO')
        if self.service_clothing:
            types.append('CLOT')
        if self.service_books:
            types.append('BOOK')
        if self.service_ingredients:
            types.append('INGR')
        if self.service_picks:
            types.append('LOCK')
        if self.service_probes:
            types.append('PROB')
        if self.service_lights:
            types.append('LIGH')
        if self.service_apparatus:
            types.append('APPA')
        if self.service_repair_items:
            types.append('REPA')
        if self.service_miscellaneous:
            types.append('MISC')
        if self.service_potions:
            types.append('ALCH')
        if self.service_magic_items:
            types.append("Magic Items")
        return types

    def other_services(self):
        types = []
        if self.service_training:
            types.append("Training")
        if self.service_spellmaking:
            types.append("Spellmaking")
        if self.service_enchanting:
            types.append("Enchanting")
        if self.service_repair:
            types.append("Repair")
        return types

    def record_details(self):
        return MwRecord.format_record_details(self, [
            ("|Name|", '__str__'),
            ("\n|Primary Attributes|", 'get_primary_attributes'),
            ("\n|Specialization|", 'get_specialization'),
            ("\n|Major Skills|", 'get_major_skills'),
            ("\n|Minor Skills|", 'get_minor_skills'),
            ("\n|Description|", 'description'),
            ("\n|Playable|", 'playable', False),
            ("\n|Buys / Sells|", 'buys_sells', []),
            ("\n|Other Services|", 'other_services', [])
        ])

    def __str__(self):
        return f"{self.name} [{self.id_}]"

    def diff(self, other):
        return MwRecord.diff(self, other, ['name', 'get_primary_attributes', 'get_specialization', 'get_minor_skills',
                                           'get_major_skills', 'playable', 'buys_sells', 'other_services',
                                           'description'])
