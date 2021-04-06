from mwpyeditor.core import mwglobals
from mwpyeditor.core.mwrecord import MwRecord
from mwpyeditor.record.mwlevi import MwLEVIItem


class MwLEVC(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
        self.id_ = ''
        self.calc_less_than_pc_level = False
        self.chance_none = 0
        self.creatures = []

    def load(self):
        self.id_ = self.parse_string('NAME')
        flags = self.parse_uint('DATA')
        self.calc_less_than_pc_level = (flags & 0x1) == 0x1
        self.chance_none = self.parse_uint('NNAM', length=1)

        self.creatures = [MwLEVIItem(self.parse_string('CNAM', index=i),
                                     self.parse_uint('INTV', index=i, length=2))
                          for i in range(self.num_subrecords('CNAM'))]

        mwglobals.object_ids[self.id_] = self

    def record_details(self):
        return MwRecord.format_record_details(self, [
            ("|ID|", 'id_'),
            ("\n|Calculate from all levels <= PC's level|", 'calc_less_than_pc_level', False),
            ("\n|Chance None|", 'chance_none'),
            ("\n|Creatures|", 'creatures', [])
        ])

    def __str__(self):
        return self.id_

    def diff(self, other):
        diff = [MwRecord.diff(self, other, ['calc_less_than_pc_level', 'chance_none'])]

        creature_details1 = [str(creature) for creature in self.creatures]
        creature_details2 = [str(creature) for creature in other.creatures]

        for creature2 in creature_details2:
            if creature2 not in creature_details1:
                diff.append(f"\n{self}: Added {creature2}")

        for creature1 in creature_details1:
            if creature1 not in creature_details2:
                diff.append(f"\n{self}: Removed {creature1}")

        return ''.join(diff)
