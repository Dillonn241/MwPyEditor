from mwrecord import MwRecord
import mwglobals

class MwWEAP(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
    
    def load(self):
        self.id = self.get_subrecord_string("NAME")
        self.model = self.get_subrecord_string("MODL")
        self.name = self.get_subrecord_string("FNAM")
        
        self.weight = self.get_subrecord_float("WPDT", start=0, length=4)
        self.value = self.get_subrecord_int("WPDT", start=4, length=4)
        self.type = mwglobals.WEAPON_TYPES[self.get_subrecord_int("WPDT", start=8, length=2)]
        self.health = self.get_subrecord_int("WPDT", start=10, length=2, signed=False)
        self.speed = self.get_subrecord_float("WPDT", start=12, length=4)
        self.reach = self.get_subrecord_float("WPDT", start=16, length=4)
        self.enchantment = self.get_subrecord_int("WPDT", start=20, length=2)
        self.chop_min = self.get_subrecord_int("WPDT", start=22, length=1, signed=False)
        self.chop_max = self.get_subrecord_int("WPDT", start=23, length=1, signed=False)
        self.slash_min = self.get_subrecord_int("WPDT", start=24, length=1, signed=False)
        self.slash_max = self.get_subrecord_int("WPDT", start=25, length=1, signed=False)
        self.thrust_min = self.get_subrecord_int("WPDT", start=26, length=1, signed=False)
        self.thrust_max = self.get_subrecord_int("WPDT", start=27, length=1, signed=False)
        flags = self.get_subrecord_int("WPDT", start=28, length=4)
        self.ignores_normal_weapon_resistance = (flags & 0x1) == 0x1
        self.silver_weapon = (flags & 0x2) == 0x2
        
        self.icon = self.get_subrecord_string("ITEX")
        self.enchanting = self.get_subrecord_string("ENAM")
        self.script = self.get_subrecord_string("SCRI")
        mwglobals.object_ids[self.id] = self
    
    def get_actual_enchant():
        return self.enchant / 10
    
    def record_details(self):
        return "|Name|    " + str(self) + MwRecord.format_record_details(self, [
        ("\n|Type|", "type"),
        ("\n|Script|", "script"),
        ("\n|Weight|    {:.2f}", "weight"),
        ("\n|Value|", "value"),
        ("\n|Health|", "health"),
        ("\n|Speed|    {:.2f}", "speed"),
        ("\n|Reach|    {:.2f}", "reach"),
        ("\n|Enchantment|", "enchantment"),
        ("\n|Enchanting|", "enchanting"),
        ("\n|Chop|", "chop_min"), (" - {}", "chop_max"),
        ("\n|Slash|", "slash_min"), (" - {}", "slash_max"),
        ("\n|Thrust|", "thrust_min"), (" - {}", "thrust_max"),
        ("\n|Model|", "model"),
        ("\n|Icon|", "icon"),
        ("\n|Ignores Normal Weapon Resistance|", "ignores_normal_weapon_resistance", False),
        ("\n|Silver Weapon|", "silver_weapon", False)
        ])
    
    def __str__(self):
        return "{} [{}]".format(self.name, self.id)
    
    def compare(self, other):
        MwRecord.compare(self, other, ["model", "name", "weight", "value", "type", "health", "speed", "reach", "enchantment", "chop_min", "chop_max", "slash_min", "slash_max", "thrust_min", "thrust_max", "ignore_normal_weapon_resistance", "silver", "icon", "enchanting", "script"])