import mwglobals
from mwrecord import MwRecord


class MwLEVI(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
        self.id_ = ''
        self.calc_less_than_pc_level = False
        self.calc_each_item = False
        self.chance_none = 0
        self.items = []

    def load(self):
        self.id_ = self.parse_string('NAME')
        flags = self.parse_uint('DATA')
        self.calc_less_than_pc_level = (flags & 0x1) == 0x1
        self.calc_each_item = (flags & 0x2) == 0x2
        self.chance_none = self.parse_uint('NNAM', length=1)

        self.items = [MwLEVIItem(self.parse_string('INAM', index=i),
                                 self.parse_uint('INTV', index=i, length=2))
                      for i in range(self.num_subrecords('INAM'))]

        mwglobals.object_ids[self.id_] = self

    def record_details(self):
        return MwRecord.format_record_details(self, [
            ("|ID|", 'id_'),
            ("\n|Calculate from all levels <= PC's level|", 'calc_less_than_pc_level', False),
            ("\n|Calculate for each item in count|", 'calc_each_item', False),
            ("\n|Chance None|", 'chance_none'),
            ("\n|Items|", 'items', [])
        ])

    def __str__(self):
        return self.id_

    def diff(self, other):
        diff = [MwRecord.diff(self, other, ['calc_less_than_pc_level', 'calc_each_item', 'chance_none'])]

        item_details1 = [str(item) for item in self.items]
        item_details2 = [str(item) for item in other.items]

        for item2 in item_details2:
            if item2 not in item_details1:
                diff.append(f"\n{self}: Added {item2}")

        for item1 in item_details1:
            if item1 not in item_details2:
                diff.append(f"\n{self}: Removed {item1}")

        return ''.join(diff)


class MwLEVIItem:
    def __init__(self, id_, level):
        self.id_ = id_
        self.level = level

    def __str__(self):
        return f"{mwglobals.readable_object(self.id_)} (Lvl {self.level})"

    def __repr__(self):
        return str(self)
