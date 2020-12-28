from mwrecord import MwRecord
import record.mwmgef as mwmgef
import mwglobals

do_autocalc = False

class MwENCH(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
    
    def load(self):
        self.id = self.get_subrecord_string("NAME")
        self.type = mwglobals.ENCH_TYPES[self.get_subrecord_int("ENDT", start=0, length=4)]
        self.enchantment_cost = self.get_subrecord_int("ENDT", start=4, length=4)
        self.charge = self.get_subrecord_int("ENDT", start=8, length=4)
        self.autocalc = self.get_subrecord_int("ENDT", start=12, length=1) == 1
        
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
            self.enchantment_cost = round(cost)
            self.charge = self.enchantment_cost
            if self.type == "Cast When Used":
                self.charge *= 5
            elif self.type == "Cast When Strikes":
                self.charge *= 10
    
    def charge_cost_uses(self):
        return "Infinite" if type == "Constant Effect" else "{}/{} = {}".format(self.charge, self.enchantment_cost, self.charge, self.enchantment_cost)
    
    def wiki_entry(self):
        string = self.type
        for enchantment in self.enchantments:
            string += "<br>\n" + enchantment.__str__(True, add_type=self.type != "Constant Effect")
        return string
    
    def record_details(self):
        return MwRecord.format_record_details(self, [
        ("|ID|", "id"),
        ("\n|Cast Type|", "type"),
        ("\n|Charge Amount|", "charge"),
        ("\n|Enchantment Cost|", "enchantment_cost"),
        ("\n|Auto Calculcate|", "autocalc", False),
        ("\n|Enchantments|", "enchantments", [])
        ])
    
    def __str__(self):
        return self.id
    
    def diff(self, other):
        MwRecord.diff(self, other, ["type", "enchantment_cost", "charge", "autocalc", "enchantments"])

def load_enchantments(self):
    self.enchantments = []
    for i in range(self.num_subrecords("ENAM")):
        enchantment = MwENCHSingle()
        enchantment.effect_id = self.get_subrecord_int("ENAM", index=i, start=0, length=2)
        enchantment.skill_id = self.get_subrecord_int("ENAM", index=i, start=2, length=1)
        enchantment.attribute_id = self.get_subrecord_int("ENAM", index=i, start=3, length=1)
        enchantment.range_type = mwglobals.ENCH_RANGES[self.get_subrecord_int("ENAM", index=i, start=4, length=4)]
        enchantment.area = self.get_subrecord_int("ENAM", index=i, start=8, length=4)
        enchantment.duration = self.get_subrecord_int("ENAM", index=i, start=12, length=4)
        enchantment.mag_min = self.get_subrecord_int("ENAM", index=i, start=16, length=4)
        enchantment.mag_max = self.get_subrecord_int("ENAM", index=i, start=20, length=4)
        self.enchantments += [enchantment]

class MwENCHSingle:
    def __str__(self, add_template=False, add_type=True):
        effect_name = mwglobals.MAGIC_NAMES[self.effect_id]
        string = ("{{Effect Link|" if add_template else "") + effect_name
        if self.skill_id != -1:
            if add_template:
                string += "|" + effect_name
            string += " " + mwglobals.SKILLS[self.skill_id]
        elif self.attribute_id != -1:
            if add_template:
                string += "|" + effect_name
            string += " " + mwglobals.ATTRIBUTES[self.attribute_id]
        if add_template:
            string += "}}"
        if self.mag_min >= 0 or self.mag_max >= 0:
            mag_type = mwmgef.get_magnitude_type(self.effect_id)
            if mag_type == mwglobals.MagnitudeType.TIMES_INT:
                string += " {:.1f}".format(self.mag_min / 10)
                if self.mag_min != self.mag_max:
                    string += " to {:.1f}".format(self.mag_max / 10)
                string += "x INT"
            elif mag_type != mwglobals.MagnitudeType.NONE:
                string += " " + str(self.mag_min)
                if self.mag_min != self.mag_max:
                    string += " to " + str(self.mag_max)
                if mag_type == mwglobals.MagnitudeType.PERCENTAGE:
                    string += "%"
                elif mag_type == mwglobals.MagnitudeType.FEET:
                    string += " ft"
                elif mag_type == mwglobals.MagnitudeType.LEVEL:
                    string += " Level" if self.mag_min == 1 and self.mag_max == 1 else " Levels"
                else:
                    string += " pt" if self.mag_min == 1 and self.mag_max == 1 else " pts"
            
            if add_type:
                if self.duration > 0 and not mwmgef.has_no_duration(self.effect_id):
                    string += " for {} {}".format(self.duration, "sec" if self.duration == 1 else "secs")
                if self.area > 0:
                    string += " in {} ft".format(self.area)
                if self.range_type != None:
                    string += " on " + str(self.range_type)
        
        return string
    
    def __repr__(self):
        return str(self)