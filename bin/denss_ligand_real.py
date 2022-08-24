#!/usr/bin/env python
#
#    denss.py
#    DENSS: DENsity from Solution Scattering
#    A tool for calculating an electron density map from solution scattering data
#
#    Tested using Anaconda / Python 2.7
#
#    Author: Thomas D. Grant
#    Email:  <tgrant@hwi.buffalo.edu>
#    Copyright 2017 The Research Foundation for SUNY
#
#    Author: Darren J. Hsu
#    Email:  <hsudj@ornl.gov>
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
import saxstats.denssopts as dopts
import numpy as np
import sys, argparse, os
import logging

parser = argparse.ArgumentParser(description="DENSS: DENsity from Solution Scattering.\n A tool for calculating an electron density map from solution scattering data", formatter_class=argparse.RawTextHelpFormatter)
args = dopts.parse_arguments(parser)

if __name__ == "__main__":
    my_logger = logging.getLogger()
    my_logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s %(message)s', '%Y-%m-%d %I:%M:%S %p')

    # h1 = logging.StreamHandler(sys.stdout)
    # h1.setLevel(logging.INFO)
    # h1.setFormatter(formatter)

    h2 = logging.FileHandler(os.path.join('.', args.output+'.log'), mode='w')
    h2.setLevel(logging.INFO)
    h2.setFormatter(formatter)

    # my_logger.addHandler(h1)
    my_logger.addHandler(h2)

    my_logger.info('BEGIN')
    my_logger.info('Script name: %s', sys.argv[0])
    my_logger.info('DENSS Version: %s', __version__)
    my_logger.info('Data filename: %s', args.file)
    my_logger.info('Output prefix: %s', args.output)
    my_logger.info('Mode: %s', args.mode)

    qdata, Idata, sigqdata, qbinsc, Imean, chis, rg, supportV, rho, side = saxs.denss_ligand_real(
        q=args.q,
        I=args.I,
        sigq=args.sigq,
        dmax=args.dmax,
        ref_rho=args.ref,
        ligand_center=args.ligand_center,
        ligand_box_size=args.ligand_box_size,
        ligand_mask_mode=args.ligand_mask_mode,
        ligand_ref=args.ligand_ref,
        no_overlap=args.no_overlap,
        ne=args.ne,
        voxel=args.voxel,
        oversampling=args.oversampling,
        recenter=args.recenter,
        recenter_steps=args.recenter_steps,
        recenter_mode=args.recenter_mode,
        positivity=args.positivity,
        extrapolate=args.extrapolate,
        output=args.output,
        steps=args.steps,
        #ncs=args.ncs,
        #ncs_steps=args.ncs_steps,
        #ncs_axis=args.ncs_axis,
        #ncs_type=args.ncs_type,
        seed=args.seed,
        shrinkwrap=args.shrinkwrap,
        shrinkwrap_old_method=args.shrinkwrap_old_method,
        shrinkwrap_sigma_start=args.shrinkwrap_sigma_start,
        shrinkwrap_sigma_end=args.shrinkwrap_sigma_end,
        shrinkwrap_sigma_decay=args.shrinkwrap_sigma_decay,
        shrinkwrap_threshold_fraction=args.shrinkwrap_threshold_fraction,
        shrinkwrap_iter=args.shrinkwrap_iter,
        shrinkwrap_minstep=args.shrinkwrap_minstep,
        chi_end_fraction=args.chi_end_fraction,
        write_xplor_format=args.write_xplor_format,
        write_freq=args.write_freq,
        enforce_connectivity=args.enforce_connectivity,
        enforce_connectivity_steps=args.enforce_connectivity_steps,
        cutout=args.cutout,
        quiet=args.quiet,
        DENSS_GPU=args.DENSS_GPU,
        my_logger=my_logger,
        refine_mode=args.refine_mode,
        refine_switch=args.refine_switch,
        pip_threshold=args.pip_threshold,
        pip_period=args.pip_period,
        dot_radius_start=args.dot_radius_start,
        dot_radius_end=args.dot_radius_end,
        dot_tuning=args.dot_tuning,
        timing_period=args.timing_period,
        rho_start=args.rho_start,
        write_EM_trace=args.write_EM_trace,
        write_EM_trace_freq=args.write_EM_trace_freq,
        empty_canvas=args.empty_canvas
    )

    print("\n%s"%args.output)

    if args.plot:
        import matplotlib.pyplot as plt
        from  matplotlib.colors import colorConverter as cc
        import matplotlib.gridspec as gridspec

        qraw = args.qraw
        Iraw = args.Iraw
        q = args.q
        I = args.I
        sigq = args.sigq

        f = plt.figure(figsize=[6,6])
        gs = gridspec.GridSpec(2, 1, height_ratios=[3,1])

        ax0 = plt.subplot(gs[0])
        #handle sigq values whose error bounds would go negative and be missing on the log scale
        #sigq2 = np.copy(sigq)
        #sigq2[sigq>I] = I[sigq>I]*.999
        sigq2 = np.interp(qraw, q, sigq)
        sigq2[sigq2>Iraw] = Iraw[sigq2>Iraw]*.999
        #ax0.errorbar(q, I, fmt='k-', yerr=[sigq2[q<=q[-1]],sigq[q<=q[-1]]], capsize=0, elinewidth=0.1, ecolor=cc.to_rgba('0',alpha=0.5),label='Supplied Data')
        #ax0.plot(q, I, 'k.',alpha=0.1,mec='none',label='Raw Data')
        ax0.errorbar(qraw, Iraw, fmt='k.', yerr=sigq2, mec='none', mew=0, ms=3, alpha=0.3, capsize=0, elinewidth=0.1, ecolor=cc.to_rgba('0',alpha=0.5),label='Supplied Data')
        ax0.plot(q, I, 'k--',alpha=0.7,lw=1,label='Supplied Fit')
        ax0.plot(qdata[qdata<=q[-1]], Idata[qdata<=q[-1]], 'bo',alpha=0.5,label='Interpolated')
        #ax0.plot(qbinsc[qdata<=q[-1]],Imean[qdata<=q[-1]],'r.',label='DENSS Map')
        ax0.plot(qbinsc, Imean,'r.',label='DENSS Map')
        handles,labels = ax0.get_legend_handles_labels()
        handles = [handles[3], handles[0], handles[1],handles[2]]
        labels = [labels[3], labels[0], labels[1], labels[2]]
        xmax = np.min([qraw.max(),q.max(),qdata.max()])*1.1
        #ymin = np.min([np.min(I[q<=xmax]),np.min(Idata[qdata<=xmax]),np.min(Imean[qdata<=xmax])])
        #ymax = np.max([np.max(I[q<=xmax]),np.max(Idata[qdata<=xmax]),np.max(Imean[qdata<=xmax])])
        ymin = np.min([np.min(I[q<=xmax]),np.min(Idata[qdata<=xmax]),np.min(Imean)])
        ymax = np.max([np.max(I[q<=xmax]),np.max(Idata[qdata<=xmax]),np.max(Imean)])
        ax0.set_xlim([-xmax*.05,xmax])
        ax0.set_ylim([0.5*ymin,1.5*ymax])
        ax0.legend(handles,labels)
        ax0.semilogy()
        ax0.set_ylabel('I(q)')

        ax1 = plt.subplot(gs[1])
        ax1.plot(qdata[qdata<=q[-1]], qdata[qdata<=q[-1]]*0, 'k--')
        residuals = np.log10(Imean[np.in1d(qbinsc,qdata)])-np.log10(Idata)
        ax1.plot(qdata[qdata<=q[-1]], residuals[qdata<=q[-1]], 'ro-')
        ylim = ax1.get_ylim()
        ymax = np.max(np.abs(ylim))
        n = int(.9*len(residuals[qdata<=q[-1]]))
        ymax = np.max(np.abs(residuals[qdata<=q[-1]][:-n]))
        ax1.set_ylim([-ymax,ymax])
        ax1.yaxis.major.locator.set_params(nbins=5)
        xlim = ax0.get_xlim()
        ax1.set_xlim(xlim)
        ax1.set_ylabel('Residuals')
        ax1.set_xlabel(r'q ($\mathrm{\AA^{-1}}$)')
        #plt.setp(ax0.get_xticklabels(), visible=False)
        plt.tight_layout()
        plt.savefig(args.output+'_fit.png',dpi=150)
        plt.close()

        """
        plt.plot(chis[chis>0])
        plt.xlabel('Step')
        plt.ylabel('$\chi^2$')
        plt.semilogy()
        plt.tight_layout()
        plt.savefig(args.output+'_chis.png',dpi=150)
        plt.close()

        plt.plot(rg[rg!=0])
        plt.xlabel('Step')
        plt.ylabel('Rg')
        plt.tight_layout()
        plt.savefig(args.output+'_rgs.png',dpi=150)
        plt.close()

        plt.plot(supportV[supportV>0])
        plt.xlabel('Step')
        plt.ylabel('Support Volume ($\mathrm{\AA^{3}}$)')
        plt.semilogy()
        plt.tight_layout()
        plt.savefig(args.output+'_supportV.png',dpi=150)
        plt.close()
        """

        fig, host = plt.subplots(nrows=1, ncols=1)

        par1 = host.twinx()
        par2 = host.twinx()

        #host.set_xlim(0, 2)
        #host.set_ylim(0, 1.05*chis.max())
        #par1.set_ylim(0, 4)
        #par2.set_ylim(1, 65)

        host.set_xlabel('Step')
        host.set_ylabel('$\chi^2$')
        par1.set_ylabel('Rg')
        par2.set_ylabel('Support Volume')

        color1 = plt.cm.viridis(0)
        color2 = plt.cm.viridis(0.5)
        color3 = plt.cm.viridis(.9)

        p1, = host.plot(chis[chis>0], color=color1,label="$\chi^2$")
        p2, = par1.plot(rg[rg!=0], color=color2, label="Rg")
        p3, = par2.plot(supportV[supportV>0], color=color3, label="Support Volume")

        host.semilogy()
        par2.semilogy()

        lns = [p1, p2, p3]
        host.legend(handles=lns, loc='best')

        # right, left, top, bottom
        par2.spines['right'].set_position(('outward', 60))      
        # no x-ticks                 
        #par2.xaxis.set_ticks([])
        # Sometimes handy, same for xaxis
        #par2.yaxis.set_ticks_position('right')

        host.yaxis.label.set_color(p1.get_color())
        par1.yaxis.label.set_color(p2.get_color())
        par2.yaxis.label.set_color(p3.get_color())

        plt.savefig(args.output+'_stats_by_step.png', bbox_inches='tight',dpi=150)
        plt.close()

    logging.info('END')


