import mwglobals
from mwrecord import MwRecord
from record.mwnpc_ import load_ai, MwNPCDestination, MwNPCAIPackage

CREA_TYPES = ["Creature", "Daedra", "Undead", "Humanoid"]


class MwCREA(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)

    def load(self):
        self.id = self.get_subrecord_string("NAME")
        self.animation_file = self.get_subrecord_string("MODL")
        self.sound_gen_creature = self.get_subrecord_string("CNAM")
        self.name = self.get_subrecord_string("FNAM")
        self.script = self.get_subrecord_string("SCRI")
        self.type = mwglobals.CREA_TYPES[self.get_subrecord_int("NPDT", start=0, length=4)]
        self.level = self.get_subrecord_int("NPDT", start=4, length=4)
        self.attributes = {}
        for i in range(len(mwglobals.ATTRIBUTES)):
            self.attributes[mwglobals.ATTRIBUTES[i]] = self.get_subrecord_int("NPDT", start=8 + 4 * i, length=4)
        self.health = self.get_subrecord_int("NPDT", start=40, length=4)
        self.spell_pts = self.get_subrecord_int("NPDT", start=44, length=4)
        self.fatigue = self.get_subrecord_int("NPDT", start=48, length=4)
        self.soul = self.get_subrecord_int("NPDT", start=52, length=4)
        self.combat = self.get_subrecord_int("NPDT", start=56, length=4)
        self.magic = self.get_subrecord_int("NPDT", start=60, length=4)
        self.stealth = self.get_subrecord_int("NPDT", start=64, length=4)
        self.attack1_min = self.get_subrecord_int("NPDT", start=68, length=4)
        self.attack1_max = self.get_subrecord_int("NPDT", start=72, length=4)
        self.attack2_min = self.get_subrecord_int("NPDT", start=76, length=4)
        self.attack2_max = self.get_subrecord_int("NPDT", start=80, length=4)
        self.attack3_min = self.get_subrecord_int("NPDT", start=84, length=4)
        self.attack3_max = self.get_subrecord_int("NPDT", start=88, length=4)
        self.barter_gold = self.get_subrecord_int("NPDT", start=92, length=4)

        flags = self.get_subrecord_int("FLAG")
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

        self.scale = self.get_subrecord_float("XSCL")

        self.items = {}
        for i in range(self.num_subrecords("NPCO")):
            item_count = self.get_subrecord_int("NPCO", index=i, start=0, length=4)
            item_name = self.get_subrecord_string("NPCO", index=i, start=4, length=32)
            self.items[item_name] = item_count
        self.spells = []
        for i in range(self.num_subrecords("NPCS")):
            self.spells += [self.get_subrecord_string("NPCS", index=i)]

        load_ai(self)

        mwglobals.object_ids[self.id] = self

    def get_blood(self):
        if self.white_blood:
            return "Skeleton (White)"
        if self.gold_blood:
            return "Metal Sparks (Gold)"
        return "Default (Red)"

    def buys_sells(self):
        types = []
        if self.service_weapons:
            types += ["WEAP"]
        if self.service_armor:
            types += ["ARMO"]
        if self.service_clothing:
            types += ["CLOT"]
        if self.service_books:
            types += ["BOOK"]
        if self.service_ingredients:
            types += ["INGR"]
        if self.service_picks:
            types += ["LOCK"]
        if self.service_probes:
            types += ["PROB"]
        if self.service_lights:
            types += ["LIGH"]
        if self.service_apparatus:
            types += ["APPA"]
        if self.service_repair_items:
            types += ["REPA"]
        if self.service_miscellaneous:
            types += ["MISC"]
        if self.service_potions:
            types += ["ALCH"]
        if self.service_magic_items:
            types += ["Magic Items"]
        return types

    def other_services(self):
        types = []
        if self.service_training:
            types += ["Training"]
        if self.service_spellmaking:
            types += ["Spellmaking"]
        if self.service_enchanting:
            types += ["Enchanting"]
        if self.service_repair:
            types += ["Repair"]
        return types

    def trained_skills(self):
        if self.service_training:
            return sorted(self.skills.items(), key=lambda x: x[1], reverse=True)[:3]
        return []

    def record_details(self):
        string = "|Name|    " + str(self) + MwRecord.format_record_details(self, [
            ("\n|Script|", "script"),
            ("\n|Type|", "type"), ("    |Level|", "level"),
            ("\n|Essential|", "essential", False),
            ("\n|Respawn|", "respawn", False),
            ("\n|Animation File|", "animation_file"),
            ("\n|Scale|    {:.2f}", "scale"),
            ("\n|Weapon & Shield|", "weapon_and_shield", False),
            ("\n|Flies|", "flies", False),
            ("\n|Walks|", "walks", False),
            ("\n|Swims|", "swims", False),
            ("\n|Biped|", "biped", False),
            ("\n|None|", "none", False),
            ("\n|Attributes|", "attributes"),
            ("\n|Combat|", "combat"),
            ("\n|Magic|", "magic"),
            ("\n|Stealth|", "stealth"),
            ("\n|Health|", "health"),
            ("\n|Spell Pts|", "spell_pts"),
            ("\n|Fatigue|", "fatigue"),
            ("\n|Soul|", "soul"),
            ("\n|Attack 1|", "attack1_min"), (" - {}", "attack1_max"),
            ("\n|Attack 2|", "attack2_min"), (" - {}", "attack2_max"),
            ("\n|Attack 3|", "attack3_min"), (" - {}", "attack3_max"),
            ("\n|Blood Texture|", "get_blood", "Default (Red)"),
            ("\n|Sound Gen Creature|", "sound_gen_creature"),
            ("\n|Items|", "items", {}),
            ("\n|Spells|", "spells", []),
            ("\n|Fight|", "fight"), ("    |Flee|", "flee"), ("    |Alarm|", "alarm"), ("    |Hello|", "hello"),
            ("\n|Barter Gold|", "barter_gold", 0),
            ("\n|Buys / Sells|", "buys_sells", []),
            ("\n|Other Services|", "other_services", [])
        ])
        if len(self.destinations) > 0:
            string += "\n|Travel Services|"
            for destination in self.destinations:
                string += "\n" + destination.record_details()
        if len(self.ai_packages) > 0:
            string += "\n|AI Packages|"
            for ai_package in self.ai_packages:
                string += "\n" + ai_package.record_details()
        return string

    def __str__(self):
        return "{} [{}]".format(self.name, self.id)

    def diff(self, other):
        MwRecord.diff(self, other, ["animation_file", "sound_gen_creature", "name", "script", "type", "level",
                                    "attributes", "health", "spell_pts", "fatigue", "soul", "combat", "magic",
                                    "stealth", "attack1_min", "attack1_max", "attack2_min", "attack2_max",
                                    "attack3_min", "attack3_max", "barter_gold", "biped", "respawn",
                                    "weapon_and_shield", "none", "swims", "flies", "walks", "essential", "white_blood",
                                    "gold_blood", "scale", "items", "spells", "hello", "fight", "flee", "alarm",
                                    "service_ingredients", "service_picks", "service_probes", "service_lights",
                                    "service_apparatus", "service_repair_items", "service_miscellaneous",
                                    "service_spells", "service_magic_items", "service_potions", "service_training",
                                    "service_spellmaking", "service_enchanting", "service_repair", "destinations",
                                    "ai_packages"])
