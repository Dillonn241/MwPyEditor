import sys
import time

from mwpyeditor.core import mwplugin, mwglobals, mwjobs
from mwpyeditor.core.mwplugin import load_plugin
from mwpyeditor.record import mwcell, mwland


def init_settings():
    """Change settings for which data is loaded in and how much of it is processed."""

    """
    Record types loaded by default for every plugin. Options:
        RECORDS_ALL        -- all types
        RECORDS_NO_DIAL    -- all types except: DIAL, INFO
        RECORDS_MOST       -- all types except: DIAL, INFO, CELL, LAND
        RECORDS_REFS       -- RECORDS_AUTOCALC, CELL, and anything that can be placed as a ref
        RECORDS_ITEMS      -- RECORDS_AUTOCALC, CONT, CREA, NPC_, LEVI, CELL, and items that can be held in inventories
        RECORDS_ITEM_USAGE -- minimum types required for item usage job: CONT, CREA, NPC_, LEVI, CELL
        RECORDS_AUTOCALC   -- minimum types required for autocalc: MGEF, CLAS, RACE, SKIL
        RECORDS_DIALOGUE   -- DIAL and INFO
        RECORDS_NONE       -- nothing except for TES3, which is always loaded
    """
    mwglobals.default_records = mwglobals.RECORDS_DIALOGUE

    """Expand initial list above."""
    mwglobals.default_records += []

    """Automatically load the same record types for a plugin's ESM master files, esp. Morrowind and expansions."""
    mwplugin.auto_load_masters = False

    """Process large data for CELL and LAND."""
    mwcell.init_references = True  # statics and other references placed in the world
    mwland.init_lod = False  # lod to show global map
    mwland.init_terrain = False  # normals, heights, colors, and textures of landscape (long load time)


def init_plugins():
    """Choose common plugins to load for TR and PT devs."""

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

    """Tamriel Rebuilt"""
    load_plugin('TR_Mainland.esm')
    # load_plugin('TR_Factions.esp')

    """Skyrim: Home of the Nords"""
    # load_plugin('Sky_Main.esm')

    """Province: Cyrodiil"""
    # load_plugin('Cyr_Main.esm')


def testing_area():
    """
    Anything put here is executed after settings and plugins are initialized. You can load additional plugins, run
    jobs, or anything else not possible through command line args (you can run those too).
    """

    mwjobs.journal_entries("TR_Mainland.esm")


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
