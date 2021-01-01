import mwglobals
from mwrecord import MwRecord

class MwLIGH(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
    
    def load(self):
        self.id = self.get_subrecord_string("NAME")
        self.model = self.get_subrecord_string("MODL")
        self.name = self.get_subrecord_string("FNAM")
        self.icon = self.get_subrecord_string("ITEX")
        
        self.weight = self.get_subrecord_float("LHDT", start=0, length=4)
        self.value = self.get_subrecord_int("LHDT", start=4, length=4)
        self.time = self.get_subrecord_int("LHDT", start=8, length=4)
        self.radius = self.get_subrecord_int("LHDT", start=12, length=4)
        self.red = self.get_subrecord_int("LHDT", start=16, length=1, signed=False)
        self.green = self.get_subrecord_int("LHDT", start=17, length=1, signed=False)
        self.blue = self.get_subrecord_int("LHDT", start=18, length=1, signed=False)
        flags = self.get_subrecord_int("LHDT", start=20, length=4)
        self.dynamic = (flags & 0x1) == 0x1
        self.can_carry = (flags & 0x2) == 0x2
        self.negative = (flags & 0x4) == 0x4
        self.flicker = (flags & 0x8) == 0x8
        self.fire = (flags & 0x10) == 0x10
        self.off_default = (flags & 0x20) == 0x20
        self.flicker_slow = (flags & 0x40) == 0x40
        self.pulse = (flags & 0x80) == 0x80
        self.pulse_slow = (flags & 0x100) == 0x100
        
        self.sound_id = self.get_subrecord_string("SNAM")
        self.script = self.get_subrecord_string("SCRI")
        mwglobals.object_ids[self.id] = self
    
    def wiki_entry(self):
        return "|-\n" \
        "|[[File:TD3-icon-light-" + self.icon + ".png]]\n" \
        "|{{Small|" + self.id + "}}\n" \
        "|" + mwglobals.decimal_format(self.weight) + "||" + str(self.value) + "||{{BG|#" + "{:02X}{:02X}{:02X}".format(self.red, self.green, self.blue) + "}}|'''" + str(self.radius) + "'''||" + str(self.time)
    
    def record_details(self):
        return "|Name|    " + str(self) + MwRecord.format_record_details(self, [
        ("\n|Radius|", "radius"),
        ("\n|Script|", "script"),
        ("\n|Can Carry|", "can_carry", False),
        ("\n|Off by Default|", "off_default", False),
        ("\n|Weight|    {:.2f}", "weight"),
        ("\n|Value|", "value"),
        ("\n|Time|", "time"),
        ("\n|Model|", "model"),
        ("\n|Icon|", "icon"),
        ("\n|Fire|", "fire", False),
        ("\n|Negative|", "negative", False),
        ("\n|Dynamic|", "dynamic", False),
        ("\n|Sound ID|", "sound_id"),
        ("\n|Color|", "red"), (", {}", "green"), (", {}", "blue"),
        ("\n|Flicker|", "flicker", False),
        ("\n|Flicker Slow|", "flicker_slow", False),
        ("\n|Pulse|", "pulse", False),
        ("\n|Pulse Slow|", "pulse_slow", False)
        ])
    
    def __str__(self):
        if self.can_carry:
            return "{} [{}]".format(self.name, self.id)
        return "[{}]".format(self.id)
    
    def diff(self, other):
        MwRecord.diff(self, other, ["model", "name", "icon", "weight", "value", "time", "radius", "red", "green", "blue", "dynamic", "can_carry", "negative", "flicker", "fire", "off_default", "flicker_slow", "pulse", "pulse_slow", "sound_id", "script"])