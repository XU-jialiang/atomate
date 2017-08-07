# coding: utf-8

from __future__ import division, print_function, unicode_literals, absolute_import

"""
This module defines functions that yield lammps workflows
"""

from fireworks import Workflow

from pymatgen.io.lammps.sets import LammpsInputSet

from atomate.lammps.fireworks.core import LammpsFW, PackmolFW, LammpsForceFieldFW

__author__ = 'Kiran Mathew'
__email__ = "kmathew@lbl.gov"


def get_wf_from_input_template(input_template_file, user_settings, lammps_data=None,
                               input_filename="lammps.in", is_forcefield=False, lammps_cmd="lammps",
                               dump_filenames=None, db_file=None, name="LAMMPS template Wflow"):
    """
    Returns workflow where the input file parameters are set from the given template file.

    Args:
        input_template_file (str): path to plain text template lammps input file.
        user_settings ([dict] or dict): list of settings dict
        lammps_data (string/LammpsData/LammpsForceFieldData): path to the data file or
            an appropriate object.
        input_filename (string): input file name. This is the name of the input file passed to the
            lammps binary.
        is_forcefield (bool): whether the data file has forcefield and topology info in it.
            This is required only if lammps_data is a path to the data file instead of a data object.
        lammps_cmd (string): lammps command to run (skip the input file).
        dump_filenames ([str]): list of dump file names
        db_file (string): path to the db file.
        name (str): workflow name

    Returns:
        Workflow
    """
    wf_name = name
    user_settings = user_settings or {}
    user_settings = user_settings if isinstance(user_settings, list) else [user_settings]

    fws = []
    for settings in user_settings:

        data_filename = settings.get("data_file", "lammps.data")

        if "log_file" not in settings:
            settings["log_file"] = "log.lammps"

        lammps_input_set = LammpsInputSet.from_file(wf_name, input_template_file,
                                                    user_settings=settings, lammps_data=lammps_data,
                                                    data_filename=data_filename,
                                                    is_forcefield=is_forcefield)

        fws.append(
            LammpsFW(lammps_input_set=lammps_input_set, input_filename=input_filename,
                     data_filename=data_filename, lammps_cmd=lammps_cmd, db_file=db_file,
                     log_filename=settings["log_file"], dump_filename=dump_filenames)
        )

    return Workflow(fws, name=name)


def get_packmol_wf(input_file, user_settings, molecules, packing_config, force_field, box_size,
                   site_property=None, tolerance=2.0, filetype="xyz", control_params=None,
                   lammps_cmd = "lammps", dump_filenames=None, db_file=None,
                   name="LAMMPS packmol Wflow"):

    packmol_output_file = "packed.{}".format(filetype)
    mols_number = [mol_config["number"] for mol_config in packing_config]

    fw_packmol = PackmolFW(molecules, packing_config, tolerance=tolerance, filetype=filetype,
                           control_params=control_params, copy_to_current_on_exit=True,
                           output_file=packmol_output_file, site_property=site_property),

    fw_lammps = LammpsForceFieldFW(input_file, packmol_output_file, molecules, mols_number,
                                   forcefield, user_settings=user_settings,
                                   site_property=site_property, input_filename="lammps.in",
                                   lammps_cmd=lammps_cmd, db_file=db_file, parents=[fw_packmol],
                                   log_filename="lammps.log", dump_filename=dump_filenames)

    wf = Workflow([fw_packmol, fw_lammps])

    return wf


# TODO: get rid off it or find some use for it
def get_wf(name, lammps_input_set, input_filename, data_filename, lammps_cmd, db_file,
           log_filename, dump_filenames):
    """
    Returns workflow that writes lammps input/data files, runs lammps and inserts to DB.

    Args:
        name (str): workflow name
        lammps_input_set (DictLammpsInput): lammps input set
        input_filename (str): input file name
        data_filename (str): data file name
        lammps_cmd (str): path to the lammps binary
        db_file (str): path to the db file
        log_filename (str)
        dump_filenames (str)

    Returns:
        Workflow
    """

    fws = [
        LammpsFW(lammps_input_set=lammps_input_set, input_filename=input_filename,
                 data_filename=data_filename, lammps_cmd=lammps_cmd, db_file=db_file,
                 log_filename=log_filename, dump_filename=dump_filenames)
    ]

    return Workflow(fws, name=name)
