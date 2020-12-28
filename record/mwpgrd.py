from mwrecord import MwRecord
import mwglobals

class MwPGRD(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
    
    def load(self):
        self.id = self.get_subrecord_string("NAME")
        self.grid_x = self.get_subrecord_int("DATA", start=0, length=4)
        self.grid_y = self.get_subrecord_int("DATA", start=4, length=4)
        if self.id in mwglobals.interior_cells:
            cell = mwglobals.interior_cells[self.id]
            cell.pgrd = self
            self.cell = cell
        elif (self.grid_x, self.grid_y) in mwglobals.exterior_cells:
            cell = mwglobals.exterior_cells[(self.grid_x, self.grid_y)]
            cell.pgrd = self
            self.cell = cell
        
        self.num_points = self.get_subrecord_int("DATA", start=10, length=2)
        self.points = []
        for i in range(self.num_points):
            point = MwPGRDPoint()
            point.x = self.get_subrecord_int("PGRP", start=i * 16, length=4)
            point.y = self.get_subrecord_int("PGRP", start=4 + i * 16, length=4)
            point.z = self.get_subrecord_int("PGRP", start=8 + i * 16, length=4)
            point.user = self.get_subrecord_int("PGRP", start = 12 + i * 16, length=1, signed=False) == 1
            point.num_connections = self.get_subrecord_int("PGRP", start = 13 + i * 16, length=1, signed=False)
            self.points += [point]
        
        self.edges = []
        if "PGRC" in self.subrecords:
            num_connections = int(len(self.get_subrecord("PGRC").data) / 8)
            for i in range(num_connections):
                point1 = self.points[self.get_subrecord_int("PGRC", start=i * 8, length=4)]
                point2 = self.points[self.get_subrecord_int("PGRC", start=4 + i * 8, length=4)]
                self.edges += [(point1, point2)]
    
    def record_details(self):
        return "|Name|    " + str(self) + MwRecord.format_record_details(self, [
        ("\n|Num Points|", "num_points"),
        ("\n|Points|", "points", []),
        ("\n|Edges|", "edges", [])
        ])
    
    def __str__(self):
        if self.grid_x == 0 and self.grid_y == 0 and self.id != "Ashlands Region":
            return self.id
        return "{} [{},{}]".format(self.id, self.grid_x, self.grid_y)
    
    def get_id(self):
        return str(self)
    
    def diff(self, other):
        MwRecord.diff(self, other, ["num_points", "points", "edges"])

class MwPGRDPoint:
    def __str__(self):
        return "({}, {}, {})".format(self.x, self.y, self.z)
    
    def __repr__(self):
        return str(self)