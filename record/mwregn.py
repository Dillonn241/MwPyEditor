from mwrecord import MwRecord
import mwglobals

class MwREGN(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
    
    def load(self):
        self.id = self.get_subrecord_string("NAME")
        self.name = self.get_subrecord_string("FNAM")
        self.weather_chances = {}
        for i in range(self.num_subrecords("WEAT")):
            self.weather_chances[mwglobals.WEATHERS[i]] = self.get_subrecord_int("WEAT", index=i, start=i, length=1, signed=False)
        self.sleep_creature = self.get_subrecord_string("BNAM")
        self.map_red = self.get_subrecord_int("CNAM", start=0, length=1, signed=False)
        self.map_blue = self.get_subrecord_int("CNAM", start=1, length=1, signed=False)
        self.map_green = self.get_subrecord_int("CNAM", start=2, length=1, signed=False)
        self.sounds = {}
        for i in range(self.num_subrecords("SNAM")):
            sound_id = self.get_subrecord_string("SNAM", index=i, start=0, length=16)
            sound_chance = self.get_subrecord_int("SNAM", index=i, start=32, length=1, signed=False)
            self.sounds[sound_id] = sound_chance
        mwglobals.object_ids[self.id] = self
    
    def record_details(self):
        return "|Name|    " + str(self) + MwRecord.format_record_details(self, [
        ("\n|Weather Chances|", "weather_chances", {}),
        ("\n|Sleep Creature|", "sleep_creature"),
        ("\n|Map Color|", "map_red"), (", {}", "map_green"), (", {}", "map_blue"),
        ("\n|Sounds|", "sounds", {})
        ])
    
    def __str__(self):
        return "{} [{}]".format(self.name, self.id)
    
    def diff(self, other):
        MwRecord.diff(self, other, ["name", "weather_chances", "sleep_creature", "map_red", "map_blue", "map_green", "sounds"])