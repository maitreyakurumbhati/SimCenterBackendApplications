"""
authors: Dr. Frank McKenna*, Aakash Bangalore Satish*, Mukesh Kumar Ramancha, Maitreya Manoj Kurumbhati,
and Prof. J.P. Conte
affiliation: SimCenter*; University of California, San Diego

"""

import os
import platform
import subprocess
import shutil
import numpy as np


def copytree(src, dst, symlinks=False, ignore=None):
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            copytree(s, d, symlinks, ignore)
        else:
            if not os.path.exists(d) or os.stat(s).st_mtime - os.stat(d).st_mtime > 1:
                shutil.copy2(s, d)


def runFEM(ParticleNum, par, variables, workdirMain, log_likelihood, calibrationData, numExperiments,
           covarianceMatrixList, edpNamesList, edpLengthsList, scaleFactors, shiftFactors, workflowDriver):
    """ 
    this function runs FE model (model.tcl) for each parameter value (par)
    model.tcl should take parameter input
    model.tcl should output 'output$PN.txt' -> column vector of size 'Ny'
    """

    # print("\nParticleNum: {}, parameter values: {} ".format(ParticleNum, par))

    stringtoappend = ("workdir." + str(ParticleNum + 1))
    analysisPath = os.path.join(workdirMain, stringtoappend)

    if os.path.isdir(analysisPath):
        pass
    else:
        os.mkdir(analysisPath)

    # copy templatefiles
    templateDir = os.path.join(workdirMain, "templatedir")
    copytree(templateDir, analysisPath)

    # change to analysis directory
    os.chdir(analysisPath)

    # write input file and covariance multiplier values list
    covarianceMultiplierList = []
    ParameterName = variables["names"]
    f = open("params.in", "w")
    f.write('{}\n'.format(len(par) - len(edpNamesList)))
    for i in range(0, len(par)):
        name = str(ParameterName[i])
        value = str(par[i])
        if name.split('.')[-1] != 'CovMultiplier':
            f.write('{} {}\n'.format(name, value))
        else:
            covarianceMultiplierList.append(par[i])
    f.close()

    script = workflowDriver

    # print("RUN FEM: " + script)

    p = subprocess.Popen(script, stderr=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()

    # Read in the model prediction
    if os.path.exists('results.out'):
        prediction = np.atleast_2d(np.genfromtxt('results.out')).reshape((1, -1))

        # os.chdir(workdirMain)

        return log_likelihood(calibrationData, prediction, numExperiments, covarianceMatrixList, edpNamesList,
                            edpLengthsList, covarianceMultiplierList, scaleFactors, shiftFactors)
    else:
        return -np.inf