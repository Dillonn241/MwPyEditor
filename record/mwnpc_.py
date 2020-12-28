import math
from mwrecord import MwRecord
import mwglobals

do_autocalc = False

class MwNPC_(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
    
    def load(self):
        self.id = self.get_subrecord_string("NAME")
        self.animation_file = self.get_subrecord_string("MODL")
        self.name = self.get_subrecord_string("FNAM")
        self.race = self.get_subrecord_string("RNAM")
        self.class_ = self.get_subrecord_string("CNAM")
        self.faction = self.get_subrecord_string("ANAM")
        self.head_model = self.get_subrecord_string("BNAM")
        self.hair_model = self.get_subrecord_string("KNAM")
        self.script = self.get_subrecord_string("SCRI")
        
        self.level = self.get_subrecord_int("NPDT", start=0, length=2)
        if len(self.get_subrecord("NPDT").data) == 12:
            self.disposition = self.get_subrecord_int("NPDT", start=2, length=1, signed=False)
            self.reputation = self.get_subrecord_int("NPDT", start=3, length=1, signed=False)
            self.faction_rank = self.get_subrecord_int("NPDT", start=4, length=1, signed=False)
            self.barter_gold = self.get_subrecord_int("NPDT", start=8, length=4)
        else:
            self.attributes = {}
            for i in range(len(mwglobals.ATTRIBUTES)):
                value = self.get_subrecord_int("NPDT", start=2 + i, length=1, signed=False)
                self.attributes[mwglobals.ATTRIBUTES[i]] = value
            self.skills = {}
            for i in range(len(mwglobals.SKILLS)):
                value = self.get_subrecord_int("NPDT", start=10 + i, length=1, signed=False)
                self.skills[mwglobals.SKILLS[i]] = value
            self.health = self.get_subrecord_int("NPDT", start=38, length=2, signed=False)
            self.magicka = self.get_subrecord_int("NPDT", start=40, length=2, signed=False)
            self.fatigue = self.get_subrecord_int("NPDT", start=42, length=2, signed=False)
            self.disposition = self.get_subrecord_int("NPDT", start=44, length=1, signed=False)
            self.reputation = self.get_subrecord_int("NPDT", start=45, length=1, signed=False)
            self.faction_rank = self.get_subrecord_int("NPDT", start=46, length=1, signed=False)
            self.barter_gold = self.get_subrecord_int("NPDT", start=48, length=4)
        flags = self.get_subrecord_int("FLAG")
        self.female = (flags & 0x1) == 0x1
        self.essential = (flags & 0x2) == 0x2
        self.respawn = (flags & 0x4) == 0x4
        self.autocalc = (flags & 0x10) == 0x10
        self.white_blood = (flags & 0x400) == 0x400
        self.gold_blood = (flags & 0x800) == 0x800
        
        self.items = {}
        for i in range(self.num_subrecords("NPCO")):
            item_count = self.get_subrecord_int("NPCO", index=i, start=0, length=4)
            item_name = self.get_subrecord_string("NPCO", index=i, start=4, length=32)
            self.items[item_name] = item_count
        self.spells = []
        for i in range(self.num_subrecords("NPCS")):
            self.spells += [self.get_subrecord_string("NPCS", index=i)]
        
        load_ai(self)
        
        if do_autocalc and self.autocalc:
            self.autocalc_stats()
        mwglobals.object_ids[self.id] = self
    
    def autocalc_stats(self):
        mw_race = mwglobals.object_ids[self.race]
        mw_class = mwglobals.object_ids[self.class_]
        self.attributes = {}
        for i in range(len(mwglobals.ATTRIBUTES)):
            attribute = mwglobals.ATTRIBUTES[i]
            base = mw_race.get_sex_attribute(attribute, self.female)
            if attribute in mw_class.primary_attributes:
                base += 10
            
            k = 0
            for mw_skill in mwglobals.records["SKIL"]:
                if mw_skill.governing_attribute == attribute:
                    if mw_skill.name in mw_class.major_skills:
                        k += 1
                    elif mw_skill.name in mw_class.minor_skills:
                        k += 0.5
                    else:
                        k += 0.2
            self.attributes[attribute] = round(base + k * (self.level - 1))
        
        health_mult = 3
        if mw_class.specialization == "Combat":
            health_mult += 2
        elif mw_class.specialization == "Stealth":
            health_mult += 1
        if "Endurance" in mw_class.primary_attributes:
            health_mult += 1
        self.health = math.floor(0.5 * (self.attributes["Strength"]  + self.attributes["Endurance"]) + health_mult * (self.level - 1))
        
        self.magicka = math.floor(2 * self.attributes["Intelligence"]) # 2 = fNPCbaseMagickaMult
        self.fatigue = self.attributes["Strength"] + self.attributes["Willpower"] + self.attributes["Agility"] + self.attributes["Endurance"]
        
        self.skills = {}
        for mw_skill in mwglobals.records["SKIL"]:
            if mw_skill.name in mw_class.major_skills:
                k = 1
                base = 30
            elif mw_skill.name in mw_class.minor_skills:
                k = 1
                base = 15
            else:
                k = 0.1
                base = 5
            if mw_skill.specialization == mw_class.specialization:
                base += 5
                k += 0.5
            base += mw_race.get_skill_bonus(mw_skill.name)
            self.skills[mw_skill.name] = round(base + k * (self.level - 1))
        
        if self.faction:
            self.reputation = 2 * (self.faction_rank + 1) # 2 = iAutoRepFacMod
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
        if self.class_ == "Alchemist" or self.class_ == "Apothecary" or self.class_ == "Bookseller" or self.class_ == "Buoyant Armiger" or self.class_ == "Clothier" or self.class_ == "Enchanter" or self.class_ == "Guard" or self.class_ == "Guild Guide" or self.class_ == "Ordinator" or self.class_ == "Pawnbroker" or self.class_ == "Priest" or self.class_ == "Savant" or self.class_ == "Slave" or self.class_ == "Smith" or self.class_ == "Trader":
            return self.class_ + " (class)"
        return self.class_
    
    def get_faction_rank_name(self):
        return mwglobals.object_ids[self.faction].ranks[self.faction_rank].name
    
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
            return sorted(self.skills.items(), key=lambda x:x[1], reverse=True)[:3]
        return []
    
    def record_details(self):
        string = "|Name|    " + str(self) + MwRecord.format_record_details(self, [
        ("\n|Script|", "script"),
        ("\n|Race|", "race"), ("    |Sex|", "sex"),
        ("\n|Class|", "class"), ("    |Level|", "level"),
        ("\n|Faction|", "faction", ""), ("    |Rank|", "faction_rank", 0 if self.faction == "" else None),
        ("\n|Essential|", "essential", False),
        ("\n|Respawn|", "respawn", False),
        ("\n|Head Model|", "head_model"),
        ("\n|Hair Model|", "hair_model"),
        ("\n|Animation File|", "animation_file"),
        ("\n|Attributes|", "attributes"),
        ("\n|Skills|", "skills"),
        ("\n|Health|", "health"),
        ("\n|Magicka|", "magicka"),
        ("\n|Fatigue|", "fatigue"),
        ("\n|Disposition|", "disposition"),
        ("\n|Reputation|", "reputation"),
        ("\n|Blood Texture|", self.get_blood(), "Default (Red)", None),
        ("\n|Auto Calculate Stats|", "autocalc", False),
        ("\n|Items|", "items", {}),
        ("\n|Spells|", "spells", []),
        ("\n|Fight|", "fight"), ("    |Flee|", "flee"), ("    |Alarm|", "alarm"), ("    |Hello|", "hello"),
        ("\n|Barter Gold|", "barter_gold", 0),
        ("\n|Buys / Sells|", self.buys_sells(), [], None),
        ("\n|Other Services|", self.other_services(), [], None)
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
        MwRecord.diff(self, other, ["animation_file", "name", "race", "class_", "faction", "head_model", "hair_model", "script", "level", "attributes", "skills", "health", "magicka", "fatigue", "disposition", "reputation", "faction_rank", "barter_gold", "female", "essential", "respawn", "autocalc", "white_blood", "gold_blood", "spells", "items", "hello", "fight", "flee", "alarm", "service_weapons", "service_armor", "service_clothing", "service_books", "service_ingredients", "service_picks", "service_probes", "service_lights", "service_apparatus", "service_repair_items", "service_miscellaneous", "service_spells", "service_magic_items", "service_potions", "service_training", "service_spellmaking", "service_enchanting", "service_repair", "destinations", "ai_packages"])

def load_ai(self):
    self.hello = self.get_subrecord_int("AIDT", start=0, length=1, signed=False)
    self.fight = self.get_subrecord_int("AIDT", start=2, length=1, signed=False)
    self.flee = self.get_subrecord_int("AIDT", start=3, length=1, signed=False)
    self.alarm = self.get_subrecord_int("AIDT", start=4, length=1, signed=False)
    ai_flags = self.get_subrecord_int("AIDT", start=8, length=4)
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
        if subrecord.record_type == "DODT":
            destination = MwNPCDestination()
            destination.pos_x = subrecord.get_float(start=0, length=4)
            destination.pos_y = subrecord.get_float(start=4, length=4)
            destination.pos_z = subrecord.get_float(start=8, length=4)
            destination.rot_x = subrecord.get_float(start=12, length=4)
            destination.rot_y = subrecord.get_float(start=16, length=4)
            destination.rot_z = subrecord.get_float(start=20, length=4)
            self.destinations += [destination]
        elif subrecord.record_type == "DNAM":
            destination.cell = subrecord.get_string()
    
    self.ai_packages = []
    ai_package = None
    for subrecord in self.ordered_subrecords:
        if subrecord.record_type == "AI_A":
            ai_package = MwNPCAIPackage()
            ai_package.type = "Activate"
            ai_package.target = subrecord.get_string(start=0, length=32)
            self.ai_packages += [ai_package]
        elif subrecord.record_type == "AI_E":
            ai_package = MwNPCAIPackage()
            ai_package.type = "Escort"
            ai_package.x = subrecord.get_float(start=0, length=4)
            ai_package.y = subrecord.get_float(start=4, length=4)
            ai_package.z = subrecord.get_float(start=8, length=4)
            ai_package.duration = subrecord.get_int(start=12, length=2, signed=False)
            ai_package.target = subrecord.get_string(start=14, length=32)
            self.ai_packages += [ai_package]
        elif subrecord.record_type == "AI_F":
            ai_package = MwNPCAIPackage()
            ai_package.type = "Follow"
            ai_package.x = subrecord.get_float(start=0, length=4)
            ai_package.y = subrecord.get_float(start=4, length=4)
            ai_package.z = subrecord.get_float(start=8, length=4)
            ai_package.duration = subrecord.get_int(start=12, length=2, signed=False)
            ai_package.target = subrecord.get_string(start=14, length=32)
            self.ai_packages += [ai_package]
        elif subrecord.record_type == "AI_T":
            ai_package = MwNPCAIPackage()
            ai_package.type = "Travel"
            ai_package.x = subrecord.get_float(start=0, length=4)
            ai_package.y = subrecord.get_float(start=4, length=4)
            ai_package.z = subrecord.get_float(start=8, length=4)
            self.ai_packages += [ai_package]
        elif subrecord.record_type == "AI_W":
            ai_package = MwNPCAIPackage()
            ai_package.type = "Wander"
            ai_package.distance = subrecord.get_int(start=0, length=2, signed=False)
            ai_package.duration = subrecord.get_int(start=2, length=2, signed=False)
            ai_package.time_of_day = subrecord.get_int(start=4, length=1, signed=False)
            ai_package.idles = []
            for i in range(8):
                ai_package.idles += [subrecord.get_int(start=5 + i, length=1, signed=False)]
            self.ai_packages += [ai_package]
        elif subrecord.record_type == "CNDT":
            ai_package.cell = subrecord.get_string()

class MwNPCDestination:
    def record_details(self):
        return MwRecord.format_record_details(self, [
        ("|Position|    {:.3f}", "pos_x"), (", {:.3f}", "pos_y"), (", {:.3f}", "pos_z"), (" [{:.3f}", "rot_x"), (", {:.3f}", "rot_y"), (", {:.3f}]", "rot_z"), (" {}", str(self), None, None)
        ])
    
    def __str__(self):
        if hasattr(self, "cell"):
            return self.cell
        grid_x = math.floor(self.pos_x / 8192)
        grid_y = math.floor(self.pos_y / 8192)
        for cell in mwglobals.exterior_cells.values():
            if cell.grid_x == grid_x and cell.grid_y == grid_y:
                return str(cell)
        return "Wilderness [{},{}]".format(grid_x, grid_y)
    
    def __repr__(self):
        return self.record_details()

class MwNPCAIPackage:
    def record_details(self):
        details = [
        ("|Type|", "type"),
        ("\n|Target|", "target")
        ]
        if self.type == "Travel" or hasattr(self, "cell"):
            details += [("\n|Position|    {:.3f}", "x"), (", {:.3f}", "y"), (", {:.3f}", "z"), (" {}", "cell")]
        details += [
        ("\n|Distance|", "distance"),
        ("\n|Duration|", "duration"),
        ("\n|Time of Day|", "time_of_day"),
        ("\n|Idles|", "idles")
        ]
        return MwRecord.format_record_details(self, details)
    
    def __str__(self):
        return self.type
    
    def __repr__(self):
        return self.record_details()