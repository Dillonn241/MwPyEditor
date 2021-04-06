from mwpyeditor.core.mwrecord import MwRecord


class MwLTEX(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
        self.id_ = ''
        self.index = 0
        self.texture = ''

    def load(self):
        self.id_ = self.parse_string('NAME')
        self.index = self.parse_uint('INTV')
        self.texture = self.parse_string('DATA')

    def save(self):
        self.clear_subrecords()
        self.save_deleted()
        self.add_string(self.id_, 'NAME')
        self.add_uint(self.index, 'INTV')
        self.add_string(self.texture, 'DATA')

    def record_details(self):
        return MwRecord.format_record_details(self, [
            ("|ID|", 'id_'),
            ("\n|Index|", 'index'),
            ("\n|Texture|", 'texture')
        ])

    def __str__(self):
        return self.id_

    def diff(self, other):
        return MwRecord.diff(self, other, ['index', 'texture'])
