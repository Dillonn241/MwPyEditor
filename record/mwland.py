import mwglobals
from mwrecord import MwRecord

init_lod = False
init_terrain = False

class MwLAND(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
        self.lod_loaded = False
        self.terrain_loaded = False
    
    def load(self):
        self.grid_x = self.get_subrecord_int("INTV", start=0, length=4)
        self.grid_y = self.get_subrecord_int("INTV", start=4, length=4)
        if (self.grid_x, self.grid_y) in mwglobals.exterior_cells:
            cell = mwglobals.exterior_cells[(self.grid_x, self.grid_y)]
            cell.land = self
            self.cell = cell
        if init_lod:
            self.load_lod()
        if init_terrain:
            self.load_terrain()
    
    def load_lod(self):
        self.lod_heights = [0] * mwglobals.LAND_NUM_LOD_VERTS
        if "WNAM" in self.subrecords:
            for i in range(mwglobals.LAND_NUM_LOD_VERTS):
                self.lod_heights[i] = self.get_subrecord_int("WNAM", start=i, length=1)
        
        self.lod_loaded = True
    
    def load_terrain(self):
        self.normals = [(0, 0, 127)] * mwglobals.LAND_NUM_VERTS
        if "VNML" in self.subrecords:
            for i in range(mwglobals.LAND_NUM_VERTS):
                x = self.get_subrecord_int("VNML", start=i * 3, length=1)
                y = self.get_subrecord_int("VNML", start=i * 3 + 1, length=1)
                z = self.get_subrecord_int("VNML", start=i * 3 + 2, length=1)
                self.normals[i] = (x, y, z)
        
        self.heights = [mwglobals.LAND_DEFAULT_HEIGHT] * mwglobals.LAND_NUM_VERTS
        if "VHGT" in self.subrecords:
            self.height_offset = self.get_subrecord_float("VHGT", start=0, length=4)
            row_offset = self.height_offset
            for y in range(mwglobals.LAND_SIZE):
                row_offset += self.get_subrecord_int("VHGT", start=4 + y * mwglobals.LAND_SIZE, length=1)
                self.heights[y * mwglobals.LAND_SIZE] = row_offset
                col_offset = row_offset
                for x in range(1, mwglobals.LAND_SIZE):
                    col_offset += self.get_subrecord_int("VHGT", start=4 + y * mwglobals.LAND_SIZE + x, length=1)
                    self.heights[x + y * mwglobals.LAND_SIZE] = col_offset
        
        self.colors = [(255, 255, 255)] * mwglobals.LAND_NUM_VERTS
        if "VCLR" in self.subrecords:
            for i in range(mwglobals.LAND_NUM_VERTS):
                r = self.get_subrecord_int("VCLR", start=i * 3, length=1)
                g = self.get_subrecord_int("VCLR", start=i * 3 + 1, length=1)
                b = self.get_subrecord_int("VCLR", start=i * 3 + 2, length=1)
                self.colors[i] = (r, g, b)
        
        self.textures = [0] * mwglobals.LAND_NUM_TEXTURES
        if "VTEX" in self.subrecords:
            for i in range(mwglobals.LAND_NUM_TEXTURES):
                self.textures[i] = self.get_subrecord_int("VTEX", start=i * 2, length=2)
        
        self.terrain_loaded = True
    
    """def save(self):
        self.set_subrecord_int(self.grid_x, "INTV", start=0, length=4)
        self.set_subrecord_int(self.grid_y, "INTV", start=4, length=4)
        
        if self.lod_loaded:
            for i in range(mwglobals.LAND_NUM_LOD_VERTS):
                self.set_subrecord_int(self.lod_heights[i], "WNAM", start=i, length=1)
        
        if self.terrain_loaded:
            if "VNML" in self.subrecords:
                for i in range(mwglobals.LAND_NUM_VERTS):
                    self.set_subrecord_int(self.normals[i][0], "VNML", start=i * 3, length=1)
                    self.set_subrecord_int(self.normals[i][1], "VNML", start=i * 3 + 1, length=1)
                    self.set_subrecord_int(self.normals[i][2], "VNML", start=i * 3 + 2, length=1)
            
            if "VHGT" in self.subrecords:
                self.set_subrecord_float(self.height_offset, "VHGT", start=0, length=4)
                last_row = self.height_offset
                for y in range(mwglobals.LAND_SIZE):
                    diff = int(self.heights[y * mwglobals.LAND_SIZE] - last_row)
                    last_row = self.heights[y * mwglobals.LAND_SIZE]
                    self.set_subrecord_int(diff, "VHGT", start=4 + y * mwglobals.LAND_SIZE, length=1)
                    last_col = last_row
                    for x in range(1, mwglobals.LAND_SIZE):
                        diff = int(self.heights[x + y * mwglobals.LAND_SIZE] - last_col)
                        last_col = self.heights[x + y * mwglobals.LAND_SIZE]
                        self.set_subrecord_int(diff, "VHGT", start=4 + y * mwglobals.LAND_SIZE + x, length=1)
            
            if "VCLR" in self.subrecords:
                for i in range(mwglobals.LAND_NUM_VERTS):
                    self.set_subrecord_int(self.colors[i][0], "VCLR", start=i * 3, length=1)
                    self.set_subrecord_int(self.colors[i][1], "VCLR", start=i * 3 + 1, length=1)
                    self.set_subrecord_int(self.colors[i][2], "VCLR", start=i * 3 + 2, length=1)
            
            if "VTEX" in self.subrecords:
                for i in range(mwglobals.LAND_NUM_TEXTURES):
                    self.set_subrecord_int(self.textures[i], "VTEX", start=i * 2, length=2)"""
    
    def record_details(self):
        string = "|Cell|    " + str(self)
        if self.lod_loaded:
            string += MwRecord.format_record_details(self, [
            ("\n|LOD Heights|", "lod_heights")
            ])
        if self.terrain_loaded:
            string += MwRecord.format_record_details(self, [
            ("\n|Normals|", "normals"),
            ("\n|Heights|", "heights"),
            ("\n|Colors|", "colors"),
            ("\n|Textures|", "textures")
            ])
        return string
    
    def __str__(self):
        if hasattr(self, "cell"):
            return str(self.cell)
        return "Wilderness [{},{}]".format(self.grid_x, self.grid_y)
    
    def get_id(self):
        return str(self)
    
    def diff(self, other):
        if self.lod_loaded:
            MwRecord.diff(self, other, ["lod_heights"])
        if self.terrain_loaded:
            MwRecord.diff(self, other, ["normals", "heights", "colors", "textures"])