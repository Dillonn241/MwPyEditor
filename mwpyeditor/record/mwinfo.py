from mwpyeditor.core import mwglobals
from mwpyeditor.core.mwrecord import MwRecord


class MwINFO(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
        self.dial = None
        self.id_ = ''
        self.prev_id = ''
        self.next_id = ''
        self.disposition = None
        self.rank = None
        self.sex = None
        self.pc_rank = None
        self.actor = None
        self.race = None
        self.class_ = None
        self.faction = None
        self.cell = None
        self.pc_faction = None
        self.sound_file = None
        self.response = None
        self.func_var_filters = []
        self.result = None
        self.quest_name = None
        self.quest_finished = None
        self.quest_restart = None

    def load(self):
        self.id_ = self.parse_string('INAM')
        self.prev_id = self.parse_string('PNAM')
        self.next_id = self.parse_string('NNAM')

        self.disposition = self.parse_uint('DATA', start=4)
        self.rank = self.parse_uint('DATA', start=8, length=1)
        self.sex = self.parse_int('DATA', start=9, length=1)
        self.pc_rank = self.parse_uint('DATA', start=10, length=1)

        self.actor = self.parse_string('ONAM')
        self.race = self.parse_string('RNAM')
        self.class_ = self.parse_string('CNAM')
        self.faction = self.parse_string('FNAM')
        self.cell = self.parse_string('ANAM')
        self.pc_faction = self.parse_string('DNAM')
        self.sound_file = self.parse_string('SNAM')
        self.response = self.parse_string('NAME')

        self.func_var_filters = []
        func_var_filter = None
        for subrecord in self.ordered_subrecords:
            if subrecord.record_type == 'SCVR':
                func_var_filter = MwINFOFilter()
                func_var_filter.index = subrecord.parse_uint(length=1) - 48
                func_var_filter.type_id = subrecord.parse_uint(start=1, length=1) - 48
                if func_var_filter.type_id > 9:
                    func_var_filter.type_id -= 7
                func_var_filter.function_id = subrecord.parse_string(start=2, length=2)
                func_var_filter.operator_id = subrecord.parse_uint(start=4, length=1) - 48
                func_var_filter.name = subrecord.parse_string(start=5)
                self.func_var_filters.append(func_var_filter)
            elif subrecord.record_type == 'INTV':
                func_var_filter.intv = subrecord.parse_uint()
            elif subrecord.record_type == 'FLTV':
                func_var_filter.fltv = subrecord.parse_float()

        self.result = self.parse_string('BNAM')
        self.quest_name = self.parse_uint('QSTN') == 1
        self.quest_finished = self.parse_uint('QSTF') == 1
        self.quest_restart = self.parse_uint('QSTR') == 1

        mwglobals.info_ids[self.id_] = self

    def save(self):
        self.clear_subrecords()
        self.add_string(self.id_, 'INAM')
        self.add_string(self.prev_id, 'PNAM')
        self.add_string(self.next_id, 'NNAM')
        if not self.deleted:
            sub_data = self.add_subrecord('DATA')
            sub_data.add_uint(self.dial.type_id, length=1)
            sub_data.data += b'\x00\x00\x00'
            sub_data.add_uint(self.disposition)
            sub_data.add_uint(self.rank, length=1)
            sub_data.add_int(self.sex, length=1)
            sub_data.add_uint(self.pc_rank, length=1)
            sub_data.data += b'\x00'
            self.add_string(self.actor, 'ONAM')
            self.add_string(self.race, 'RNAM')
            self.add_string(self.class_, 'CNAM')
            self.add_string(self.faction, 'FNAM')
            self.add_string(self.cell, 'ANAM')
            self.add_string(self.pc_faction, 'DNAM')
            self.add_string(self.sound_file, 'SNAM')
        self.add_string(self.response, 'NAME', terminator=False)
        if not self.deleted:
            for func_var_filter in self.func_var_filters:
                sub_scvr = self.add_subrecord('SCVR')
                sub_scvr.add_uint(func_var_filter.index + 48, length=1)
                func_type = func_var_filter.type_id
                if func_type > 9:
                    func_type += 7
                sub_scvr.add_uint(func_type + 48, length=1)
                sub_scvr.add_string(func_var_filter.function_id, terminator=False)
                sub_scvr.add_uint(func_var_filter.operator_id + 48, length=1)
                sub_scvr.add_string(func_var_filter.name, terminator=False)
                if func_var_filter.intv is not None:
                    self.add_uint(func_var_filter.intv, 'INTV')
                elif func_var_filter.fltv is not None:
                    self.add_float(func_var_filter.fltv, 'FLTV')
            self.add_string(self.result, 'BNAM', terminator=False)
            if self.quest_name:
                self.add_uint(1, 'QSTN', length=1)
            elif self.quest_finished:
                self.add_uint(1, 'QSTF', length=1)
            elif self.quest_restart:
                self.add_uint(1, 'QSTR', length=1)
        self.save_deleted()

    def filter(self, actor='', race='', class_='', faction='', cell='', pc_faction=''):
        if actor != '' and actor != self.actor:
            return False
        if race != '' and race != self.race:
            return False
        if class_ != '' and class_ != self.class_:
            return False
        if faction != '' and faction != self.faction:
            return False
        if cell != '' and not (self.cell and self.cell.startswith(cell)):
            return False
        if pc_faction != '' and pc_faction != self.pc_faction:
            return False
        return True

    def record_details(self):
        if self.dial.type_id == 4:  # Journal
            disp_index = "Index"
            response_entry = "Entry"
        else:
            disp_index = "Disp"
            response_entry = "Response"
        return MwRecord.format_record_details(self, [
            (f"|{response_entry}|    {self.dial}: {{}}", 'response'),
            ("\n|ID|", 'id_'), ("    |Prev|", 'prev_id', ''), ("    |Next|", 'next_id', ''),
            (f"\n|{disp_index}|", 'disposition', 0),
            ("\n|Sex|", 'sex', -1),
            ("\n|Actor|", 'actor'),
            ("\n|Race|", 'race'),
            ("\n|Class|", 'class_'),
            ("\n|Faction|", 'faction'), ("    |Rank|", 'rank', -1),
            ("\n|Cell|", 'cell'),
            ("\n|PC Faction|", 'pc_faction'), ("    |PC Rank|", 'pc_rank', -1),
            ("\n|Sound Filename|", 'sound_file'),
            ("\n|Function/Variable|", 'func_var_filters', []),
            ("\n|Result|", 'result'),
            ("\n|Quest Name|", 'quest_name', False),
            ("\n|Quest Finished|", 'quest_finished', False),
            ("\n|Quest Restart|", 'quest_restart', False)
        ])

    def __str__(self):
        return f"{self.dial}: {self.response} [{self.id_}]"

    def __repr__(self):
        return str(self)

    def diff(self, other):
        return MwRecord.diff(self, other, ['prev_id', 'next_id', 'disposition', 'rank', 'sex', 'pc_rank', 'actor',
                                           'race', 'class_', 'faction', 'cell', 'pc_faction', 'sound_file', 'response',
                                           'func_var_filters', 'result', 'quest_name', 'quest_finished',
                                           'quest_restart'])


class MwINFOFilter:
    def __init__(self):
        self.index = None
        self.type_id = None
        self.function_id = None
        self.operator_id = None
        self.name = None
        self.intv = None
        self.fltv = None

    def get_type(self):
        return mwglobals.INFO_SCVR_TYPE[self.type_id]

    def get_function(self):
        if self.function_id[1] == "X":
            return self.name
        return mwglobals.INFO_SCVR_FUNCTION[int(self.function_id)]

    def get_operator(self):
        return mwglobals.INFO_SCVR_OPERATOR[self.operator_id]

    def get_value(self):
        if self.intv:
            return str(self.intv)
        if self.fltv:
            return str(self.fltv)

    def __str__(self):
        return f"{self.get_type()} {self.get_function()} {self.get_operator()} {self.get_value()}"

    def __repr__(self):
        return str(self)
