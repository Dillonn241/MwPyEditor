from mwpyeditor.core import mwglobals
from mwpyeditor.core.mwrecord import MwRecord


class MwREGN(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
        self.id_ = ''
        self.name = ''
        self.weather_chances = []
        self.sleep_creature = None
        self.map_red = 0
        self.map_blue = 0
        self.map_green = 0
        self.sounds = {}

    def load(self):
        self.id_ = self.parse_string('NAME')
        self.name = self.parse_string('FNAM')

        self.weather_chances = [self.parse_uint('WEAT', index=i, start=i, length=1)
                                for i in range(self.num_subrecords('WEAT'))]

        self.sleep_creature = self.parse_string('BNAM')
        self.map_red = self.parse_uint('CNAM', length=1)
        self.map_blue = self.parse_uint('CNAM', start=1, length=1)
        self.map_green = self.parse_uint('CNAM', start=2, length=1)

        self.sounds = {self.parse_string('SNAM', index=i, length=16):
                       self.parse_uint('SNAM', index=i, start=32, length=1)
                       for i in range(self.num_subrecords('SNAM'))}

        mwglobals.object_ids[self.id_] = self

    def weather_chance_from_name(self, weather):
        if weather in mwglobals.WEATHERS:
            return self.weather_chances[mwglobals.WEATHERS.index(weather)]

    def record_details(self):
        return MwRecord.format_record_details(self, [
            ("|Name|", '__str__'),
            ("\n|Weather Chances|", 'weather_chances', []),
            ("\n|Sleep Creature|", 'sleep_creature'),
            ("\n|Map Color|", 'map_red'), (", {}", 'map_green'), (", {}", 'map_blue'),
            ("\n|Sounds|", 'sounds', {})
        ])

    def __str__(self):
        return f"{self.name} [{self.id_}]"

    def diff(self, other):
        return MwRecord.diff(self, other, ['name', 'weather_chances', 'sleep_creature', 'map_red', 'map_blue',
                                           'map_green', 'sounds'])
