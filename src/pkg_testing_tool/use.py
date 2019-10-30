#!/usr/bin/env python3

import portage
import random
from itertools import product


def iuse_match_always_true(flag):
    return True


def strip_use_flags(flags):
    stripped_flags = []

    for flag in flags:
        if flag[0] in ['+', '-']:
            flag = flag[1:]

        stripped_flags.append(flag)

    return stripped_flags


def filter_out_use_flags(flags):
    new_flags = []

    # some flags that *most* likely we shouldn't shuffle and test.
    for flag in flags:
        if not flag.startswith((
            'debug',
            'doc',
            'test',
            'eglibc_',
            'video_cards_',
            'linguas_',
            'kernel_',
            'abi_',
            'python_target_',
            'python_targets_',
            'python_single_target_'
        )):
            new_flags.append(flag)

    return new_flags


def get_package_flags(atom):
    pkg_name = portage.dep.dep_getcpv(atom)

    flags = portage.db[portage.root]['porttree'].dbapi.aux_get(pkg_name, ['IUSE', 'REQUIRED_USE'])

    use_flags = strip_use_flags(flags[0].split())
    use_flags = filter_out_use_flags(use_flags)
    use_flags = sorted(use_flags)

    ruse_flags = flags[1].split()

    return [
        use_flags,
        ruse_flags
    ]


def get_use_combinations(iuse, ruse, max_use_combinations):
    all_combinations = list(product(['', '-'], repeat=len(iuse)))

    valid_use_flags_combinations = []

    if len(all_combinations) > max_use_combinations:
        random.seed()
        checked_combinations = set()

        while len(valid_use_flags_combinations) < max_use_combinations and len(checked_combinations) < len(all_combinations):
            index = random.randint(0, len(all_combinations)-1)

            if index in checked_combinations:
                continue
            else:
                checked_combinations.add(index)

            flags = list("".join(flag) for flag in list(zip(all_combinations[index], iuse)))

            if portage.dep.check_required_use(" ".join(ruse), flags, iuse_match_always_true):
                valid_use_flags_combinations.append(flags)
    else:
        for index in range(0, len(all_combinations)):
            flags = list("".join(flag) for flag in list(zip(all_combinations[index], iuse)))

            if portage.dep.check_required_use(" ".join(ruse), flags, iuse_match_always_true):
                valid_use_flags_combinations.append(flags)

    return valid_use_flags_combinations