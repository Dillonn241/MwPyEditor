from core import mwglobals
from core.mwrecord import MwRecord
from record.mwench import load_enchantments


class MwSPEL(MwRecord):
    do_autocalc = False

    def __init__(self):
        MwRecord.__init__(self)
        self.id_ = ''
        self.name = None
        self.type_id = 0
        self.spell_cost = 0
        self.autocalc = False
        self.pc_start_spell = False
        self.always_succeeds = False
        self.enchantments = []

    def load(self):
        self.id_ = self.parse_string('NAME')
        self.name = self.parse_string('FNAM')

        self.type_id = self.parse_uint('SPDT')
        self.spell_cost = self.parse_uint('SPDT', start=4)
        flags = self.parse_uint('SPDT', start=8)
        self.autocalc = (flags & 0x1) == 0x1
        self.pc_start_spell = (flags & 0x2) == 0x2
        self.always_succeeds = (flags & 0x4) == 0x4

        load_enchantments(self)

        if MwSPEL.do_autocalc and self.autocalc:
            self.autocalc_stats()

        mwglobals.object_ids[self.id_] = self

    def autocalc_stats(self):
        if self.type_id == 0 or self.type_id == 5:  # Spell or Power
            cost = 0
            for enchantment in self.enchantments:
                base_cost = mwglobals.records['MGEF'][enchantment.effect_id].base_cost
                base_cost /= 40
                multiplier = base_cost
                base_cost *= enchantment.duration
                base_cost *= enchantment.mag_min + enchantment.mag_max
                base_cost += enchantment.area * multiplier
                if enchantment.range_type_id == 2:  # Target
                    base_cost *= 1.5
                cost += base_cost
            self.spell_cost = round(cost)

    def get_type(self):
        if 0 <= self.type_id < len(mwglobals.SPEL_TYPES):
            return mwglobals.SPEL_TYPES[self.type_id]

    def set_type(self, value):
        if value in mwglobals.SPEL_TYPES:
            self.type_id = mwglobals.SPEL_TYPES.index(value)

    def wiki_entry(self):
        string = [f"|-\n|'''{{{{Anchor|{self.name}}}}}'''"]
        add_type = self.type_id != 3 and self.type_id != 2  # Disease and Blight
        for enchantment in self.enchantments:
            enchant_str = enchantment.__str__(True, add_type=add_type)
            string.append(f"<br>{{{{Small|{enchant_str}}}}}")
        string.append(f"\n|style=text-align:center|{self.spell_cost}\n|")
        return ''.join(string)

    def record_details(self):
        return MwRecord.format_record_details(self, [
            ("|Name|", '__str__'),
            ("\n|Type|", 'get_type'),
            ("\n|Spell Cost|", 'spell_cost'),
            ("\n|Auto Calculate Cost|", 'autocalc', False),
            ("\n|PC Start Spell|", 'pc_start_spell', False),
            ("\n|Always Succeeds|", 'always_succeeds', False),
            ("\n|Enchantments|", 'enchantments', [])
        ])

    def __str__(self):
        return f"{self.name} [{self.id_}]"

    def diff(self, other):
        return MwRecord.diff(self, other, ['name', 'get_type', 'spell_cost', 'autocalc', 'pc_start_spell',
                                           'always_succeeds', 'enchantments'])
