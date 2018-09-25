#!/usr/bin/env python
from __future__ import print_function
import dxpy
import argparse
import sys
import os
import subprocess

def main():
    argparser = argparse.ArgumentParser(description="Run tests for the cidr_project workflow. This should normally be invoked indirectly, through ./build_workflow.py --run-tests")
    argparser.add_argument("--project", help="DNAnexus project ID", required=True)
    argparser.add_argument("--workflow", help="Workflow ID (must reside in the project)", required=True)
    argparser.add_argument("--folder", help="Folder in which to place outputs (default: test/ subfolder of workflow's folder)")
    argparser.add_argument("--no-wait", help="Exit immediately after launching tests", action="store_true", default=False)
    args = argparser.parse_args()

    project = dxpy.DXProject(args.project)
    workflow = dxpy.DXWorkflow(project=project.get_id(), dxid=args.workflow)

    if args.folder is None:
        args.folder = os.path.join(workflow.describe()["folder"], "test")

    print("test folder: " + args.folder)

    def find_test_data(name, classname="file"):
        return dxpy.find_one_data_object(classname=classname, name=name,
                                         project=project.get_id(), folder="/test-data",
                                         zero_ok=False, more_ok=False, return_handler=True)

    test_analyses = run_test_analyses(project, args.folder, workflow, find_test_data)
    print("test analyses: " + ", ".join([a.get_id() for a in test_analyses]))

    if args.no_wait != True:
        print("awaiting completion...")
        # wait for analysis to finish while working around Travis 10m console inactivity timeout
        noise = subprocess.Popen(["/bin/bash", "-c", "while true; do sleep 60; date; done"])
        try:
            for test_analysis in test_analyses:
                test_analysis.wait_on_done()
            print("Success!")
        finally:
            noise.kill()

        # TODO: validate the test analysis results in some way

def run_test_analyses(project, folder, workflow, find_test_data):
    # test cases: one or more named input hashes to run the workflow with
    test_inputs = {
        "test1": {
            # "hello-world1.infile": dxpy.dxlink(find_test_data("myfile").get_id())
        }
        # other test inputs could go here...
    }

    # The tests might only need smaller instance types than the applet
    # defaults (reduces cost of running tests).
    stage_instance_types = {
        # "hello-world1": "mem2_hdd2_x1"
    }

    git_revision = workflow.describe(incl_properties=True)["properties"]["git_revision"]
    analyses = []
    for test_name, test_input in test_inputs.iteritems():
        test_folder = os.path.join(folder, test_name)
        project.new_folder(test_folder, parents=True)
        analyses.append(workflow.run(test_input, project=project.get_id(), folder=test_folder,
                                     stage_instance_types=stage_instance_types,
                                     name="cidr_project {} {}".format(test_name, git_revision)))
    return analyses

if __name__ == '__main__':
    main()

