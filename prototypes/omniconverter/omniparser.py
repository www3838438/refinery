import ase.io


def omniparse(file_path, try_all=False, info=False):
    """Parse a data file however possible.

    Arguments:
    file_path (str): The path to the data file.
    try_all (bool): If True, will extract data from all parsers as possible.
                    If False, will stop after the first successful parsing.
                    Default False.
    info (bool): If True, will return a tuple of (results, info) (see "Returns").
                 If False, will just return results.
                 Default False.

    Returns:
    dict (if not info): The metadata parsed from the file. Will be empty if file could not be parsed.
    tuple of (dict, dict) (if info): The metadata, and a dict of parsing information.
    """
    ALL_PARSERS = [
        parse_ase
    ]
    data = {}
    info_dict = {
        "success": False,
        "failed": []
    }
    for parser in ALL_PARSERS:
        res = parser(file_path, stats=True)
        # If success, process results
        if res[0]:
            data.update(res[0])
            info_dict["success"] = True
            if not try_all:
                info_dict["parser"] = parser.__name__
                break
            else:
                info_dict["parser"] = info_dict.get("parser", []).append(parser.__name__)
        else:
            info_dict["failed"].append(parser.__name__)
    if not info:
        return data
    else:
        return (data, info_dict)


def parse_ase(file_path, stats=False):
    """Parser for data in ASE-readable formats.
    If ASE is incapable of reading the file and raises an exception,
    the (first) return dict == {} and total_num == 0 and failure_num == 1.

    Arguments:
    file_path (str): Path to the data file.
    stats (bool): If True, will return a tuple of (results, stats) (see "Returns").
                  If False, just returns the results.
                  Default False.

    Returns:
    dict (if not stats): Useful data ASE could pull out of the file.
    tuple of (dict, dict) (if stats): The data ASE parsed, and success/failure numbers.
    """
    
    ase_template = {
#        "constraints" : None,              # No get()
#        "all_distances" : None,
#        "angular_momentum" : None,
#        "atomic_numbers" : None,
#        "cell" : None,
        "cell_lengths_and_angles" : None,
#        "celldisp" : None,
#        "center_of_mass" : None,
#        "charges" : None,
        "chemical_formula" : None,
#        "chemical_symbols" : None,
#        "dipole_moment" : None,
#        "forces" : None,
#        "forces_raw" : None,               # No get()
#        "initial_charges" : None,
#        "initial_magnetic_moments" : None,
#        "kinetic_energy" : None,
#        "magnetic_moment" : None,
#        "magnetic_moments" : None,
#        "masses" : None,
#        "momenta" : None,
#        "moments_of_inertia" : None,
#        "number_of_atoms" : None,
        "pbc" : None,
#        "positions" : None,
#        "potential_energies" : None,
#        "potential_energy" : None,
#        "potential_energy_raw" : None,     # No get()
#        "reciprocal_cell" : None,
#        "scaled_positions" : None,
#        "stress" : None,
#        "stresses" : None,
#        "tags" : None,
        "temperature" : None,
#        "total_energy" : None,
#        "velocities" : None,
        "volume" : None,
#        "filetype": None,                  # No get()
#        "num_frames": None,                # No get()
#        "num_atoms": None                  # No get()
        }
    total_count = 0
    failures = []
    success_count = 0
    none_count = 0


    # Read the file and process it if the reading succeeds
    try:
        result = ase.io.read(file_path)
    except Exception as e:
        failures.append(repr(e))
        # none_count - len(failures) should be 0
        none_count = 1
        ase_dict = {}
    else:
        ase_dict = ase_template.copy()
        # Data with easy .get() functions
        for key in ase_dict.keys():
            total_count += 1
            try:
                ase_dict[key] = eval("result.get_" + key + "()")
                success_count += 1
            # Any exception is a failure to get the data
            except Exception as e:
                failures.append(repr(e))
                ase_dict[key] = None

        # Data without a .get()
        ase_dict["filetype"] = ase.io.formats.filetype(file_path)
        ase_dict["num_atoms"] = len(result)
#        if type(result) is list:
#            ase_dict["num_frames"] = len(result)
#        else:
#            ase_dict["num_atoms"] = len(result)


        # Fix up the extracted data
        none_keys = []
        for key in ase_dict.keys():
            # numpy ndarrays aren't JSON serializable
            if 'numpy' in str(type(ase_dict[key])).lower():
                ase_dict[key] = ase_dict[key].tolist()

            # None values aren't useful
            if ase_dict[key] is None:
                none_keys.append(key)
                none_count += 1
            # Remake lists with valid values
            elif type(ase_dict[key]) is list:
                new_list = []
                for elem in ase_dict[key]:
                    # FixAtoms aren't JSON serializable
                    if 'fixatoms' in str(elem).lower():
                        new_elem = elem.get_indices().tolist()
                    else:
                        new_elem = elem
                    # Only add elements with data
                    if new_elem:
                        new_list.append(new_elem)
                # Only add lists with data
                if new_list:
                    ase_dict[key] = new_list
                else:
                    none_keys.append(key)
        # None keys aren't useful
        for key in none_keys:
            ase_dict.pop(key)

    if not stats:
        return ase_dict
    else:
        stats = {
            "total_num": total_count,
            "num_success": success_count,
            "num_failure": len(failures),
            "failure_exceptions": failures,
            # none_count includes None due to failure, don't double-count
            "num_none": none_count - len(failures)
            }
        return (ase_dict, stats)
