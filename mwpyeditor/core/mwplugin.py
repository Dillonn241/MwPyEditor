import argparse
import struct
import sys

from mwpyeditor.core import mwglobals
from mwpyeditor.record import (mwacti, mwalch, mwappa, mwarmo, mwbody, mwbook, mwbsgn, mwcell, mwclas, mwclot, mwcont,
                               mwcrea, mwdial, mwdoor, mwench, mwfact, mwglob, mwgmst, mwinfo, mwingr, mwland, mwlevc,
                               mwlevi, mwligh, mwlock, mwltex, mwmgef, mwmisc, mwnpc_, mwpgrd, mwprob, mwrace, mwregn,
                               mwrepa, mwscpt, mwskil, mwsndg, mwsoun, mwspel, mwsscr, mwstat, mwtes3, mwweap)

auto_load_masters = True


def init_args():
    parser = argparse.ArgumentParser(description="""Analyze a plugin file.
                                                 \n\nThe following commands are available:
                                                 \ndiff\tfind the difference between two plugins
                                                 \ndump\toutput readable record data""",
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('command', help="name of the action to take")
    parser.add_argument('plugins', nargs='+', help="list of plugins to load and provide as arguments")
    parser.add_argument('-t', '--type', nargs='+', help="limit to given <record type>s", metavar="<record type>")
    parser.add_argument('-l', '--list', action='store_true', help="show only identifying data for each record")
    parser.add_argument('--diff_ignore_changed', action='store_true', help="""do not report changes between records that
                                                                           exist in plugin1 and plugin2""")
    parser.add_argument('--diff_equal', action='store_true', help="""report records in plugin1 that are identical in
                                                                    plugin2""")
    parser.add_argument('--diff_added', action='store_true', help="""report records in plugin2 that do not exist in
                                                                  plugin1""")
    parser.add_argument('--diff_removed', action='store_true', help="""report records in plugin1 that do not exist in
                                                                    plugin2""")
    args = parser.parse_args()
    if args.type:
        args.type = [x.upper() for x in args.type]
    return args


def handle_args(args):
    if args.command == 'diff':
        args_diff(args)
    elif args.command == 'dump':
        args_dump(args)


def args_diff(args):
    if len(args.plugins) != 2:
        sys.exit("Exactly two plugins can be diffed!")

    plugin1 = args.plugins[0]  # 'Tamriel_Data_6.esm'
    plugin2 = args.plugins[1]  # 'Tamriel_Data.esm'
    record_types = mwglobals.RECORDS_MIN + args.type if args.type else mwglobals.RECORDS_ALL
    print(f"# Diff plugin {plugin1} with {plugin2}: #\n")
    load_plugin(plugin1, records_to_load=record_types)
    load_plugin(plugin2, records_to_load=record_types)

    diff_changed = not args.diff_ignore_changed if args.diff_ignore_changed else True
    diff_equal = args.diff_equal if args.diff_equal else False
    diff_added = args.diff_added if args.diff_added else False
    diff_removed = args.diff_removed if args.diff_removed else False
    for rcd_type in record_types:
        print(f"\n## Diff record type {rcd_type}: ##\n")
        diff_plugins(plugin1, plugin2, rcd_type, changed=diff_changed, equal=diff_equal, added=diff_added,
                     removed=diff_removed)
    print("\n")


def diff_plugins(plugin1, plugin2, record_type, changed=True, equal=False, added=False, removed=False):
    object_ids1 = {}
    object_ids2 = {}
    for record in mwglobals.records[record_type]:
        if record.file_name == plugin1:
            object_ids1[record.get_id()] = record
        elif record.file_name == plugin2:
            object_ids2[record.get_id()] = record

    if changed or equal:
        for record in mwglobals.records[record_type]:
            if record.file_name == plugin1:
                if record.get_id() in object_ids2:
                    record2 = object_ids2[record.get_id()]
                    diff = record.diff(record2)
                    if changed and diff:
                        print(diff)
                    if equal and not diff:
                        print(f"Identical records: {record.get_id()} = {record2.get_id()}")

    if added:
        for record in mwglobals.records[record_type]:
            if record.file_name == plugin2:
                if record.get_id() not in object_ids1:
                    print(f"\nAdded {record}\n{record.details()}\n")

    if removed:
        for record in mwglobals.records[record_type]:
            if record.file_name == plugin1:
                if record.get_id() not in object_ids2:
                    print(f"\nRemoved {record}")


def args_dump(args):
    for plugin in args.plugins:
        record_types = mwglobals.RECORDS_MIN + args.type if args.type else mwglobals.RECORDS_ALL
        print(f"# Dump plugin {plugin}: #\n")
        load_plugin(plugin, records_to_load=record_types)
        for rcd_type in record_types:
            print(f"\n## Dump record type {rcd_type}: ##\n")
            if args.list:
                for rcd in mwglobals.plugin_records[plugin][rcd_type]:
                    print(rcd)
            else:
                for rcd in mwglobals.plugin_records[plugin][rcd_type]:
                    print(f"{rcd.record_details()}\n")
        print("\n")


def load_plugin(file_name, records_to_load=None, masters_loaded=None):
    # use default_records if no argument is provided for records_to_load
    if not records_to_load:
        records_to_load = mwglobals.default_records
    # if automatically loading masters, TES3 is required
    if auto_load_masters:
        if 'TES3' not in records_to_load:
            records_to_load.append('TES3')
        # keep track of masters loaded to avoid chain reaction
        if not masters_loaded:
            masters_loaded = []
    # DIAL should always be loaded with INFO
    if 'INFO' in records_to_load and 'DIAL' not in records_to_load:
        records_to_load.append('DIAL')
    # if the plugin has been loaded before, only load what is still unloaded
    if file_name in mwglobals.plugin_records:
        records_to_load = [x for x in records_to_load if x not in mwglobals.plugin_records[file_name]]
    # otherwise, set up a record list for this plugin in plugin_records
    else:
        mwglobals.plugin_records[file_name] = {}
        for x in records_to_load:
            mwglobals.plugin_records[file_name][x] = []
    # nothing to do if records_to_load is empty
    if not records_to_load:
        return

    # read the plugin file
    with open(mwglobals.DATA_PATH + file_name, mode='rb') as file:
        def load_record():
            # 4 bytes make up a header
            record_type, length, unknown, flags = struct.unpack('<4siii', header)
            record_type = record_type.decode('mbcs')
            length_left = length
            # skip record if it's not a type being loaded
            if record_type not in records_to_load:
                file.seek(length, 1)
                return
            # create record and associate it with this plugin name
            record = create_record(record_type)
            record.file_name = file_name
            # add to global record data structures
            mwglobals.records[record_type].append(record)
            mwglobals.ordered_records.append(record)
            mwglobals.plugin_records[file_name][record_type].append(record)
            # split up the data into subrecords
            while length_left > 0:
                subtype, sublength = struct.unpack('<4si', file.read(8))
                subtype = subtype.decode('mbcs')
                record.add_subrecord(subtype, subdata=file.read(sublength))
                length_left -= 8 + sublength
            # send flags and data off to class to parse
            record.load_flags(flags)
            record.load()
            record.load_deleted()
            return record

        # if setting on, automatically load records from masters; skip if TES3 has been loaded previously
        if auto_load_masters and 'TES3' in records_to_load:
            if header := file.read(16):  # same as single iteration of load_record loop
                for master in load_record().masters:  # first record must be TES3
                    if master not in masters_loaded:
                        masters_loaded.append(master)
                        load_plugin(master, records_to_load=records_to_load, masters_loaded=masters_loaded)
        # print a loading message
        print(f"** Loading {file_name}: {records_to_load} **")
        # load_record loop
        while header := file.read(16):
            load_record()


def save_plugin(file_name, active_file, *merge_files):
    print(file_name)
    files = (active_file,) + merge_files
    with open(file_name, mode='wb') as file:
        for record in mwglobals.ordered_records:
            if record.file_name in files:
                flags = record.save_flags()
                if hasattr(record, 'save'):  # temporary until all are implemented
                    record.save()
                length = 0
                for subrecord in record.ordered_subrecords:
                    length += 8 + len(subrecord.data)
                file.write(struct.pack('<4siii', record.get_record_type().encode('mbcs'), length, 0, flags))
                for subrecord in record.ordered_subrecords:
                    file.write(struct.pack('<4si', subrecord.record_type.encode('mbcs'), len(subrecord.data)))
                    file.write(subrecord.data)


def create_record(record_type):
    if record_type == 'TES3':
        return mwtes3.MwTES3()
    elif record_type == 'GMST':
        return mwgmst.MwGMST()
    elif record_type == 'GLOB':
        return mwglob.MwGLOB()
    elif record_type == 'CLAS':
        return mwclas.MwCLAS()
    elif record_type == 'FACT':
        return mwfact.MwFACT()
    elif record_type == 'RACE':
        return mwrace.MwRACE()
    elif record_type == 'SOUN':
        return mwsoun.MwSOUN()
    elif record_type == 'SKIL':
        return mwskil.MwSKIL()
    elif record_type == 'MGEF':
        return mwmgef.MwMGEF()
    elif record_type == 'SCPT':
        return mwscpt.MwSCPT()
    elif record_type == 'REGN':
        return mwregn.MwREGN()
    elif record_type == 'BSGN':
        return mwbsgn.MwBSGN()
    elif record_type == 'LTEX':
        return mwltex.MwLTEX()
    elif record_type == 'STAT':
        return mwstat.MwSTAT()
    elif record_type == 'DOOR':
        return mwdoor.MwDOOR()
    elif record_type == 'MISC':
        return mwmisc.MwMISC()
    elif record_type == 'WEAP':
        return mwweap.MwWEAP()
    elif record_type == 'CONT':
        return mwcont.MwCONT()
    elif record_type == 'SPEL':
        return mwspel.MwSPEL()
    elif record_type == 'CREA':
        return mwcrea.MwCREA()
    elif record_type == 'BODY':
        return mwbody.MwBODY()
    elif record_type == 'LIGH':
        return mwligh.MwLIGH()
    elif record_type == 'ENCH':
        return mwench.MwENCH()
    elif record_type == 'NPC_':
        return mwnpc_.MwNPC_()
    elif record_type == 'ARMO':
        return mwarmo.MwARMO()
    elif record_type == 'CLOT':
        return mwclot.MwCLOT()
    elif record_type == 'REPA':
        return mwrepa.MwREPA()
    elif record_type == 'ACTI':
        return mwacti.MwACTI()
    elif record_type == 'APPA':
        return mwappa.MwAPPA()
    elif record_type == 'LOCK':
        return mwlock.MwLOCK()
    elif record_type == 'PROB':
        return mwprob.MwPROB()
    elif record_type == 'INGR':
        return mwingr.MwINGR()
    elif record_type == 'BOOK':
        return mwbook.MwBOOK()
    elif record_type == 'ALCH':
        return mwalch.MwALCH()
    elif record_type == 'LEVI':
        return mwlevi.MwLEVI()
    elif record_type == 'LEVC':
        return mwlevc.MwLEVC()
    elif record_type == 'CELL':
        return mwcell.MwCELL()
    elif record_type == 'LAND':
        return mwland.MwLAND()
    elif record_type == 'PGRD':
        return mwpgrd.MwPGRD()
    elif record_type == 'SNDG':
        return mwsndg.MwSNDG()
    elif record_type == 'DIAL':
        return mwdial.MwDIAL()
    elif record_type == 'INFO':
        info = mwinfo.MwINFO()
        last_dial = mwglobals.records['DIAL'][-1]
        last_dial.infos.append(info)
        info.dial = last_dial
        return info
    elif record_type == 'SSCR':
        return mwsscr.MwSSCR()
