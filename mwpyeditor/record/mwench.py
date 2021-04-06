from mwpyeditor.core import mwglobals
from mwpyeditor.core.mwrecord import MwRecord
from mwpyeditor.record import mwmgef


class MwENCH(MwRecord):
    do_autocalc = False

    def __init__(self):
        MwRecord.__init__(self)
        self.id_ = ''
        self.type_id = 0
        self.enchantment_cost = 0
        self.charge = 0
        self.autocalc = False
        self.enchantments = []

    def load(self):
        self.id_ = self.parse_string('NAME')

        self.type_id = self.parse_uint('ENDT')
        self.enchantment_cost = self.parse_uint('ENDT', start=4)
        self.charge = self.parse_uint('ENDT', start=8)
        flags = self.parse_uint('ENDT', start=12, length=1)
        self.autocalc = (flags & 0x1) == 0x1

        load_enchantments(self)

        if MwENCH.do_autocalc and self.autocalc:
            self.autocalc_stats()

        mwglobals.object_ids[self.id_] = self

    def autocalc_stats(self):
        if self.type_id != 3:  # Constant Effect
            cost = 0
            for enchantment in self.enchantments:
                base_cost = mwglobals.records['MGEF'][enchantment.effect_id].base_cost
                base_cost /= 40
                multiplier = base_cost
                base_cost *= enchantment.duration
                base_cost *= enchantment.mag_min + enchantment.mag_max
                base_cost += enchantment.area * multiplier
                if enchantment.range_type_id == mwglobals.ENCH_RANGES[2]:  # Target
                    base_cost *= 1.5
                cost += base_cost
            self.enchantment_cost = round(cost)
            self.charge = self.enchantment_cost
            if self.type_id == 2:  # Cast When Used
                self.charge *= 5
            elif self.type_id == 1:  # Cast When Strikes
                self.charge *= 10

    def get_type(self):
        if 0 <= self.type_id < len(mwglobals.ENCH_TYPES):
            return mwglobals.ENCH_TYPES[self.type_id]

    def set_type(self, value):
        if value in mwglobals.ENCH_TYPES:
            self.type_id = mwglobals.ENCH_TYPES.index(value)

    def charge_cost_uses(self):
        if self.type_id == 3:  # Constant Effect
            return "Infinite"
        else:
            return f"{self.charge}/{self.enchantment_cost} = {self.charge / self.enchantment_cost}"

    def wiki_entry(self):
        string = self.get_type()
        for enchantment in self.enchantments:
            add_type = self.type_id != 3  # Constant Effect
            string += "<br>\n" + enchantment.__str__(True, add_type=add_type)
        return string

    def record_details(self):
        return MwRecord.format_record_details(self, [
            ("|ID|", 'id_'),
            ("\n|Cast Type|", 'get_type'),
            ("\n|Charge Amount|", 'charge'),
            ("\n|Enchantment Cost|", 'enchantment_cost'),
            ("\n|Auto Calculate|", 'autocalc', False),
            ("\n|Enchantments|", 'enchantments', [])
        ])

    def __str__(self):
        return self.id_

    def diff(self, other):
        return MwRecord.diff(self, other, ['get_type', 'enchantment_cost', 'charge', 'autocalc', 'enchantments'])


def load_enchantments(self):
    self.enchantments = [MwENCHSingle(enam.parse_uint(length=2),  # effect id
                                      enam.parse_int(start=2, length=1),  # skill id
                                      enam.parse_int(start=3, length=1),  # attribute id
                                      enam.parse_uint(start=4),  # range type id
                                      enam.parse_uint(start=8),  # area
                                      enam.parse_uint(start=12),  # duration
                                      enam.parse_uint(start=16),  # mag min
                                      enam.parse_uint(start=20))  # mag max
                         for enam in self.subrecords.get('ENAM', [])]


class MwENCHSingle:
    def __init__(self, effect_id, skill_id, attribute_id, range_type_id, area, duration, mag_min, mag_max):
        self.effect_id = effect_id
        self.skill_id = skill_id
        self.attribute_id = attribute_id
        self.range_type_id = range_type_id
        self.area = area
        self.duration = duration
        self.mag_min = mag_min
        self.mag_max = mag_max

    def get_range_type(self):
        return mwglobals.ENCH_RANGES[self.range_type_id]

    def set_range_type(self, value):
        if value in mwglobals.ENCH_RANGES:
            self.range_type_id = mwglobals.ENCH_RANGES.index(value)

    def __str__(self, add_template=False, add_type=True):
        effect_name = mwglobals.MAGIC_NAMES[self.effect_id]
        if add_template:
            string = [f"{{Effect Link|{effect_name}"]
        else:
            string = [effect_name]

        if self.skill_id != -1:
            if add_template:
                string.append(f"|{effect_name}")
            string.append(f" {mwglobals.SKILLS[self.skill_id]}")
        elif self.attribute_id != -1:
            if add_template:
                string.append(f"|{effect_name}")
            string.append(f" {mwglobals.ATTRIBUTES[self.attribute_id]}")
        if add_template:
            string.append("}}")

        if self.mag_min >= 0 or self.mag_max >= 0:
            mag_type = mwmgef.get_magnitude_type(self.effect_id)
            if mag_type == mwglobals.MagnitudeType.TIMES_INT:
                string.append(f" {self.mag_min / 10:.1f}")
                if self.mag_min != self.mag_max:
                    string.append(f" to {self.mag_max / 10:.1f}")
                string.append("x INT")
            elif mag_type != mwglobals.MagnitudeType.NONE:
                string.append(f" {self.mag_min}")
                if self.mag_min != self.mag_max:
                    string.append(f" to {self.mag_max}")
                if mag_type == mwglobals.MagnitudeType.PERCENTAGE:
                    string.append("%")
                elif mag_type == mwglobals.MagnitudeType.FEET:
                    string.append(" ft")
                elif mag_type == mwglobals.MagnitudeType.LEVEL:
                    string.append(" Level")
                    if self.mag_min == 1 and self.mag_max == 1:
                        string.append("s")
                else:
                    string.append(" pt")
                    if self.mag_min == 1 and self.mag_max == 1:
                        string.append("s")

            if add_type:
                if self.duration > 0 and not mwmgef.has_no_duration(self.effect_id):
                    string.append(f" for {self.duration} sec")
                    if self.duration != 1:
                        string.append("s")
                if self.area > 0:
                    string.append(f" in {self.area} ft")
                if self.range_type_id != -1:
                    string.append(f" on {self.get_range_type()}")

        return ''.join(string)

    def __repr__(self):
        return str(self)
