from core import mwglobals
from core.mwrecord import MwRecord


class MwMGEF(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
        self.id_ = 0
        self.school_id = 0
        self.base_cost = 0.0
        self.spellmaking = False
        self.enchanting = False
        self.negative = False
        self.red = 0
        self.green = 0
        self.blue = 0
        self.speed_x = 0.0
        self.size_x = 0.0
        self.size_cap = 0.0
        self.effect_icon = None
        self.particle_texture = None
        self.bolt_sound = None
        self.casting_sound = None
        self.hit_sound = None
        self.area_sound = None
        self.casting_visual = None
        self.bolt_visual = None
        self.hit_visual = None
        self.area_visual = None
        self.description = None
        self.target_skill = False
        self.target_attribute = False
        self.no_duration = False
        self.no_magnitude = False
        self.harmful = False
        self.continuous_vfx = False
        self.cast_self = False
        self.cast_touch = False
        self.cast_target = False
        self.uncapped_damage = False
        self.non_recastable = False
        self.unreflectable = False
        self.caster_linked = False

    def load(self):
        self.id_ = self.parse_int('INDX')

        self.school_id = self.parse_uint('MEDT')
        self.base_cost = self.parse_float('MEDT', start=4)
        flags = self.parse_uint('MEDT', start=8)
        self.spellmaking = (flags & 0x200) == 0x200
        self.enchanting = (flags & 0x400) == 0x400
        self.negative = (flags & 0x800) == 0x800
        self.red = self.parse_uint('MEDT', start=12)
        self.green = self.parse_uint('MEDT', start=16)
        self.blue = self.parse_uint('MEDT', start=20)
        self.speed_x = self.parse_float('MEDT', start=24)
        self.size_x = self.parse_float('MEDT', start=28)
        self.size_cap = self.parse_float('MEDT', start=32)

        self.effect_icon = self.parse_string('ITEX')
        self.particle_texture = self.parse_string('PTEX')
        self.bolt_sound = self.parse_string('BSND')
        self.casting_sound = self.parse_string('CSND')
        self.hit_sound = self.parse_string('HSND')
        self.area_sound = self.parse_string('ASND')
        self.casting_visual = self.parse_string('CVFX')
        self.bolt_visual = self.parse_string('BVFX')
        self.hit_visual = self.parse_string('HVFX')
        self.area_visual = self.parse_string('AVFX')
        self.description = self.parse_string('DESC')

        hard_flags = mwglobals.HARDCODED_FLAGS[self.id_]
        self.target_skill = (hard_flags & 0x1) == 0x1
        self.target_attribute = (hard_flags & 0x2) == 0x2
        self.no_duration = (hard_flags & 0x4) == 0x4
        self.no_magnitude = (hard_flags & 0x8) == 0x8
        self.harmful = (hard_flags & 0x10) == 0x10
        self.continuous_vfx = (hard_flags & 0x20) == 0x20
        self.cast_self = (hard_flags & 0x40) == 0x40
        self.cast_touch = (hard_flags & 0x80) == 0x80
        self.cast_target = (hard_flags & 0x100) == 0x100
        self.uncapped_damage = (hard_flags & 0x200) == 0x200
        self.non_recastable = (hard_flags & 0x400) == 0x400
        self.unreflectable = (hard_flags & 0x800) == 0x800
        self.caster_linked = (hard_flags & 0x1000) == 0x1000

    def get_name(self):
        return mwglobals.MAGIC_NAMES[self.id_]

    def get_school(self):
        return mwglobals.MAGIC_SCHOOLS[self.school_id]

    def set_school(self, value):
        if value in mwglobals.MAGIC_SCHOOLS:
            self.school_id = mwglobals.MAGIC_SCHOOLS.index(value)

    def get_magnitude_type(self):
        return get_magnitude_type(self.id_)

    def requires_attribute(self):
        return requires_attribute(self.id_)

    def requires_skill(self):
        return requires_skill(self.id_)

    def record_details(self):
        return MwRecord.format_record_details(self, [
            ("|Name|", '__str__'),
            ("\n|School|", 'get_school'),
            ("\n|Base Cost|    {:.2f}", 'base_cost'),
            ("\n|Spellmaking|", 'spellmaking', False),
            ("\n|Enchanting|", 'enchanting', False),
            ("\n|Lighting Negative|", 'negative', False),
            ("\n|Lighting Color|", 'red'), (", {}", 'green'), (", {}", 'blue'),
            ("\n|SpeedX|", 'speed_x'),
            ("\n|SizeX|", 'size_x'),
            ("\n|Size Cap|", 'size_cap'),
            ("\n|Effect Icon|", 'effect_icon'),
            ("\n|Particle Texture|", 'particle_texture'),
            ("\n|Bolt Sound|", 'bolt_sound'),
            ("\n|Casting Sound|", 'casting_sound'),
            ("\n|Hit Sound|", 'hit_sound'),
            ("\n|Area Sound|", 'area_sound'),
            ("\n|Casting Visual|", 'casting_visual'),
            ("\n|Bolt Visual|", 'bolt_visual'),
            ("\n|Hit Visual|", 'hit_visual'),
            ("\n|Area Visual|", 'area_visual'),
            ("\n|Description|", 'description'),
            ("\n|Target Skill|", 'target_skill', False),
            ("\n|Target Attribute|", 'target_attribute', False),
            ("\n|No Duration|", 'no_duration', False),
            ("\n|No Magnitude|", 'no_magnitude', False),
            ("\n|Harmful|", 'harmful', False),
            ("\n|Continuous VFX|", 'continuous_vfx', False),
            ("\n|Cast Self|", 'cast_self', False),
            ("\n|Cast Touch|", 'cast_touch', False),
            ("\n|Cast Target|", 'cast_target', False),
            ("\n|Uncapped Damage|", 'uncapped_damage', False),
            ("\n|Non Recastable|", 'non_recastable', False),
            ("\n|Unreflectable|", 'unreflectable', False),
            ("\n|Caster Linked|", 'caster_linked', False)
        ])

    def __str__(self):
        return f"{self.get_name()} [{self.id_}]"

    def diff(self, other):
        return MwRecord.diff(self, other, ['get_school', 'base_cost', 'spellmaking', 'enchanting', 'negative', 'red',
                                           'green', 'blue', 'speed_x', 'size_x', 'size_cap', 'effect_icon',
                                           'particle_texture', 'bolt_sound', 'casting_sound', 'hit_sound', 'area_sound',
                                           'casting_visual', 'bolt_visual', 'hit_visual', 'area_visual', 'description',
                                           'target_skill', 'target_attribute', 'no_duration', 'no_magnitude', 'harmful',
                                           'continuous_vfx', 'cast_self', 'cast_touch', 'cast_target',
                                           'uncapped_damage', 'non_recastable', 'unreflectable', 'caster_linked'])


def get_magnitude_type(effect_id):
    if has_no_magnitude(effect_id):
        return mwglobals.MagnitudeType.NONE
    if effect_id == 84:
        return mwglobals.MagnitudeType.TIMES_INT
    if effect_id == 59 or (64 <= effect_id <= 66):
        return mwglobals.MagnitudeType.FEET
    if effect_id == 118 or effect_id == 119:
        return mwglobals.MagnitudeType.LEVEL
    if ((28 <= effect_id <= 36) or (90 <= effect_id <= 99) or effect_id == 40 or effect_id == 47 or effect_id == 57 or
            effect_id == 68):
        return mwglobals.MagnitudeType.PERCENTAGE
    return mwglobals.MagnitudeType.POINTS


def has_no_duration(effect_id):
    return effect_id in [12, 13, 57, 60, 61, 62, 63, 69, 70, 71, 72, 73, 133]


def has_no_magnitude(effect_id):
    if effect_id < 102:
        return effect_id in [0, 2, 39, 45, 46, 58, 60, 61, 62, 63, 69, 70, 71, 72, 73]
    else:
        return effect_id not in [117, 118, 119, 135]


def requires_attribute(effect_id):
    return effect_id == 17 or effect_id == 22 or effect_id == 74 or effect_id == 79 or effect_id == 85


def requires_skill(effect_id):
    return effect_id == 21 or effect_id == 26 or effect_id == 78 or effect_id == 83 or effect_id == 89
