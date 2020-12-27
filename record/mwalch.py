from mwrecord import MwRecord
import mwglobals
from record.mwench import MwENCHSingle

class MwALCH(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
    
    def load(self):
        self.id = self.get_subrecord_string("NAME")
        self.model = self.get_subrecord_string("MODL")
        self.name = self.get_subrecord_string("FNAM")
        self.weight = self.get_subrecord_float("ALDT", start=0, length=4)
        self.value = self.get_subrecord_int("ALDT", start=4, length=4)
        self.autocalc = self.get_subrecord_int("ALDT", start=8, length=4) == 1
        
        self.enchantments = []
        for i in range(self.num_subrecords("ENAM")):
            enchantment = MwENCHSingle()
            enchantment.effect_id = self.get_subrecord_int("ENAM", index=i, start=0, length=2)
            enchantment.skill_id = self.get_subrecord_int("ENAM", index=i, start=2, length=1)
            enchantment.attribute_id = self.get_subrecord_int("ENAM", index=i, start=3, length=1)
            enchantment.range_type = None
            enchantment.area = 0
            enchantment.duration = self.get_subrecord_int("ENAM", index=i, start=12, length=4)
            enchantment.mag_min = self.get_subrecord_int("ENAM", index=i, start=16, length=4)
            enchantment.mag_max = enchantment.mag_min
            self.enchantments += [enchantment]
        
        self.icon = self.get_subrecord_string("TEXT")
        self.script = self.get_subrecord_string("SCRI")
        
        if self.autocalc:
            self.autocalc_stats()
        mwglobals.object_ids[self.id] = self
    
    def autocalc_stats(self):
        cost = 0
        for enchantment in self.enchantments:
            base_cost = mwglobals.records["MGEF"][enchantment.effect_id].base_cost
            base_cost /= 10
            multiplier = base_cost * 2
            if enchantment.mag_min > 0:
                base_cost += (enchantment.duration + enchantment.mag_min) * multiplier
            cost += base_cost
        self.value = round(cost)
    
    def wiki_entry(self, is_beverage=True):
        enchantment_list = ""
        num_enchantments = len(self.enchantments)
        for i in range(num_enchantments):
            enchantment_list += self.enchantments[i].__str__(add_template=True)
            if i != num_enchantments - 1:
                enchantment_list += "<br>\n"
        if is_beverage:
            return "|-\n" \
            "|[[File:TD3-icon-potion-" + self.icon + ".png]]\n" \
            "|'''{{Anchor|" + self.name + "}}'''<br>{{Small|" + self.id + "}}\n" \
            "| style=\"text-align:left;\" |\n" + enchantment_list + "\n" \
            "|" + mwglobals.decimal_format(self.weight) + "||" + str(self.value)
        return "|-\n" \
        "|[[File:TD3-icon-potion-" + self.icon + ".png]]\n" \
        "|'''{{Anchor|" + self.name + "}}'''\n" \
        "|" + self.id + "\n" \
        "| style=\"text-align:left;\" |\n" + enchantment_list + "\n" \
        "|" + mwglobals.decimal_format(self.weight) + "||" + str(self.value)
    
    def record_details(self):
        return "|Name|    " + str(self) + MwRecord.format_record_details(self, [
        ("\n|Script|", "script"),
        ("\n|Model|", "model"),
        ("\n|Icon|", "icon"),
        ("\n|Weight|    {:.2f}", "weight"),
        ("\n|Value|", "value"),
        ("\n|Auto Calculate Value|", "autocalc", False),
        ("\n|Enchantments|", "enchantments", [])
        ])
    
    def __str__(self):
        return "{} [{}]".format(self.name, self.id)
    
    def compare(self, other):
        MwRecord.compare(self, other, ["model", "name", "weight", "value", "autocalc", "enchantments", "icon", "script"])