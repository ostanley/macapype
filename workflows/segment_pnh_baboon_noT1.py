#!/usr/bin/env python3
"""
    Non humain primates anatomical segmentation pipeline based ANTS

    Adapted in Nipype from an original pipelin of Kepkee Loh wrapped.

    Description
    --------------
    TODO :/

    Arguments
    -----------
    -data:
        Path to the BIDS directory that contain subjects' MRI data.

    -out:
        Nipype's processing directory.
        It's where all the outputs will be saved.

    -subjects:
        IDs list of subjects to process.

    -ses
        session (leave blank if None)

    -params
        json parameter file; leave blank if None

    Example
    ---------
    python segment_pnh_kepkee.py -data [PATH_TO_BIDS] -out ../local_tests/ -subjects Elouk

    Requirements
    --------------
    This workflow use:
        - ANTS
        - AFNI
        - FSL
"""

# Authors : David Meunier (david.meunier@univ-amu.fr)
#           Bastien Cagna (bastien.cagna@univ-amu.fr)
#           Kepkee Loh (kepkee.loh@univ-amu.fr)
#           Julien Sein (julien.sein@univ-amu.fr)

import os
import os.path as op

import argparse
import json
import pprint

import nipype

import nipype.pipeline.engine as pe
import nipype.interfaces.utility as niu

import nipype.interfaces.fsl as fsl
fsl.FSLCommand.set_default_output_type('NIFTI_GZ')

from macapype.pipelines.full_pipelines import (
    create_full_segment_pnh_noT1_subpipes)

from macapype.utils.utils_bids import (create_datasource_indiv_params_noT1,
                                       create_datasource_noT1)

from macapype.utils.utils_tests import load_test_data, format_template

from macapype.utils.utils_nodes import node_output_exists

from macapype.utils.misc import show_files, get_first_elem

###############################################################################

def create_main_workflow(data_dir, process_dir, subjects, sessions,
                         acquisitions, params_file, indiv_params_file,
                         wf_name="baboon_noT1_segmentation_test"):
    """ Set up the segmentatiopn pipeline based on ANTS

    Arguments
    ---------
    data_path: pathlike str
        Path to the BIDS directory that contains anatomical images

    out_path: pathlike str
        Path to the ouput directory (will be created if not alredy existing).
        Previous outputs maybe overwritten.

    subjects: list of str (optional)
        Subject's IDs to match to BIDS specification (sub-[SUB1], sub-[SUB2]...)

    sessions: list of str (optional)
        Session's IDs to match to BIDS specification (ses-[SES1], ses-[SES2]...)

    acquisitions: list of str (optional)
        Acquisition name to match to BIDS specification (acq-[ACQ1]...)

    indiv_params_file: path to a JSON file
        JSON file that specify some parameters of the pipeline,
        unique for the subjects/sessions.

    params_file: path to a JSON file
        JSON file that specify some parameters of the pipeline.


    Returns
    -------
    workflow: nipype.pipeline.engine.Workflow


    """

    # formating args
    data_dir = op.abspath(data_dir)

    if not op.isdir(process_dir):
        os.makedirs(process_dir)

    # params
    params = {}
    if params_file is not None:

        print("Params:", params_file)

        assert os.path.exists(params_file), "Error with file {}".format(
            params_file)

        params = json.load(open(params_file))

    pprint.pprint(params)

    # indiv_params
    indiv_params = {}
    if indiv_params_file is not None:

        print("Multi Params:", indiv_params_file)

        assert os.path.exists(indiv_params_file), "Error with file {}".format(
            indiv_params_file)

        indiv_params = json.load(open(indiv_params_file))

        wf_name+="_indiv_params"


    pprint.pprint(indiv_params)

    # params_template
    assert ("general" in params.keys() and \
        "template_name" in params["general"].keys()), \
            "Error, the params.json should contains a general/template_name"

    template_name = params["general"]["template_name"]

    if "general" in params.keys() and "my_path" in params["general"].keys():
        my_path = params["general"]["my_path"]
    else:
        my_path = ""

    nmt_dir = load_test_data(template_name, path_to = my_path)
    params_template = format_template(nmt_dir, template_name)
    print (params_template)

    # main_workflow
    main_workflow = pe.Workflow(name= wf_name)
    main_workflow.base_dir = process_dir

    segment_pnh = create_full_segment_pnh_noT1_subpipes(
        params_template=params_template, params=params)
 

    if indiv_params:
        datasource = create_datasource_indiv_params_noT1(data_dir, indiv_params,
                                                    subjects, sessions)

        main_workflow.connect(datasource, "indiv_params",
                              segment_pnh,'inputnode.indiv_params')
    else:
        datasource = create_datasource_noT1(data_dir, subjects, sessions,
                                       acquisitions)

    main_workflow.connect(datasource, 'T1', segment_pnh, 'inputnode.list_T1')
    
    return main_workflow

if __name__ == '__main__':

    # Command line parser
    parser = argparse.ArgumentParser(
        description="PNH segmentation pipeline")

    parser.add_argument("-data", dest="data", type=str, required=True,
                        help="Directory containing MRI data (BIDS)")
    parser.add_argument("-out", dest="out", type=str, #nargs='+',
                        help="Output dir", required=True)
    parser.add_argument("-subjects", dest="subjects", type=str, nargs='+',
                        help="Subjects' ID", required=False)
    parser.add_argument("-ses", dest="ses", type=str,
                        help="Session", required=False)
    parser.add_argument("-acq", dest="acq", type=str, nargs='+', default=None,
                        help="Acquisitions ID")
    parser.add_argument("-params", dest="params_file", type=str,
                        help="Parameters json file", required=False)
    parser.add_argument("-indiv_params", dest="indiv_params_file", type=str,
                        help="Individual parameters json file", required=False)


    args = parser.parse_args()

    # main_workflow
    print("Initialising the pipeline...")
    wf = create_main_workflow(
        data_dir=args.data,
        process_dir=args.out,
        subjects=args.subjects,
        sessions=args.ses,
        acquisitions=args.acq,
        params_file=args.params_file,
        indiv_params_file=args.indiv_params_file)

    wf.write_graph(graph2use="colored")
    wf.config['execution'] = {'remove_unnecessary_outputs': 'false'}
    #print('The PNH segmentation pipeline is ready')
    #print("Start to process")
    #wf.run()
    wf.run(plugin='MultiProc', plugin_args={'n_procs' : 4})

