from core import mwglobals
from core.mwrecord import MwRecord
from record.mwnpc_ import load_ai


class MwCREA(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
        self.id_ = ''
        self.animation_file = ''
        self.sound_gen_creature = None
        self.name = None
        self.script = None
        self.type_id = 0
        self.level = 0
        self.attributes = []
        self.health = 0
        self.spell_pts = 0
        self.fatigue = 0
        self.soul = 0
        self.combat = 0
        self.magic = 0
        self.stealth = 0
        self.attack1_min = 0
        self.attack1_max = 0
        self.attack2_min = 0
        self.attack2_max = 0
        self.attack3_min = 0
        self.attack3_max = 0
        self.barter_gold = 0
        self.biped = False
        self.respawn = False
        self.weapon_and_shield = False
        self.none = False
        self.swims = False
        self.flies = False
        self.walks = False
        self.essential = False
        self.white_blood = False
        self.gold_blood = False
        self.scale = None
        self.items = []
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
        self.sound_gen_creature = self.parse_string('CNAM')
        self.name = self.parse_string('FNAM')
        self.script = self.parse_string('SCRI')

        self.type_id = self.parse_uint('NPDT')
        self.level = self.parse_uint('NPDT', start=4)

        self.attributes = [self.parse_uint('NPDT', start=8 + 4 * i)
                           for i in range(8)]  # len(mwglobals.ATTRIBUTES)

        self.health = self.parse_uint('NPDT', start=40)
        self.spell_pts = self.parse_uint('NPDT', start=44)
        self.fatigue = self.parse_uint('NPDT', start=48)
        self.soul = self.parse_uint('NPDT', start=52)
        self.combat = self.parse_uint('NPDT', start=56)
        self.magic = self.parse_uint('NPDT', start=60)
        self.stealth = self.parse_uint('NPDT', start=64)
        self.attack1_min = self.parse_uint('NPDT', start=68)
        self.attack1_max = self.parse_uint('NPDT', start=72)
        self.attack2_min = self.parse_uint('NPDT', start=76)
        self.attack2_max = self.parse_uint('NPDT', start=80)
        self.attack3_min = self.parse_uint('NPDT', start=84)
        self.attack3_max = self.parse_uint('NPDT', start=88)
        self.barter_gold = self.parse_uint('NPDT', start=92)

        flags = self.parse_uint('FLAG')
        self.biped = (flags & 0x1) == 0x1
        self.respawn = (flags & 0x2) == 0x2
        self.weapon_and_shield = (flags & 0x4) == 0x4
        self.none = (flags & 0x8) == 0x8
        self.swims = (flags & 0x10) == 0x10
        self.flies = (flags & 0x20) == 0x20
        self.walks = (flags & 0x40) == 0x40
        if (flags & 0x48) == 0x48:
            self.none = False
        self.essential = (flags & 0x80) == 0x80
        self.white_blood = (flags & 0x400) == 0x400
        self.gold_blood = (flags & 0x800) == 0x800

        self.scale = self.parse_float('XSCL')

        self.items = {self.parse_string('NPCO', index=i, start=4, length=32):
                      self.parse_uint('NPCO', index=i)
                      for i in range(self.num_subrecords('NPCO'))}

        self.spells = self.parse_string_array('NPCS')

        load_ai(self)

        mwglobals.object_ids[self.id_] = self

    def get_type(self):
        if 0 <= self.type_id < len(mwglobals.CREA_TYPES):
            return mwglobals.CREA_TYPES[self.type_id]

    def set_type(self, value):
        if value in mwglobals.CREA_TYPES:
            self.type_id = mwglobals.CREA_TYPES.index(value)

    def get_attribute(self, attribute_name):
        if attribute_name in mwglobals.ATTRIBUTES:
            attribute_id = mwglobals.ATTRIBUTES.index(attribute_name)
            return self.attributes[attribute_id]

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

    def record_details(self):
        string = [MwRecord.format_record_details(self, [
            ("|Name|", '__str__'),
            ("\n|Animation File|", 'animation_file'),
            ("\n|Sound Gen Creature|", 'sound_gen_creature'),
            ("\n|Script|", 'script'),
            ("\n|Type|", 'get_type'),
            ("\n|Level|", 'level'),
            ("\n|Attributes|", 'attributes'),
            ("\n|Health|", 'health'),
            ("\n|Spell Pts|", 'spell_pts'),
            ("\n|Fatigue|", 'fatigue'),
            ("\n|Soul|", 'soul'),
            ("\n|Combat|", 'combat'),
            ("\n|Magic|", 'magic'),
            ("\n|Stealth|", 'stealth'),
            ("\n|Attack 1|", 'attack1_min'), (" - {}", 'attack1_max'),
            ("\n|Attack 2|", 'attack2_min'), (" - {}", 'attack2_max'),
            ("\n|Attack 3|", 'attack3_min'), (" - {}", 'attack3_max'),
            ("\n|Barter Gold|", 'barter_gold', 0),
            ("\n|Biped|", 'biped', False),
            ("\n|Respawn|", 'respawn', False),
            ("\n|Weapon & Shield|", 'weapon_and_shield', False),
            ("\n|None|", 'none', False),
            ("\n|Swims|", 'swims', False),
            ("\n|Flies|", 'flies', False),
            ("\n|Walks|", 'walks', False),
            ("\n|Essential|", 'essential', False),
            ("\n|Blood Texture|", 'get_blood', "Default (Red)"),
            ("\n|Scale|    {:.2f}", 'scale'),
            ("\n|Items|", 'items', {}),
            ("\n|Spells|", 'spells', []),
            ("\n|Hello|", 'hello'), ("    |Fight|", 'fight'), ("    |Flee|", 'flee'), ("    |Alarm|", 'alarm'),
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
        return MwRecord.diff(self, other, ['animation_file', 'sound_gen_creature', 'name', 'script', 'get_type',
                                           'level', 'attributes', 'health', 'spell_pts', 'fatigue', 'soul', 'combat',
                                           'magic', 'stealth', 'attack1_min', 'attack1_max', 'attack2_min',
                                           'attack2_max', 'attack3_min', 'attack3_max', 'barter_gold', 'biped',
                                           'respawn', 'weapon_and_shield', 'none', 'swims', 'flies', 'walks',
                                           'essential', 'white_blood', 'gold_blood', 'scale', 'items', 'spells',
                                           'hello', 'fight', 'flee', 'alarm', 'service_ingredients', 'service_picks',
                                           'service_probes', 'service_lights', 'service_apparatus',
                                           'service_repair_items', 'service_miscellaneous', 'service_spells',
                                           'service_magic_items', 'service_potions', 'service_training',
                                           'service_spellmaking', 'service_enchanting', 'service_repair',
                                           'destinations', 'ai_packages'])
