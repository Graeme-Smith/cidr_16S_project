#!/usr/bin/env python
from __future__ import print_function
import dxpy
import argparse
import sys
import os
import subprocess
import json
import time

here = os.path.dirname(sys.argv[0])
if here == '':
    here = '.'

git_revision = subprocess.check_output(["git", "describe", "--always", "--dirty", "--tags"], cwd=here).strip()

def main():
    argparser = argparse.ArgumentParser(description="Build cidr_project workflow on DNAnexus.")
    argparser.add_argument("--project", help="DNAnexus project ID", default="project-FKb3KXQ0FpVGFv2v2yBJqz39")
    argparser.add_argument("--folder", help="Folder within project (default: timestamp/git-based)", default=None)
    argparser.add_argument("--run-tests", help="Execute run_tests.py on the new workflow", action='store_true')
    argparser.add_argument("--run-tests-no-wait", help="Execute run_tests.py --no-wait", action='store_true')
    args = argparser.parse_args()

    # set up environment
    if args.folder is None:
        args.folder = time.strftime("/builds/%Y-%m-%d/%H%M%S-") + git_revision

    project = dxpy.DXProject(args.project)
    applets_folder = args.folder + "/applets"
    print("project: {} ({})".format(project.name, args.project))
    print("folder: {}".format(args.folder))

    # build the applets
    build_applets(project, applets_folder)

    # build the workflow
    wf = build_workflow(project, args.folder, applets_folder)
    print("workflow: {} ({})".format(wf.name, wf.get_id()))

    # run the tests if desired
    if args.run_tests_no_wait is True or args.run_tests is True:
        cmd = "python {} --project {} --workflow {}".format(os.path.join(here, "run_tests.py"),
                                                            project.get_id(), wf.get_id())
        if args.run_tests_no_wait is True:
            cmd = cmd + " --no-wait"
        print(cmd)
        sys.exit(subprocess.call(cmd, shell=True, cwd=here))

def build_applets(project, applets_folder):
    here_applets = os.path.join(here, "applets")
    applet_dirs = [os.path.join(here_applets,dir) for dir in os.listdir(here_applets)]
    applet_dirs = [dir for dir in applet_dirs if os.path.isdir(dir)]

    project.new_folder(applets_folder, parents=True)
    for applet_dir in applet_dirs:
        build_cmd = ["dx","build","--destination",project.get_id()+":"+applets_folder+"/",applet_dir]
        print(" ".join(build_cmd))
        applet_dxid = json.loads(subprocess.check_output(build_cmd))["id"]
        applet = dxpy.DXApplet(applet_dxid, project=project.get_id())
        applet.set_properties({"git_revision": git_revision})

def build_workflow(project, folder, applets_folder):

    # helper functions to get handles to stuff in the continuous integration
    # project: applets (which were just built) and slowly-evolving assets
    # (from the /assets folder -- typically large files used as bound inputs
    # in the workflow, e.g. reference genomes)
    def find_applet(applet_name):
        return dxpy.find_one_data_object(classname='applet', name=applet_name,
                                         project=project.get_id(), folder=applets_folder,
                                         zero_ok=False, more_ok=False, return_handler=True)
    def find_asset(asset_name, classname="file"):
        return dxpy.find_one_data_object(classname=classname, name=asset_name,
                                         project=project.get_id(), folder="/assets",
                                         zero_ok=False, more_ok=False, return_handler=True)
    def find_app(app_handle):
        return dxpy.find_one_app(name=app_handle, zero_ok=False, more_ok=False, return_handler=True)

    # create the workflow object
    wf = dxpy.new_dxworkflow(title="cidr_project",
                             name="cidr_project",
                             description="cidr_project",
                             project=project.get_id(),
                             folder=folder,
                             properties={"git_revision": git_revision})

    # set up the workflow stages, chaining outputs/inputs together as needed
    hello_world1_input = {
        # "infile": dxpy.dxlink(find_asset("myfile").get_id())
    }
    hello_world1_stage_id = wf.add_stage(find_applet("hello-world"), name="hello-world1",
                                         stage_input=hello_world1_input)

    hello_world2_input = {
        "infile": dxpy.dxlink({"stage": hello_world1_stage_id, "outputField": "outfile"})
    }
    hello_world2_stage_id = wf.add_stage(find_applet("hello-world"), name="hello-world2",
                                         stage_input=hello_world2_input)


    return wf

if __name__ == '__main__':
    main()

