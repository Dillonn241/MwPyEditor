import mwglobals
from mwrecord import MwRecord


class MwWEAP(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
        self.id_ = ''
        self.model = ''
        self.name = None
        self.weight = 0.0
        self.value = 0
        self.type_id = 0
        self.health = 0
        self.speed = 0.0
        self.reach = 0.0
        self.enchantment = 0
        self.chop_min = 0
        self.chop_max = 0
        self.slash_min = 0
        self.slash_max = 0
        self.thrust_min = 0
        self.thrust_max = 0
        self.ignores_normal_weapon_resistance = False
        self.silver_weapon = False
        self.icon = None
        self.enchanting = None
        self.script = None

    def load(self):
        self.id_ = self.parse_string('NAME')
        self.model = self.parse_string('MODL')
        self.name = self.parse_string('FNAM')
        self.weight = self.parse_float('WPDT')
        self.value = self.parse_uint('WPDT', start=4)
        self.type_id = self.parse_uint('WPDT', start=8, length=2)
        self.health = self.parse_uint('WPDT', start=10, length=2)
        self.speed = self.parse_float('WPDT', start=12)
        self.reach = self.parse_float('WPDT', start=16)
        self.enchantment = self.parse_uint('WPDT', start=20, length=2)
        self.chop_min = self.parse_uint('WPDT', start=22, length=1)
        self.chop_max = self.parse_uint('WPDT', start=23, length=1)
        self.slash_min = self.parse_uint('WPDT', start=24, length=1)
        self.slash_max = self.parse_uint('WPDT', start=25, length=1)
        self.thrust_min = self.parse_uint('WPDT', start=26, length=1)
        self.thrust_max = self.parse_uint('WPDT', start=27, length=1)

        flags = self.parse_uint('WPDT', start=28)
        self.ignores_normal_weapon_resistance = (flags & 0x1) == 0x1
        self.silver_weapon = (flags & 0x2) == 0x2

        self.icon = self.parse_string('ITEX')
        self.enchanting = self.parse_string('ENAM')
        self.script = self.parse_string('SCRI')

        mwglobals.object_ids[self.id_] = self

    def get_type(self):
        return mwglobals.WEAP_TYPES[self.type_id]

    def set_type(self, value):
        if value in mwglobals.WEAP_TYPES:
            self.type_id = mwglobals.WEAP_TYPES.index(value)

    def get_actual_enchantment(self):
        return self.enchantment / 10

    def record_details(self):
        return MwRecord.format_record_details(self, [
            ("|Name|", '__str__'),
            ("\n|Model|", 'model'),
            ("\n|Weight|    {:.2f}", 'weight'),
            ("\n|Value|", 'value'),
            ("\n|Type|", 'get_type'),
            ("\n|Health|", 'health'),
            ("\n|Speed|    {:.2f}", 'speed'),
            ("\n|Reach|    {:.2f}", 'reach'),
            ("\n|Enchantment|", 'enchantment'),
            ("\n|Chop|", 'chop_min'), (" - {}", 'chop_max'),
            ("\n|Slash|", 'slash_min'), (" - {}", 'slash_max'),
            ("\n|Thrust|", 'thrust_min'), (" - {}", 'thrust_max'),
            ("\n|Ignores Normal Weapon Resistance|", 'ignores_normal_weapon_resistance', False),
            ("\n|Silver Weapon|", 'silver_weapon', False),
            ("\n|Icon|", 'icon'),
            ("\n|Enchanting|", 'enchanting'),
            ("\n|Script|", 'script')
        ])

    def __str__(self):
        return f"{self.name} [{self.id_}]"

    def diff(self, other):
        return MwRecord.diff(self, other, ['model', 'name', 'weight', 'value', 'get_type', 'health', 'speed', 'reach',
                                           'enchantment', 'chop_min', 'chop_max', 'slash_min', 'slash_max',
                                           'thrust_min', 'thrust_max', 'ignore_normal_weapon_resistance', 'silver',
                                           'icon', 'enchanting', 'script'])
