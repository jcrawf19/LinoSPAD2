"""Script for plotting a grid 5x5 of delta t for different pairs of pixels.

This script utilizes an unpacking module used specifically for the LinoSPAD2
data output.

The output is saved in the `results/delta_t` directory, in the case there is
no such folder, it is created where the data are stored.

This file can also be imported as a module and contains the following
functions:

    * plot_grid - plots a 4x4 grid of delta t for different pairs of pixels for
    5 pixels total

"""

import os
import glob
from tqdm import tqdm
import numpy as np
from matplotlib import pyplot as plt
from functions import unpack as f_up


def plot_grid(path, pix, lines_of_data: int = 512, show_fig: bool = False):
    '''Plots a 4x4 grid of delta t for different pairs of pixels for 5 pixels
    total in the giver range.


    Parameters
    ----------
    path : str
        Path to the data file.
    pix : array-like
        Array of indices of 5 pixels for analysis.
    lines_of_data : int, optional
        Number of data points per pixel per acquisition cycle. The default is
        512.
    show_fig : bool, optional
        Switch for showing the output figure. The default is False.

    Returns
    -------
    None.

    '''

    os.chdir(path)

    DATA_FILES = glob.glob('*.dat*')

    for num, filename in enumerate(DATA_FILES):
        lod = lines_of_data
        data = f_up.unpack_binary_flex(filename, lod)

        data_1 = data[pix[0]]  # 1st pixel
        data_2 = data[pix[1]]  # 2nd pixel
        data_3 = data[pix[2]]  # 3d pixel
        data_4 = data[pix[3]]  # 4th pixel
        data_5 = data[pix[4]]  # 5th pixel

        pixel_numbers = np.arange(pix[0], pix[-1]+1, 1)

        all_data = np.vstack((data_1, data_2, data_3, data_4, data_5))

        # check if the figure should appear in a separate window or not at all
        if show_fig is True:
            plt.ion()
        else:
            plt.ioff()

        plt.rcParams.update({'font.size': 20})
        fig, axs = plt.subplots(4, 4, figsize=(24, 24))

        for q in range(5):
            for w in range(5):
                if w <= q:
                    continue

                data_pair = np.vstack((all_data[q], all_data[w]))

                minuend = len(data_pair)-1  # i=255
                lines_of_data = len(data_pair[0])  # j=10*11999 (lines of data
                # * number of acq cycles)
                subtrahend = len(data_pair)  # k=254
                timestamps = 512  # lines of data in the acq cycle

                output = []

                for i in tqdm(range(minuend)):
                    acq = 0  # number of acq cycle
                    for j in range(lines_of_data):
                        if data_pair[i][j] == -1:
                            continue
                        if j % 512 == 0:
                            acq = acq + 1  # next acq cycle
                        for k in range(subtrahend):
                            if k <= i:
                                continue  # to avoid repetition: 2-1, 53-45
                            for p in range(timestamps):
                                n = 512*(acq-1) + p
                                if data_pair[k][n] == -1:
                                    continue
                                elif data_pair[i][j] - data_pair[k][n] > 3e2:
                                    continue
                                elif data_pair[i][j] - data_pair[k][n] < -3e2:
                                    continue
                                else:
                                    output.append(data_pair[i][j]
                                                  - data_pair[k][n])

                bins = np.arange(np.min(output), np.max(output), 17.857)
                axs[q][w-1].set_xlabel('\u0394t [ps]')
                axs[q][w-1].set_ylabel('Timestamps [-]')
                n, b, p = axs[q][w-1].hist(output, bins=bins)
                # find position of the histogram peak
                n_max = np.argmax(n)
                arg_max = format((bins[n_max] + bins[n_max + 1]) / 2, ".2f")

                axs[q][w-1].set_title('Pixels {p1}-{p2}\nPeak position {pp}'
                                      .format(p1=pixel_numbers[q],
                                              p2=pixel_numbers[w],
                                              pp=arg_max))
        try:
            os.chdir("results/delta_t")
        except Exception:
            os.mkdir("results/delta_t")
            os.chdir("results/delta_t")
        fig.tight_layout()  # for perfect spacing between the plots
        plt.savefig("{name}_delta_t_grid.png".format(name=filename))
        os.chdir("..")
