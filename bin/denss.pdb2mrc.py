#!/usr/bin/env python
#
#    denss.pdb2mrc.py
#    A tool for calculating simple electron density maps from pdb files.
#
#    Part of the DENSS package
#    DENSS: DENsity from Solution Scattering
#    A tool for calculating an electron density map from solution scattering data
#
#    Tested using Anaconda / Python 2.7
#
#    Author: Thomas D. Grant
#    Email:  <tgrant@hwi.buffalo.edu>
#    Copyright 2018 The Research Foundation for SUNY
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from __future__ import print_function
from saxstats._version import __version__
import saxstats.saxstats as saxs
import numpy as np
import sys, argparse, os

parser = argparse.ArgumentParser(description="A tool for calculating simple electron density maps from pdb files.", formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("--version", action="version",version="%(prog)s v{version}".format(version=__version__))
parser.add_argument("-f", "--file", type=str, help="PDB filename")
parser.add_argument("-s", "--side", default=300., type=float, help="Desired length real space box side (default=300 angstroms)")
parser.add_argument("-v", "--voxel", default=None, type=float, help="Desired voxel size (default=None)")
parser.add_argument("-n", "--nsamples", default=64, type=float, help="Desired number of samples per axis (default=64)")
parser.add_argument("-m", "--mode", default="fast", type=str, help="Mode. Either fast (Simple Gaussian sphere), slow (accurate 5-term Gaussian using Cromer-Mann coefficients), or FFT (default=slow).")
parser.add_argument("-r", "--resolution", default=10.0, type=float, help="Desired resolution (i.e. Gaussian sphere width sigma) (default=15 angstroms)")
parser.add_argument("--solv", default=0.334, type=float, help="Desired Solvent Density (default=0.335 e-/A^3)")
parser.add_argument("-c_on", "--center_on", dest="center", action="store_true", help="Center PDB reference (default).")
parser.add_argument("-c_off", "--center_off", dest="center", action="store_false", help="Do not center PDB reference.")
parser.add_argument("-o", "--output", default=None, help="Output filename prefix (default=basename_pdb)")
parser.set_defaults(center = True)
args = parser.parse_args()

if __name__ == "__main__":

    basename, ext = os.path.splitext(args.file)

    if args.output is None:
        output = basename + "_pdb"
    else:
        output = args.output

    side = args.side
    if args.voxel is None:
        voxel = side / args.nsamples
    else:
        voxel = args.voxel

    halfside = side/2
    n = int(side/voxel)
    #want n to be even for speed/memory optimization with the FFT, ideally a power of 2, but wont enforce that
    if n%2==1: n += 1
    dx = side/n
    dV = dx**3
    x_ = np.linspace(-halfside,halfside,n)
    x,y,z = np.meshgrid(x_,x_,x_,indexing='ij')

    xyz = np.column_stack((x.ravel(),y.ravel(),z.ravel()))
    pdb = saxs.PDB(args.file)
    if args.center:
        pdboutput = basename+"_centered.pdb"
        pdb.coords -= pdb.coords.mean(axis=0)
        pdb.write(filename=pdboutput)

    if args.mode == "fast":
        #rho = saxs.pdb2map_gauss(pdb,xyz=xyz,sigma=args.resolution,mode="fast",eps=1e-6)
        rho = saxs.pdb2map_fastgauss(pdb,x=x,y=y,z=z,sigma=args.resolution,r=args.resolution*2)
    elif args.mode == "slow":
        #this slow mode uses the 5-term Gaussian with Cromer-Mann coefficients
        rho, support = saxs.pdb2map_multigauss(pdb,x=x,y=y,z=z,r=3.0)
    else:
        print("Note: Using FFT method results in severe truncation ripples in map.")
        print("This will also run a quick refinement of phases to attempt to clean this up.")
        rho, support = saxs.pdb2map_FFT(pdb,x=x,y=y,z=z,radii=None)
        rho = saxs.denss_3DFs(rho_start=rho,dmax=side,voxel=dx,oversampling=1.,shrinkwrap=False,support=support)
    print()
    #subtract solvent density value
    #first, identify which voxels have particle
    support = np.zeros(rho.shape,dtype=bool)
    #set a threshold for selecting which voxels have density
    #say, some low percent of the maximum
    #this becomes important for estimating solvent content
    support[rho>0.0001*rho.max()] = True
    rho[~support] = 0
    #scale map to total number of electrons
    rho *= np.sum(pdb.nelectrons) / rho.sum()
    #convert total electron count to density
    rho /= dV
    #now, subtract the solvent density from the particle voxels
    rho[support] -= args.solv

    #write output
    saxs.write_mrc(rho,side,output+".mrc")
    #saxs.write_mrc(support*1.,side,output+"_support.mrc")






