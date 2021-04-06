from core import mwglobals
from core.mwrecord import MwRecord


class MwGMST(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
        self.id_ = ''
        self.value = None

    def load(self):
        self.id_ = self.parse_string('NAME')
        if 'FLTV' in self.subrecords:
            self.value = self.parse_float('FLTV')
        elif 'INTV' in self.subrecords:
            self.value = self.parse_int('INTV')
        else:
            self.value = self.parse_string('STRV')

        mwglobals.game_settings[self.id_] = self.value

    def save(self):
        self.clear_subrecords()
        self.add_string(self.id_, 'NAME', terminator=False)
        if type(self.value) == float:
            self.add_float(self.value, 'FLTV')
        elif type(self.value) == int:
            self.add_int(self.value, 'INTV')
        else:
            self.add_string(self.value, 'STRV', terminator=False)
        self.save_deleted()

    def set_game_setting(self, value):
        self.value = value
        mwglobals.game_settings[self.id_] = self.value

    def record_details(self):
        if 'FLTV' in self.subrecords:
            format_str = ':.4f'
        elif 'INTV' in self.subrecords:
            format_str = ':d'
        else:
            format_str = ''
        return MwRecord.format_record_details(self, [
            ("|ID|", 'id_'),
            ("\n|Type|", 'type'),
            (f"\n|Value|    {{{format_str}}}", 'value')
        ])

    def __str__(self):
        return f"{self.id_} = {self.value}"

    def diff(self, other):
        return MwRecord.diff(self, other, ['type', 'value'])
