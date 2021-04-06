from core import mwglobals
from core.mwrecord import MwRecord


class MwSCPT(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
        self.id_ = ''
        self.num_shorts = 0
        self.num_longs = 0
        self.num_floats = 0
        self.local_vars = None
        self.data = None
        self.text = None

    def load(self):
        self.id_ = self.parse_string('SCHD', length=32)
        self.num_shorts = self.parse_uint('SCHD', start=32)
        self.num_longs = self.parse_uint('SCHD', start=36)
        self.num_floats = self.parse_uint('SCHD', start=40)

        self.local_vars = self.parse_string('SCVR')
        if self.local_vars:
            self.local_vars = self.local_vars.split("\x00")
        self.data = self.get_subrecord_data('SCDT')
        self.text = self.parse_string('SCTX')

        mwglobals.object_ids[self.id_] = self

    def record_details(self):
        return MwRecord.format_record_details(self, [
            ("|ID|", 'id_'),
            ("\n|Num Shorts|", 'num_shorts'),
            ("\n|Num Longs|", 'num_longs'),
            ("\n|Num Floats|", 'num_floats'),
            ("\n|Local Vars|", 'local_vars', []),
            ("\n|Text|", 'text')
        ])

    def __str__(self):
        return self.id_

    def diff(self, other):
        return MwRecord.diff(self, other, ['num_shorts', 'num_longs', 'num_floats', 'local_vars', 'text'])
