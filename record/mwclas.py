from mwrecord import MwRecord
import mwglobals

class MwCLAS(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
    
    def load(self):
        self.id = self.get_subrecord_string("NAME")
        self.name = self.get_subrecord_string("FNAM")
        self.primary_attributes = []
        self.primary_attributes += [mwglobals.ATTRIBUTES[self.get_subrecord_int("CLDT", start=0, length=4)]]
        self.primary_attributes += [mwglobals.ATTRIBUTES[self.get_subrecord_int("CLDT", start=4, length=4)]]
        self.specialization = mwglobals.SPECIALIZATIONS[self.get_subrecord_int("CLDT", start=8, length=4)]
        
        self.minor_skills = []
        self.major_skills = []
        for i in range(5):
            self.minor_skills += [mwglobals.SKILLS[self.get_subrecord_int("CLDT", start=12 + 8 * i, length=4)]]
            self.major_skills += [mwglobals.SKILLS[self.get_subrecord_int("CLDT", start=16 + 8 * i, length=4)]]
        
        flags = self.get_subrecord_int("CLDT", start=52, length=4)
        self.playable = (flags & 0x1) == 0x1
        ai_flags = self.get_subrecord_int("CLDT", start=56, length=4)
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
        
        self.description = self.get_subrecord_string("DESC")
        
        mwglobals.object_ids[self.id] = self
    
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
    
    def record_details(self):
        return "|Name|    " + str(self) + MwRecord.format_record_details(self, [
        ("\n|Primary Attributes|", "primary_attributes"),
        ("\n|Specialization|", "specialization"),
        ("\n|Major Skills|", "major_skills"),
        ("\n|Minor Skills|", "minor_skills"),
        ("\n|Description|", "description"),
        ("\n|Playable|", "playable", False),
        ("\n|Buys / Sells|", "buys_sells", []),
        ("\n|Other Services|", "other_services", [])
        ])
    
    def __str__(self):
        return "{} [{}]".format(self.name, self.id)
    
    def diff(self, other):
        MwRecord.diff(self, other, ["name", "primary_attributes", "specialization", "minor_skills", "major_skills", "playable", "service_weapons", "service_armor", "service_clothing", "service_books", "service_ingredients", "service_picks", "service_probes", "service_lights", "service_apparatus", "service_repair_items", "service_miscellaneous", "service_spells", "service_magic_items", "service_potions", "service_training", "service_spellmaking", "service_enchanting", "service_repair", "description"])