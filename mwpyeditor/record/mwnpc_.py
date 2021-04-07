import math

from mwpyeditor.core import mwglobals
from mwpyeditor.core.mwrecord import MwRecord


class MwNPC_(MwRecord):
    do_autocalc = False

    def __init__(self):
        MwRecord.__init__(self)
        self.id_ = ''
        self.animation_file = None
        self.name = None
        self.race = ''
        self.class_ = ''
        self.faction = ''
        self.head_model = ''
        self.hair_model = ''
        self.script = None
        self.level = 0
        self.attributes = []
        self.skills = []
        self.health = 0
        self.magicka = 0
        self.fatigue = 0
        self.disposition = 0
        self.reputation = 0
        self.faction_rank = 0
        self.barter_gold = 0
        self.female = False
        self.essential = False
        self.respawn = False
        self.autocalc = False
        self.white_blood = False
        self.gold_blood = False
        self.items = {}
        self.spells = []
        self.hello = 0
        self.fight = 0
        self.flee = 0
        self.alarm = 0
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
        self.destinations = []
        self.ai_packages = []

    def load(self):
        self.id_ = self.parse_string('NAME')
        self.animation_file = self.parse_string('MODL')
        self.name = self.parse_string('FNAM')
        self.race = self.parse_string('RNAM')
        self.class_ = self.parse_string('CNAM')
        self.faction = self.parse_string('ANAM')
        self.head_model = self.parse_string('BNAM')
        self.hair_model = self.parse_string('KNAM')
        self.script = self.parse_string('SCRI')
        self.level = self.parse_int('NPDT', length=2)

        if len(self.get_subrecord('NPDT').data) == 12:
            self.disposition = self.parse_uint('NPDT', start=2, length=1)
            self.reputation = self.parse_uint('NPDT', start=3, length=1)
            self.faction_rank = self.parse_uint('NPDT', start=4, length=1)
            self.barter_gold = self.parse_int('NPDT', start=8)
        else:
            self.attributes = [self.parse_uint('NPDT', start=2 + i, length=1)
                               for i in range(8)]  # len(mwglobals.ATTRIBUTES)

            self.skills = [self.parse_uint('NPDT', start=10 + i, length=1)
                           for i in range(27)]  # len(mwglobals.SKILLS)

            self.health = self.parse_uint('NPDT', start=38, length=2)
            self.magicka = self.parse_uint('NPDT', start=40, length=2)
            self.fatigue = self.parse_uint('NPDT', start=42, length=2)
            self.disposition = self.parse_uint('NPDT', start=44, length=1)
            self.reputation = self.parse_uint('NPDT', start=45, length=1)
            self.faction_rank = self.parse_uint('NPDT', start=46, length=1)
            self.barter_gold = self.parse_int('NPDT', start=48)

        flags = self.parse_int('FLAG')
        self.female = (flags & 0x1) == 0x1
        self.essential = (flags & 0x2) == 0x2
        self.respawn = (flags & 0x4) == 0x4
        self.autocalc = (flags & 0x10) == 0x10
        self.white_blood = (flags & 0x400) == 0x400
        self.gold_blood = (flags & 0x800) == 0x800

        self.items = {self.parse_string('NPCO', index=i, start=4, length=32):
                      self.parse_int('NPCO', index=i)
                      for i in range(self.num_subrecords('NPCO'))}

        self.spells = self.parse_string_array('NPCS')

        load_ai(self)

        if MwNPC_.do_autocalc and self.autocalc:
            self.autocalc_stats()

        mwglobals.object_ids[self.id_] = self

    def autocalc_stats(self):
        mw_race = mwglobals.object_ids[self.race]
        mw_class = mwglobals.object_ids[self.class_]
        self.attributes = []
        for attribute_id in range(8):  # len(mwglobals.ATTRIBUTES)
            base = mw_race.attribute_base_from_id(attribute_id, self.female)
            if attribute_id in mw_class.primary_attribute_ids:
                base += 10

            k = 0
            for mw_skill in mwglobals.records['SKIL']:
                if mw_skill.governing_attribute_id == attribute_id:
                    if mw_skill.id_ in mw_class.major_skill_ids:
                        k += 1
                    elif mw_skill.id_ in mw_class.minor_skill_ids:
                        k += 0.5
                    else:
                        k += 0.2
            self.attributes.append(round(base + k * (self.level - 1)))

        health_mult = 3
        if mw_class.specialization_id == 2:  # Combat
            health_mult += 2
        elif mw_class.specialization_id == 1:  # Stealth
            health_mult += 1
        if 5 in mw_class.primary_attribute_ids:  # Endurance
            health_mult += 1
        str_end_average = 0.5 * (self.attributes[0] + self.attributes[5])  # Strength + Endurance
        self.health = math.floor(str_end_average + health_mult * (self.level - 1))

        self.magicka = math.floor(2 * self.attributes[1])  # fNPCbaseMagickaMult * Intelligence
        # Strength + Willpower + Agility + Endurance
        self.fatigue = self.attributes[0] + self.attributes[2] + self.attributes[3] + self.attributes[5]

        self.skills = []
        for mw_skill in mwglobals.records['SKIL']:
            if mw_skill.id_ in mw_class.major_skill_ids:
                k = 1
                base = 30
            elif mw_skill.id_ in mw_class.minor_skill_ids:
                k = 1
                base = 15
            else:
                k = 0.1
                base = 5
            if mw_skill.specialization_id == mw_class.specialization_id:
                base += 5
                k += 0.5
            base += mw_race.skill_bonus_from_id(mw_skill.id_)
            self.skills.append(round(base + k * (self.level - 1)))

        if self.faction:
            self.reputation = 2 * (self.faction_rank + 1)  # 2 = iAutoRepFacMod
            # formula technically adds
            # iAutoRepLevMod [0] * (level - 1)
            # which is always 0
        else:
            self.reputation = 0

    def get_wiki_race(self):
        if self.race == "Dark Elf":
            return "Dunmer"
        if self.race == "High Elf":
            return "Altmer"
        if self.race == "Wood Elf":
            return "Bosmer"
        return self.race

    def get_wiki_class(self):
        classes = ["Alchemist", "Apothecary", "Bookseller", "Buoyant Armiger", "Clothier", "Enchanter", "Guard",
                   "Guild Guide", "Ordinator", "Pawnbroker", "Priest", "Savant", "Slave", "Smith", "Trader"]
        if self.class_ in classes:
            return self.class_ + " (class)"
        return self.class_

    def get_faction_rank_name(self):
        if self.faction and self.faction in mwglobals.object_ids:
            ranks = mwglobals.object_ids[self.faction].ranks
            if 0 <= self.faction_rank < len(ranks):
                return ranks[self.faction_rank].name

    def get_attribute(self, attribute_name):
        if attribute_name in mwglobals.ATTRIBUTES:
            attribute_id = mwglobals.ATTRIBUTES.index(attribute_name)
            return self.attributes[attribute_id]
    
    def get_attributes_dict(self):
        return {mwglobals.ATTRIBUTES[attribute_id]: self.attributes[attribute_id]
                for attribute_id in range(8)}

    def get_skill(self, skill_name):
        if skill_name in mwglobals.SKILLS:
            skill_id = mwglobals.SKILLS.index(skill_name)
            return self.skills[skill_id]
    
    def get_skills_dict(self):
        return {mwglobals.SKILLS[skill_id]: self.skills[skill_id]
                for skill_id in range(27)}

    def get_sex(self):
        return "Female" if self.female else "Male"

    def get_sex_template(self):
        return "{{F}}" if self.female else "{{M}}"

    def get_blood(self):
        if self.white_blood:
            return "Skeleton (White)"
        if self.gold_blood:
            return "Metal Sparks (Gold)"
        return "Default (Red)"

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

    def trained_skills(self):
        if self.service_training:
            skill_zip = [(x, self.skills[x]) for x in range(27)]
            return sorted(skill_zip, key=lambda x: x[1], reverse=True)[:3]
        return []

    def record_details(self):
        string = [MwRecord.format_record_details(self, [
            ("|Name|", '__str__'),
            ("\n|Script|", 'script'),
            ("\n|Race|", 'race'),
            ("\n|Sex|", 'sex'),
            ("\n|Class|", 'class'),
            ("\n|Level|", 'level'),
            ("\n|Faction|", 'faction', ''),
            ("\n|Faction Rank|", 'get_faction_rank_name', 0 if self.faction == '' else None),
            (" ({})", 'faction_rank'),
            ("\n|Essential|", 'essential', False),
            ("\n|Respawn|", 'respawn', False),
            ("\n|Head Model|", 'head_model'),
            ("\n|Hair Model|", 'hair_model'),
            ("\n|Animation File|", 'animation_file'),
            ("\n|Attributes|", 'get_attributes_dict'),
            ("\n|Skills|", 'get_skills_dict'),
            ("\n|Health|", 'health'),
            ("\n|Magicka|", 'magicka'),
            ("\n|Fatigue|", 'fatigue'),
            ("\n|Disposition|", 'disposition'),
            ("\n|Reputation|", 'reputation'),
            ("\n|Blood Texture|", 'get_blood', "Default (Red)"),
            ("\n|Auto Calculate Stats|", 'autocalc', False),
            ("\n|Items|", 'items', {}),
            ("\n|Spells|", 'spells', []),
            ("\n|Hello|", 'hello'),
            ("\n|Fight|", 'fight'),
            ("\n|Flee|", 'flee'),
            ("\n|Alarm|", 'alarm'),
            ("\n|Barter Gold|", 'barter_gold', 0),
            ("\n|Buys / Sells|", 'buys_sells', []),
            ("\n|Other Services|", 'other_services', [])
        ])]
        if len(self.destinations) > 0:
            string.append("\n|Travel Services|")
            for destination in self.destinations:
                string.append(f"\n{destination.record_details()}")
        if len(self.ai_packages) > 0:
            string.append("\n|AI Packages|")
            for ai_package in self.ai_packages:
                string.append(f"\n{ai_package.record_details()}")
        return ''.join(string)

    def __str__(self):
        return f"{self.name} [{self.id_}]"

    def diff(self, other):
        return MwRecord.diff(self, other, ['animation_file', 'name', 'race', 'class_', 'faction', 'head_model',
                                           'hair_model', 'script', 'level', 'get_attributes_dict', 'get_skills_dict',
                                           'health', 'magicka', 'fatigue', 'disposition', 'reputation', 'faction_rank',
                                           'barter_gold', 'female', 'essential', 'respawn', 'autocalc', 'white_blood',
                                           'gold_blood', 'spells', 'items', 'hello', 'fight', 'flee', 'alarm',
                                           'buys_sells', 'other_services', 'destinations', 'ai_packages'])


def load_ai(self):
    self.hello = self.parse_uint('AIDT', length=1)
    self.fight = self.parse_uint('AIDT', start=2, length=1)
    self.flee = self.parse_uint('AIDT', start=3, length=1)
    self.alarm = self.parse_uint('AIDT', start=4, length=1)
    ai_flags = self.parse_int('AIDT', start=8)
    if not ai_flags:
        ai_flags = 0x0
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

    self.destinations = []
    destination = None
    for subrecord in self.ordered_subrecords:
        if subrecord.record_type == 'DODT':
            destination = MwNPCDestination()
            destination.pos_x = subrecord.parse_float()
            destination.pos_y = subrecord.parse_float(start=4)
            destination.pos_z = subrecord.parse_float(start=8)
            destination.rot_x = subrecord.parse_float(start=12)
            destination.rot_y = subrecord.parse_float(start=16)
            destination.rot_z = subrecord.parse_float(start=20)
            self.destinations.append(destination)
        elif subrecord.record_type == 'DNAM':
            destination.cell = subrecord.parse_string()

    self.ai_packages = []
    ai_package = None
    for subrecord in self.ordered_subrecords:
        if subrecord.record_type == 'AI_A':
            ai_package = MwNPCAIPackage()
            ai_package.type = "Activate"
            ai_package.target = subrecord.parse_string(length=32)
            self.ai_packages.append(ai_package)
        elif subrecord.record_type == 'AI_E':
            ai_package = MwNPCAIPackage()
            ai_package.type = "Escort"
            ai_package.x = subrecord.parse_float()
            ai_package.y = subrecord.parse_float(start=4)
            ai_package.z = subrecord.parse_float(start=8)
            ai_package.duration = subrecord.parse_uint(start=12, length=2)
            ai_package.target = subrecord.parse_string(start=14, length=32)
            self.ai_packages.append(ai_package)
        elif subrecord.record_type == 'AI_F':
            ai_package = MwNPCAIPackage()
            ai_package.type = "Follow"
            ai_package.x = subrecord.parse_float()
            ai_package.y = subrecord.parse_float(start=4)
            ai_package.z = subrecord.parse_float(start=8)
            ai_package.duration = subrecord.parse_uint(start=12, length=2)
            ai_package.target = subrecord.parse_string(start=14, length=32)
            self.ai_packages.append(ai_package)
        elif subrecord.record_type == 'AI_T':
            ai_package = MwNPCAIPackage()
            ai_package.type = "Travel"
            ai_package.x = subrecord.parse_float()
            ai_package.y = subrecord.parse_float(start=4)
            ai_package.z = subrecord.parse_float(start=8)
            self.ai_packages.append(ai_package)
        elif subrecord.record_type == 'AI_W':
            ai_package = MwNPCAIPackage()
            ai_package.type = "Wander"
            ai_package.distance = subrecord.parse_uint(length=2)
            ai_package.duration = subrecord.parse_uint(start=2, length=2)
            ai_package.time_of_day = subrecord.parse_uint(start=4, length=1)
            ai_package.idles = []
            for i in range(8):
                ai_package.idles += [subrecord.parse_uint(start=5 + i, length=1)]
            self.ai_packages.append(ai_package)
        elif subrecord.record_type == 'CNDT':
            ai_package.cell = subrecord.parse_string()


class MwNPCDestination:
    def __init__(self):
        self.pos_x = None
        self.pos_y = None
        self.pos_z = None
        self.rot_x = None
        self.rot_y = None
        self.rot_z = None
        self.cell = None

    def record_details(self):
        return MwRecord.format_record_details(self, [
            ("|Position|    {:.3f}", 'pos_x'), (", {:.3f}", 'pos_y'), (", {:.3f}", 'pos_z'), (" [{:.3f}", 'rot_x'),
            (", {:.3f}", 'rot_y'), (", {:.3f}]", 'rot_z'), (" {}", '__str__')
        ])

    def __str__(self):
        if self.cell:
            return self.cell
        grid_x = math.floor(self.pos_x / 8192)
        grid_y = math.floor(self.pos_y / 8192)
        if (grid_x, grid_y) in mwglobals.exterior_cells:
            cell = mwglobals.exterior_cells[(grid_x, grid_y)]
            return str(cell)
        return f"Wilderness [{grid_x},{grid_y}]"

    def __repr__(self):
        return self.record_details()


class MwNPCAIPackage:
    def __init__(self):
        self.type = None
        self.target = None
        self.x = None
        self.y = None
        self.z = None
        self.cell = None
        self.distance = None
        self.duration = None
        self.time_of_day = None
        self.idles = None

    def record_details(self):
        details = [
            ("|Type|", 'type'),
            ("\n|Target|", 'target')
        ]
        if self.type == "Travel" or self.cell:
            details += [("\n|Position|    {:.3f}", 'x'), (", {:.3f}", 'y'), (", {:.3f}", 'z'), (" {}", 'cell')]
        details += [
            ("\n|Distance|", 'distance'),
            ("\n|Duration|", 'duration'),
            ("\n|Time of Day|", 'time_of_day'),
            ("\n|Idles|", 'idles')
        ]
        return MwRecord.format_record_details(self, details)

    def __str__(self):
        return self.type

    def __repr__(self):
        return self.record_details()
