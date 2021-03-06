import mwglobals
from mwrecord import MwRecord
from record.mwench import load_enchantments

do_autocalc = False


class MwSPEL(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
    
    def load(self):
        self.id = self.get_subrecord_string("NAME")
        self.name = self.get_subrecord_string("FNAM")
        
        self.type = mwglobals.SPEL_TYPES[self.get_subrecord_int("SPDT", start=0, length=4)]
        self.spell_cost = self.get_subrecord_int("SPDT", start=4, length=4)
        flags = self.get_subrecord_int("SPDT", start=8, length=4)
        self.autocalc = (flags & 0x1) == 0x1
        self.pc_start_spell = (flags & 0x2) == 0x2
        self.always_succeeds = (flags & 0x4) == 0x4
        
        load_enchantments(self)
        
        if do_autocalc and self.autocalc:
            self.autocalc_stats()
        mwglobals.object_ids[self.id] = self
    
    def autocalc_stats(self):
        if self.type != "Constant Effect":
            cost = 0
            for enchantment in self.enchantments:
                base_cost = mwglobals.records["MGEF"][enchantment.effect_id].base_cost
                base_cost /= 40
                multiplier = base_cost
                base_cost *= enchantment.duration
                base_cost *= enchantment.mag_min + enchantment.mag_max
                base_cost += enchantment.area * multiplier
                if enchantment.range_type == "Target":
                    base_cost *= 1.5
                cost += base_cost
            self.spell_cost = round(cost)
    
    def wiki_entry(self):
        string = "|-\n|'''{{Anchor|" + self.name + "}}'''"
        for enchantment in self.enchantments:
            enchant_str = enchantment.__str__(True, add_type=self.type != "Disease" and self.type != "Blight")
            string += "<br>{{Small|" + enchant_str + "}}"
        string += "\n|style=text-align:center|" + str(self.spell_cost) + "\n|"
        return string
    
    def record_details(self):
        return "|Name|    " + str(self) + MwRecord.format_record_details(self, [
            ("\n|Type|", "type"),
            ("\n|Spell Cost|", "spell_cost"),
            ("\n|Auto Calculate Cost|", "autocalc", False),
            ("\n|PC Start Spell|", "pc_start_spell", False),
            ("\n|Always Succeeds|", "always_succeeds", False),
            ("\n|Enchantments|", "enchantments", [])
        ])
    
    def __str__(self):
        return "{} [{}]".format(self.name, self.id)
    
    def diff(self, other):
        MwRecord.diff(self, other, ["name", "type", "spell_cost", "autocalc", "pc_start_spell", "always_succeeds",
                                    "enchantments"])
