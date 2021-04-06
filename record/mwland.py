from core import mwglobals
from core.mwrecord import MwRecord

init_lod = False
init_terrain = False


class MwLAND(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
        self.lod_loaded = False
        self.terrain_loaded = False
        self.cell = None
        self.grid_x = 0
        self.grid_y = 0
        self.lod_heights = None
        self.normals = None
        self.heights = None
        self.height_offset = None
        self.colors = None
        self.textures = None

    def load(self):
        self.grid_x = self.parse_int('INTV')
        self.grid_y = self.parse_int('INTV', start=4)
        if (self.grid_x, self.grid_y) in mwglobals.exterior_cells:
            cell = mwglobals.exterior_cells[(self.grid_x, self.grid_y)]
            cell.land = self
            self.cell = cell
        if init_lod:
            self.load_lod()
        if init_terrain:
            self.load_terrain()

    def load_lod(self):
        if 'WNAM' in self.subrecords:
            self.lod_heights = [self.parse_int('WNAM', start=i, length=1)
                                for i in range(mwglobals.LAND_NUM_LOD_VERTS)]
        self.lod_loaded = True

    def load_terrain(self):
        if 'VNML' in self.subrecords:
            self.normals = [(self.parse_int('VNML', start=i * 3, length=1),  # x
                             self.parse_int('VNML', start=i * 3 + 1, length=1),  # y
                             self.parse_int('VNML', start=i * 3 + 2, length=1))  # z
                            for i in range(mwglobals.LAND_NUM_VERTS)]

        if 'VHGT' in self.subrecords:
            self.height_offset = self.parse_float('VHGT')
            self.heights = [self.parse_int('VHGT', start=4 + i, length=1)
                            for i in range(mwglobals.LAND_SIZE ** 2)]
            self.heights[0] += self.height_offset
            for i in range(1, len(self.heights)):
                prev_offset = mwglobals.LAND_SIZE if i % mwglobals.LAND_SIZE == 0 else 1
                self.heights[i] += self.heights[i - prev_offset]

        if 'VCLR' in self.subrecords:
            self.colors = [(self.parse_int('VCLR', start=i * 3, length=1),  # red
                            self.parse_int('VCLR', start=i * 3 + 1, length=1),  # green
                            self.parse_int('VCLR', start=i * 3 + 2, length=1))  # blue
                           for i in range(mwglobals.LAND_NUM_VERTS)]

        if 'VTEX' in self.subrecords:
            self.textures = [self.parse_int('VTEX', start=i * 2, length=2)
                             for i in range(mwglobals.LAND_NUM_TEXTURES)]

        self.terrain_loaded = True

    def record_details(self):
        string = [f"|Cell|    {self}"]
        if self.lod_loaded:
            string.append(MwRecord.format_record_details(self, [
                ("\n|LOD Heights|", 'lod_heights')
            ]))
        if self.terrain_loaded:
            string.append(MwRecord.format_record_details(self, [
                ("\n|Normals|", 'normals'),
                ("\n|Heights|", 'heights'),
                ("\n|Colors|", 'colors'),
                ("\n|Textures|", 'textures')
            ]))
        return ''.join(string)

    def __str__(self):
        if self.cell:
            return str(self.cell)
        return f"Wilderness [{self.grid_x},{self.grid_y}]"

    def get_id(self):
        return str(self)

    def diff(self, other):
        if self.lod_loaded:
            return MwRecord.diff(self, other, ['lod_heights'])
        if self.terrain_loaded:
            return MwRecord.diff(self, other, ['normals', 'heights', 'colors', 'textures'])
