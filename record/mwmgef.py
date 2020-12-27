from mwrecord import MwRecord
import mwglobals

class MwMGEF(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
    
    def load(self):
        self.index = self.get_subrecord_int("INDX")
        self.name = mwglobals.game_settings["sEffect" + mwglobals.MAGIC_EFFECTS[self.index]]
        self.school = mwglobals.MAGIC_SCHOOLS[self.get_subrecord_int("MEDT", start=0, length=4)]
        self.base_cost = self.get_subrecord_float("MEDT", start=4, length=4)
        
        flags = self.get_subrecord_int("MEDT", start=8, length=4)
        self.spellmaking = (flags & 0x200) == 0x200
        self.enchanting = (flags & 0x400) == 0x400
        self.negative = (flags & 0x800) == 0x800
        hard_flags = mwglobals.HARDCODED_FLAGS[self.index]
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
        
        self.red = self.get_subrecord_int("MEDT", start=12, length=4)
        self.green = self.get_subrecord_int("MEDT", start=16, length=4)
        self.blue = self.get_subrecord_int("MEDT", start=20, length=4)
        self.speed_x = self.get_subrecord_float("MEDT", start=24, length=4)
        self.size_x = self.get_subrecord_float("MEDT", start=28, length=4)
        self.size_cap = self.get_subrecord_float("MEDT", start=32, length=4)
        
        self.effect_icon = self.get_subrecord_string("ITEX")
        self.particle_texture = self.get_subrecord_string("PTEX")
        self.bolt_sound = self.get_subrecord_string("BSND")
        self.casting_sound = self.get_subrecord_string("CSND")
        self.hit_sound = self.get_subrecord_string("HSND")
        self.area_sound = self.get_subrecord_string("ASND")
        self.casting_visual = self.get_subrecord_string("CVFX")
        self.bolt_visual = self.get_subrecord_string("BVFX")
        self.hit_visual = self.get_subrecord_string("HVFX")
        self.area_visual = self.get_subrecord_string("AVFX")
        self.description = self.get_subrecord_string("DESC")
    
    def get_magnitude_type(self):
        if self.no_magnitude:
            return mwglobals.MagnitudeType.NONE
        if self.index == 84:
            return mwglobals.MagnitudeType.TIMES_INT
        if self.index == 59 or (self.index >= 64 and self.index <= 66):
            return mwglobals.MagnitudeType.FEET
        if self.index == 118 or self.index == 119:
            return mwglobals.MagnitudeType.LEVEL
        if (self.index >= 28 and self.index <= 36) or (self.index >= 90 and self.index <= 99) or self.index == 40 or self.index == 47 or self.index == 57 or self.index == 68:
            return mwglobals.MagnitudeType.PERCENTAGE
        return mwglobals.MagnitudeType.POINTS
    
    def requires_attribute(self):
        return self.index == 17 or self.index == 22 or self.index == 74 or self.index == 79 or self.index == 85
    
    def requires_skill(self):
        return self.index == 21 or self.index == 26 or self.index == 78 or self.index == 83 or self.index == 89
    
    def record_details(self):
        return "|Name|    " + str(self) + MwRecord.format_record_details(self, [
        ("\n|School|", "school"),
        ("\n|Base Cost|    {:.2f}", "base_cost"),
        ("\n|Spellmaking|", "spellmaking", False),
        ("\n|Enchanting|", "enchanting", False),
        ("\n|Particle Texture|", "particle_texture"),
        ("\n|Effect Icon|", "effect_icon"),
        ("\n|Description|", "description"),
        ("\n|Casting Sound|", "casting_sound"),
        ("\n|Casting Visual|", "casting_visual"),
        ("\n|Bolt Sound|", "bolt_sound"),
        ("\n|Bolt Visual|", "bolt_visual"),
        ("\n|Hit Sound|", "hit_sound"),
        ("\n|Hit Visual|", "hit_visual"),
        ("\n|Area Sound|", "area_sound"),
        ("\n|Area Visual|", "area_visual"),
        ("\n|SpeedX|", "speed_x"),
        ("\n|SizeX|", "size_x"),
        ("\n|Size Cap|", "size_cap"),
        ("\n|Lighting Color|", "red"), (", {}", "green"), (", {}", "blue"),
        ("\n|Lighting Negative|", "negative", False),
        ("\n|Target Skill|", "target_skill", False),
        ("\n|Target Attribute|", "target_attribute", False),
        ("\n|No Duration|", "no_duration", False),
        ("\n|No Magnitude|", "no_magnitude", False),
        ("\n|Harmful|", "harmful", False),
        ("\n|Continuous VFX|", "continuous_vfx", False),
        ("\n|Cast Self|", "cast_self", False),
        ("\n|Cast Touch|", "cast_touch", False),
        ("\n|Cast Target|", "cast_target", False),
        ("\n|Uncapped Damage|", "uncapped_damage", False),
        ("\n|Non Recastable|", "non_recastable", False),
        ("\n|Unreflectable|", "unreflectable", False),
        ("\n|Caster Linked|", "caster_linked", False)
        ])
    
    def __str__(self):
        return "{} [{}]".format(self.name, self.index)
    
    def get_id(self):
        return self.index
    
    def compare(self, other):
        MwRecord.compare(self, other, ["name", "school", "base_cost", "spellmaking", "enchanting", "negative", "target_skill", "target_attribute", "no_duration", "no_magnitude", "harmful", "continuous_vfx", "cast_self", "cast_touch", "cast_target", "uncapped_damage", "non_recastable", "unreflectable", "caster_linked", "red", "green", "blue", "speed_x", "size_x", "size_cap", "effect_icon", "particle_texture", "bolt_sound", "casting_sound", "hit_sound", "area_sound", "casting_visual", "bolt_visual", "hit_visual", "area_visual", "description"])