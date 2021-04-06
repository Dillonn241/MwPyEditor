from core import mwglobals


def mod_shortcut(obj):
    if obj.file_name.startswith("Tamriel_"):
        return "TD3"
    elif obj.file_name.startswith("TR_"):
        return "TR3"
    elif obj.file_name.startswith("Sky_"):
        return "SHOTN"
    elif obj.file_name.startswith("Cyrodiil_"):
        return "PC3"


def filtered_dialogue(actor='', race='', class_='', faction='', cell='', pc_faction=''):
    infos = mwglobals.records['INFO']
    return [x for x in infos if x.filter(actor=actor, race=race, class_=class_, faction=faction, cell=cell,
                                         pc_faction=pc_faction)]
