import sys
import time

from mwpyeditor.core import mwplugin, mwglobals, mwjobs
from mwpyeditor.core.mwplugin import load_plugin
from mwpyeditor.record import mwalch, mwcell, mwench, mwland, mwspel, mwnpc_


def init_settings():
    """Change settings for which data is loaded in and how much of it is processed."""

    """
    Record types loaded by default for every plugin. Options:
        RECORDS_ALL      -- all types
        RECORDS_NODIAL   -- all types except: DIAL, INFO
        RECORDS_MOST     -- all types except: DIAL, INFO, CELL, LAND
        RECORDS_REFS     -- RECORDS_MIN, CELL, and anything that can be placed as a ref
        RECORDS_ITEMS    -- RECORDS_MIN, CONT, CREA, NPC_, LEVI, CELL, and items that can be held in inventories
        RECORDS_MIN      -- minimum types required for autocalc: MGEF, CLAS, RACE, SKIL
        RECORDS_DIALOGUE -- DIAL and INFO
        RECORDS_NONE     -- nothing except for TES3, which is always loaded
    """
    mwglobals.default_records = mwglobals.RECORDS_ALL

    """Expand initial list above."""
    mwglobals.default_records += []

    """Automatically load the same record types for a plugin's ESM master files, esp. Morrowind and expansions."""
    mwplugin.auto_load_masters = False

    """Process large data for CELL and LAND."""
    mwcell.init_references = True  # statics and other references placed in the world
    mwland.init_lod = False  # lod to show global map
    mwland.init_terrain = False  # normals, heights, colors, and textures of landscape (long load time)


def init_plugins():
    """Choose common plugins to load for TR and PT devs. Versions likely out of date."""

    """Vanilla"""
    # load_plugin('Morrowind.esm')
    # load_plugin('Tribunal.esm')
    # load_plugin('Bloodmoon.esm')

    """DLC"""
    # load_plugin('adamantiumarmor.esp')
    # load_plugin('AreaEffectArrows.esp')
    # load_plugin('bcsounds.esp')
    # load_plugin('EBQ_Artifact.esp')
    # load_plugin('entertainers.esp')
    # load_plugin('LeFemmArmor.esp')
    # load_plugin('master_index.esp')
    # load_plugin('Siege at Firemoth.esp')

    """Tamriel_Data"""
    # load_plugin('Tamriel_Data.esm')
    # load_plugin('TD_Addon.esp')

    """Tamriel Rebuilt"""
    # load_plugin('TR_Mainland.esp')
    # load_plugin('TR_Factions.esp')
    # load_plugin('TR_Travels.esp')
    # load_plugin('TR_Travels_(Preview_and_Mainland).esp')
    # load_plugin('TR_RorynsBluff_v0246.ESP')
    # load_plugin('TR_ArmunAshlands_v0069.ESP')
    # load_plugin('TR_SouthernVelothis_v.0013.esp')
    # load_plugin('TR_ThirrValley_v0075.ESP')
    # load_plugin('TR_ShipalShin_v0004.ESP')
    # load_plugin('TR_RestExterior.ESP')

    """Skyrim: Home of the Nords"""
    # load_plugin('Sky_Main_2021_10_08.ESP')
    # load_plugin('Sky_Markarth_2021-10-29.ESP')
    # load_plugin('Sky_Falkheim_2021_10_30.ESP')

    """Province: Cyrodiil"""
    # load_plugin('Cyrodiil_Main_2021_06_27.esp')
    # load_plugin('PC_Anvil_v0082.esp')
    # load_plugin('PC_Sutch_v0018.ESP')


def testing_area():
    """
    Anything put here is executed after settings and plugins are initialized. You can load additional plugins, run
    jobs, or anything else not possible through command line args (you can run those too).
    """

    """Jani's Jobs"""
    # mwjobs.find_creatures(file='files/SHOTN_Creas.csv')
    # mwjobs.exterior_doors(file='files/PC_Doors.csv')
    # mwjobs.exterior_doors(file='files/SHOTN_Doors.csv')
    # mwjobs.exterior_doors(file='files/TR_Doors.csv')
    # mwjobs.ref_map(file='files/SHOTN_Doors.csv', img='files/cellexp/SHOTN_CellExport.png', top=23, bottom=-3, left=-120, right=-94)
    # mwjobs.ref_map(file='files/PC_Doors.csv', img='files/cellexp/PC_CellExport.png', top=-35, bottom=-58, left=-141, right=-108)
    # mwjobs.ref_map(file='files/TR_Doors.csv', img='files/cellexp/TR_CellExport.png', top=29, bottom=-59, left=-39, right=49)
    # mwjobs.dump_dialogue(file='files/Dump.csv')
    dump = mwjobs.choice_tree()
    dump.to_csv('files/Dump.csv', index=False, header=True)

    """Start"""
    pass


"""
IGNORE AFTER THIS
"""


def main():
    start_time = time.time()

    with open('mwpyeditor_settings.txt') as file:
        line = file.readline().split('=')
        setattr(sys.modules['mwpyeditor.core.mwglobals'], line[0], line[1])
    init_settings()
    init_plugins()
    testing_area()
    print()

    if len(sys.argv) > 2 or '-h' in sys.argv or '--help' in sys.argv:
        args = mwplugin.init_args()
        mwplugin.handle_args(args)

    time_spent = time.time() - start_time
    print(f"\n** Time spent: {time_spent:.3f} seconds **")


if __name__ == '__main__':
    main()
