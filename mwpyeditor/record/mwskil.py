from mwpyeditor.core import mwglobals
from mwpyeditor.core.mwrecord import MwRecord


class MwSKIL(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
        self.id_ = 0
        self.governing_attribute_id = 0
        self.specialization_id = 0
        self.use_values = []
        self.description = None

    def load(self):
        self.id_ = self.parse_uint('INDX')

        self.governing_attribute_id = self.parse_uint('SKDT')
        self.specialization_id = self.parse_uint('SKDT', start=4)

        self.use_values = [self.parse_float('SKDT', start=8 + i * 4)
                           for i in range(4)]

        self.description = self.parse_string('DESC')

    def get_name(self):
        if 0 <= self.id_ < len(mwglobals.SKILLS):
            return mwglobals.SKILLS[self.id_]

    def set_name(self, value):
        if value in mwglobals.SKILLS:
            self.id_ = mwglobals.SKILLS.index(value)

    def get_governing_attribute(self):
        if 0 <= self.governing_attribute_id < len(mwglobals.ATTRIBUTES):
            return mwglobals.ATTRIBUTES[self.governing_attribute_id]

    def set_governing_attribute(self, value):
        if value in mwglobals.ATTRIBUTES:
            self.governing_attribute_id = mwglobals.ATTRIBUTES.index(value)

    def get_specialization(self):
        if 0 <= self.specialization_id < len(mwglobals.SPECIALIZATIONS):
            return mwglobals.SPECIALIZATIONS[self.specialization_id]

    def set_specialization(self, value):
        if value in mwglobals.SPECIALIZATIONS:
            self.specialization_id = mwglobals.SPECIALIZATIONS.index(value)

    def record_details(self):
        return MwRecord.format_record_details(self, [
            ("|Name|", 'get_name'), (" ({})", 'id_'),
            ("\n|Governing Attribute|", 'get_governing_attribute'),
            ("\n|Specialization|", 'get_specialization'),
            ("\n|Use Values|", 'use_values'),
            ("\n|Description|", 'description')
        ])

    def __str__(self):
        return f"{self.get_name()} [{self.id_}]"

    def diff(self, other):
        return MwRecord.diff(self, other, ['governing_attribute', 'specialization', 'use_values', 'description'])
