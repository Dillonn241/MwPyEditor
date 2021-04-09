from mwpyeditor.core import mwglobals
from mwpyeditor.core.mwrecord import MwRecord
from mwpyeditor.record.mwench import load_enchantments, save_enchantments


class MwALCH(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
        self.id_ = ''
        self.model = None
        self.icon = None
        self.script = None
        self.name = None
        self.weight = 0.0
        self.value = 0
        self.autocalc = False
        self.auto_value = None
        self.enchantments = []

    def load(self):
        self.id_ = self.parse_string('NAME')
        self.model = self.parse_string('MODL')
        self.icon = self.parse_string('TEXT')
        self.script = self.parse_string('SCRI')
        self.name = self.parse_string('FNAM')

        self.weight = self.parse_float('ALDT')
        self.value = self.parse_uint('ALDT', start=4)
        flags = self.parse_uint('ALDT', start=8)
        self.autocalc = (flags & 0x1) == 0x1

        load_enchantments(self)

        mwglobals.object_ids[self.id_] = self

    def save(self):
        self.clear_subrecords()
        self.add_string(self.id_, 'NAME')
        self.add_string(self.model, 'MODL')
        self.add_string(self.icon, 'TEXT')
        self.add_string(self.script, 'SCRI')
        self.add_string(self.name, 'FNAM')
        sub_aldt = self.add_subrecord('ALDT')
        sub_aldt.add_float(self.weight)
        sub_aldt.add_uint(self.value)
        flags = 0x1 if self.autocalc else 0x0
        sub_aldt.add_uint(flags)
        save_enchantments(self)
        self.save_deleted()

    def get_auto_value(self):
        if self.auto_value:
            return self.auto_value
        return self.autocalc_value()

    def autocalc_value(self):
        if not self.autocalc:
            return self.value
        cost = 0
        for enchantment in self.enchantments:
            base_cost = mwglobals.records['MGEF'][enchantment.effect_id].base_cost
            base_cost /= 10
            multiplier = base_cost * 2
            if enchantment.mag_min > 0:
                base_cost += (enchantment.duration + enchantment.mag_min) * multiplier
            cost += base_cost
        self.auto_value = round(cost)
        return self.auto_value

    def wiki_entry(self, is_beverage=True):
        enchantment_string = []
        for enchantment in self.enchantments:
            enchantment_string.append(enchantment.__str__(add_template=True))
        enchantment_string = "<br>\n".join(enchantment_string)
        if is_beverage:
            return f"""|-\n
                    |[[File:TD3-icon-potion-{self.icon}.png]]\n
                    |'''{{{{Anchor|{self.name}}}}}'''<br>{{{{Small|{self.id_}}}}}\n
                    | style=\"text-align:left;\" |\n{enchantment_string}\n
                    |{mwglobals.decimal_format(self.weight)}||{self.value}"""
        return f"""|-\n
                |[[File:TD3-icon-potion-{self.icon}.png]]\n
                |'''{{{{Anchor|{self.name}}}}}'''\n
                |{self.id_}\n
                | style=\"text-align:left;\" |\n{enchantment_string}\n
                |{mwglobals.decimal_format(self.weight)}||{self.value}"""

    def record_details(self):
        return MwRecord.format_record_details(self, [
            ("|Name|", "__str__"),
            ("\n|Model|", "model"),
            ("\n|Icon|", "icon"),
            ("\n|Script|", "script"),
            ("\n|Weight|    {:.2f}", "weight"),
            ("\n|Value|", "get_auto_value"), (" {}", "(auto)" if self.autocalc else ''),
            ("\n|Auto Calculate|", "autocalc", False),
            ("\n|Enchantments|", "enchantments", [])
        ])

    def __str__(self):
        return f"{self.name} [{self.id_}]"

    def diff(self, other):
        return MwRecord.diff(self, other, ['model', 'name', 'icon', 'script', 'weight', 'value', 'autocalc',
                                           'enchantments'])
