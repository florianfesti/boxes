import yaml, argparse, inspect, sys, os

try:
    import boxes.generators
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../.."))
    import boxes.generators

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

def generate_yaml_for_generator(cls, output_dir):
    """Generate a YAML file for a single generator"""
    gname = cls.__name__
    
    try:
        b = cls()
        
        # Create YAML structure for boxes_generator.py
        yaml_data = {
            'Defaults': {},
            'Boxes': [
                {
                    'box_type': gname,
                    'name': f"{gname}_example",
                    'generate': False,  # Don't actually generate by default
                    'args': {}
                }
            ]
        }
        
        # Collect all parameters from argument groups
        args_dict = {}
        for grp in b.argparser._action_groups:
            # Skip the "optional arguments" group which contains --help etc
            if grp.title in ['optional arguments', 'options']:
                continue
                
            for a in grp._group_actions:
                if isinstance(a, argparse._HelpAction):
                    continue
                
                # Get parameter name (remove leading dashes)
                param_name = None
                for flag in getattr(a, 'option_strings', []):
                    if flag.startswith('--'):
                        param_name = flag[2:]
                        break
                    elif flag.startswith('-') and not flag.startswith('--'):
                        param_name = flag[1:]
                        break
                
                if param_name and param_name != 'help':
                    # Get default value
                    default_value = getattr(a, 'default', None)
                    
                    # Get help text for comment
                    help_text = getattr(a, 'help', '')
                    
                    # Add to args dictionary
                    args_dict[param_name] = default_value
        
        yaml_data['Boxes'][0]['args'] = args_dict
        
        # Generate YAML string with comments
        yaml_lines = []
        yaml_lines.append("# Generated YAML configuration for " + gname)
        yaml_lines.append("# This file can be used with boxes_generator.py")
        yaml_lines.append("")
        yaml_lines.append("Boxes:")
        yaml_lines.append("  - box_type: " + gname)
        yaml_lines.append("    name: \"" + gname + "_example\"")
        yaml_lines.append("    generate: true")
        yaml_lines.append("    args:")
        
        # Add parameters with comments
        for param_name, default_value in sorted(args_dict.items()):
            help_text = ""
            
            # Find the help text for this parameter
            for grp in b.argparser._action_groups:
                if grp.title in ['optional arguments', 'options']:
                    continue
                for a in grp._group_actions:
                    if isinstance(a, argparse._HelpAction):
                        continue
                    
                    # Check if this action matches our parameter
                    param_match = False
                    for flag in getattr(a, 'option_strings', []):
                        if flag.startswith('--') and flag[2:] == param_name:
                            param_match = True
                            break
                        elif flag.startswith('-') and not flag.startswith('--') and flag[1:] == param_name:
                            param_match = True
                            break
                    
                    if param_match:
                        help_text = getattr(a, 'help', '')
                        break
                if help_text:
                    break
            
            # Format the value for YAML
            if default_value is None:
                value_str = "null"
            elif isinstance(default_value, bool):
                value_str = str(default_value).lower()
            elif isinstance(default_value, str):
                value_str = f"\"{default_value}\""
            elif isinstance(default_value, (int, float)):
                value_str = str(default_value)
            elif isinstance(default_value, list):
                value_str = str(default_value)
            else:
                value_str = f"\"{str(default_value)}\""
            
            # Add parameter with help comment
            if help_text:
                yaml_lines.append(f"      # {help_text}")
            yaml_lines.append(f"      {param_name}: {value_str}")
        
        # Write to file
        filename = os.path.join(output_dir, f"{gname.lower()}.yaml")
        with open(filename, 'w') as f:
            f.write('\n'.join(yaml_lines))
        
        print(f"Generated {filename}")
        return filename
        
    except Exception as e:
        print(f"Error generating YAML for {gname}: {e}")
        return None

def main():
    """Generate individual YAML files for each generator"""
    # Create output directory
    output_dir = "generator_yamls"
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all generators
    allgens = getAllBoxGenerators()
    generated_files = []
    errors = {}
    
    for name, cls in sorted(allgens.items(), key=lambda kv: kv[0].split('.')[-1].lower()):
        gname = cls.__name__
        
        # Only generate for generators with webinterface (like boxes_generator.py does)
        if not getattr(cls, 'webinterface', False):
            continue
            
        try:
            filename = generate_yaml_for_generator(cls, output_dir)
            if filename:
                generated_files.append(filename)
        except Exception as e:
            errors[gname] = repr(e)
            print(f"Error with {gname}: {e}")
    
    print(f"\nGenerated {len(generated_files)} YAML files in '{output_dir}' directory")
    if errors:
        print(f"Errors encountered: {len(errors)}")
        for name, error in errors.items():
            print(f"  {name}: {error}")

if __name__ == "__main__":
    main()