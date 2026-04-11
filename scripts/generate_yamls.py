import yaml, argparse, inspect, sys
import boxes, boxes.generators
from boxes.generators import getAllBoxGenerators
 
def action_to_dict(a):
    d = {
        'flags': list(a.option_strings) if getattr(a,'option_strings',None) else [],
        'dest': getattr(a,'dest',None),
        'default': getattr(a,'default',None),
        'required': getattr(a,'required',False),
        'help': getattr(a,'help',None),
    }
    if getattr(a,'choices',None) is not None:
        try:
            d['choices'] = list(a.choices)
        except TypeError:
            d['choices'] = a.choices
    t = getattr(a,'type',None)
    if t is None:
        d['type'] = None
    else:
        d['type'] = getattr(t,'__name__', t.__class__.__name__)
    d['nargs'] = getattr(a,'nargs',None)
    return d
 
def gen_inventory():
    inv = {}
    errs = {}
    allgens = getAllBoxGenerators()
    for name, cls in sorted(allgens.items(), key=lambda kv: kv[0].split('.')[-1].lower()):
        gname = cls.__name__
        try:
            b = cls()
            groups = []
            for grp in b.argparser._action_groups:
                g = {'title': grp.title, 'actions': []}
                for a in grp._group_actions:
                    if isinstance(a, argparse._HelpAction):
                        continue
                    g['actions'].append(action_to_dict(a))
                if g['actions']:
                    groups.append(g)
            inv[gname] = {
                'module': cls.__module__,
                'webinterface': getattr(cls,'webinterface',None),
                'ui_group': getattr(cls,'ui_group',None),
                'groups': groups,
            }
        except Exception as e:
            errs[gname] = repr(e)
    return inv, errs
 
inv, errs = gen_inventory()
print(yaml.safe_dump({'generators': inv, 'errors': errs}, sort_keys=True, allow_unicode=True))