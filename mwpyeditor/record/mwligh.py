from mwpyeditor.core import mwglobals
from mwpyeditor.core.mwrecord import MwRecord


class MwLIGH(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
        self.id_ = ''
        self.model = ''
        self.name = None
        self.icon = None
        self.weight = 0.0
        self.value = 0
        self.time = 0
        self.radius = 0
        self.red = 0
        self.green = 0
        self.blue = 0
        self.dynamic = False
        self.can_carry = False
        self.negative = False
        self.flicker = False
        self.fire = False
        self.off_default = False
        self.flicker_slow = False
        self.pulse = False
        self.pulse_slow = False
        self.sound_id = None
        self.script = None

    def load(self):
        self.id_ = self.parse_string('NAME')
        self.model = self.parse_string('MODL')
        self.name = self.parse_string('FNAM')
        self.icon = self.parse_string('ITEX')

        self.weight = self.parse_float('LHDT')
        self.value = self.parse_uint('LHDT', start=4)
        self.time = self.parse_int('LHDT', start=8)
        self.radius = self.parse_uint('LHDT', start=12)
        self.red = self.parse_uint('LHDT', start=16, length=1)
        self.green = self.parse_uint('LHDT', start=17, length=1)
        self.blue = self.parse_uint('LHDT', start=18, length=1)
        flags = self.parse_uint('LHDT', start=20)
        self.dynamic = (flags & 0x1) == 0x1
        self.can_carry = (flags & 0x2) == 0x2
        self.negative = (flags & 0x4) == 0x4
        self.flicker = (flags & 0x8) == 0x8
        self.fire = (flags & 0x10) == 0x10
        self.off_default = (flags & 0x20) == 0x20
        self.flicker_slow = (flags & 0x40) == 0x40
        self.pulse = (flags & 0x80) == 0x80
        self.pulse_slow = (flags & 0x100) == 0x100

        self.sound_id = self.parse_string('SNAM')
        self.script = self.parse_string('SCRI')

        mwglobals.object_ids[self.id_] = self

    def wiki_entry(self):
        return (f"""|-\n
                |[[File:TD3-icon-light-{self.icon}.png]]\n
                |{{{{Small|{self.id_}}}}}\n
                |{mwglobals.decimal_format(self.weight)}||{self.value}||{{{{BG|#
                {self.red:02X}{self.green:02X}{self.blue:02X}}}}}|'''{self.radius}'''||{self.time}""")

    def record_details(self):
        return MwRecord.format_record_details(self, [
            ("|Name|", '__str__'),
            ("\n|Model|", 'model'),
            ("\n|Icon|", 'icon'),
            ("\n|Weight|    {:.2f}", 'weight'),
            ("\n|Value|", 'value'),
            ("\n|Time|", 'time'),
            ("\n|Radius|", 'radius'),
            ("\n|Color|", 'red'), (", {}", 'green'), (", {}", 'blue'),
            ("\n|Dynamic|", 'dynamic', False),
            ("\n|Can Carry|", 'can_carry', False),
            ("\n|Negative|", 'negative', False),
            ("\n|Flicker|", 'flicker', False),
            ("\n|Fire|", 'fire', False),
            ("\n|Off by Default|", 'off_default', False),
            ("\n|Flicker Slow|", 'flicker_slow', False),
            ("\n|Pulse|", 'pulse', False),
            ("\n|Pulse Slow|", 'pulse_slow', False),
            ("\n|Sound ID|", 'sound_id'),
            ("\n|Script|", 'script')
        ])

    def __str__(self):
        return f"{self.name} [{self.id_}]" if self.can_carry else f"[{self.id_}]"

    def diff(self, other):
        return MwRecord.diff(self, other, ['model', 'name', 'icon', 'weight', 'value', 'time', 'radius', 'red', 'green',
                                           'blue', 'dynamic', 'can_carry', 'negative', 'flicker', 'fire', 'off_default',
                                           'flicker_slow', 'pulse', 'pulse_slow', 'sound_id', 'script'])
