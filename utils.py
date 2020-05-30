import scipy.stats as stats
from scipy.stats import norm
import numpy as np
from matplotlib import pyplot as plt
from scipy.stats import pearson3
import pandas as pd
import matplotlib as mpl
from pandas.plotting import register_matplotlib_converters
import numpy as np
import matplotlib
import matplotlib.gridspec as gridspec
from matplotlib import interactive
import pathlib as pl
import imageio
from matplotlib import pylab

import matplotlib.ticker as ticker


params = {
    "legend.fontsize": "x-large",
    "axes.labelsize": "x-large",
    "axes.titlesize": "x-large",
    "xtick.labelsize": "x-large",
    "ytick.labelsize": "x-large",
}

pylab.rcParams.update(params)

interactive(True)
from dataclasses import dataclass


# Helper for printing 'Clickable' URL in Jupyter Notebook
@dataclass(frozen=True)
class Url:
    """Wrapper around a URL string to provide nice display in IPython environments."""

    __url: str

    def _repr_html_(self):
        """HTML link to this URL."""
        return f'<a href="{self.__url}">{self.__url}</a>'

    def __str__(self):
        """Return the underlying string."""
        return self.__url


class LP3:
    """Calculate synthetic gage statistics, including the station skew,
       weighted skew, and the log-Person Type III flow frequency
       distribution.
    """

    def __init__(self, discharge: list):
        self._records = discharge
        self._n = len(discharge)
        self._log = np.log10(discharge)
        self._mean = np.mean(self._log)
        self._std = np.std(self._log, ddof=1)

    @property
    def log(self):
        return self._log

    def station_skew(self) -> float:
        """The station (local) skew coefficient.
        """
        return (self._n / ((self._std ** 3) * (self._n - 1) * (self._n - 2))) * np.sum((self._log - self._mean) ** 3)

    def station_mse(self) -> float:
        """The mean square errors(MSE) of the station (local) skew.
        """
        abs_sskew = np.abs(self.station_skew())
        a = -0.33 + 0.08 * abs_sskew
        b = 0.94 - 0.26 * abs_sskew
        if abs_sskew > 0.90:
            a = -0.52 + 0.30 * abs_sskew
        if abs_sskew > 1.50:
            b = 0.55
        return 10 ** (a - b * np.log10(self._n / 10.0))

    def weighted_skew(self, rskew: float, rskew_mse: float) -> float:
        """The weighted skew coefficient. This skew is the average of the
           regional and station skews weighted by their respective mean square
           errors.
        """
        sskew = self.station_skew()
        sskew_mse = self.station_mse()
        w = rskew_mse / (sskew_mse + rskew_mse)
        return w * sskew + (1 - w) * rskew

    def lp3_values(self, aep: list, rskew: float, rskew_mse: float) -> list:
        """Calculates the discharge for the passed annual exceedance
           probabilities using the log-Person Type III distribution.
        """
        skew = self.weighted_skew(rskew, rskew_mse)
        mu = self._mean
        std = self._std
        q = []
        for ep in aep:
            pct = 1 - ep
            lp3_val = 10 ** stats.pearson3.ppf(pct, skew=skew, loc=mu, scale=std)
            q.append(lp3_val)
        return q


def ecdf(data):
    """ Compute ECDF """
    x = np.sort(data)
    n = x.size
    y = np.arange(1, n + 1) / (n + 1)
    return (x, y)


# Plotting Functions


def log_plot_format(y, pos):
    formatstring = "{:,}".format(int(y))
    return formatstring.format(y)


def logit_plot_format(y, pos):
    show_percentiles = [
        "$0.00200$",
        "0.05",
        "0.01",
        "0.20",
        "0.40",
        "0.50",
        "0.60",
        "0.70",
        "0.80",
        "0.90",
        "0.95",
        "0.98",
    ]
    if y in show_percentiles:
        formatstring = "{}".format(int(y.replace("$", "")) * 100)
    else:
        formatstring = ""
    return formatstring.format(y)


def plot_aep_full(aeps, aep_qs, skew, mu, sigma, color="Brown", ci=95):
    # PDF
    fig, ax = plt.subplots(figsize=(30, 8))

    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    gs = gridspec.GridSpec(ncols=6, nrows=1, figure=fig)

    fax1 = fig.add_subplot(gs[0:5])
    fax2 = fig.add_subplot(gs[5], sharey=fax1)

    fax2.axes.yaxis.set_visible(False)
    fax2.axes.xaxis.set_visible(False)

    x = np.linspace(
        pearson3.ppf(0.0001, skew, loc=mu, scale=sigma), pearson3.ppf(0.9999, skew, loc=mu, scale=sigma), 100
    )

    fax2.plot(pearson3.pdf(x, skew, loc=mu, scale=sigma), 10 ** x, "black", lw=2, alpha=1, label="pearson3 pdf")

    density_range = pearson3.pdf(x, skew, loc=mu, scale=sigma)

    # -----------------------------------------------------------------------------------------------------------------------------------------------------

    # fax2.fill_between(, 0, 100, color='black', alpha = 0.2)
    # fax2.fill_between(density_range, q90lower, q90upper, color='gray', alpha = 0.2)
    # fax2.fill_between(density_range, q90lower, pdfmin, color='lightgray', alpha = 0.2)
    fax2.set_xlim([0, np.max(density_range)])
    fax1.set_ylim([20000, 1200000])

    fax2.set_yscale("log")

    pdfmin = 10 ** x[0]
    pdfmax = 10 ** x[-1]

    # adjust the line for to match the extent of peakfq plots
    fax1.plot(aeps[1:-10], aep_qs[1:-10], "black", linewidth=2, alpha=0.8)

    # Plot Formatting
    # fax1.invert_xaxis()
    fax1.set_xscale("logit")

    # fax1.xaxis.set_major_formatter(ticker.FuncFormatter(myLogitFormat))
    fax1.set_yscale("log")
    fax1.set_xlim([0.990, 0.002])
    fax1.set_ylim([20000, 1200000])
    # fax1.set_xlabel('Annual exceedance probability, [%]');fax1.set_ylabel('Discharge, [cfs]')
    fax1.set_title("Flow Frequency Curve")
    fax1.grid(True, which="both")
    fax1.xaxis.set_minor_formatter(ticker.FuncFormatter(logit_plot_format))
    fax1.yaxis.set_major_formatter(ticker.FuncFormatter(log_plot_format))
    fax1.set_xlabel("Annual Exceendence Probability")
    fax1.set_ylabel("Flow (cfs)")

    # fax1.axhline(pdfmax, 0, 1e9, color='purple');
    upper_ci, lower_ci = ci * 0.01, (100 - ci) * 0.01

    qupper = int(10 ** pearson3.ppf(upper_ci, skew, loc=mu, scale=sigma))
    qlower = int(10 ** pearson3.ppf(lower_ci, skew, loc=mu, scale=sigma))

    fax1.fill_between(np.arange(0.990, 0.002, -0.001), pdfmax, qupper, color="gray", alpha=0.2)
    fax1.fill_between(np.arange(0.990, 0.002, -0.001), qlower, qupper, color="black", alpha=0.2)
    fax1.fill_between(np.arange(0.990, 0.002, -0.001), qlower, pdfmin, color="gray", alpha=0.2)

    fax2.grid()
    fig.tight_layout(pad=1.00, h_pad=0, w_pad=-1, rect=None)
    return fig, fax1


def add_emperical_plot_full(aeps, aep_qs, emp_q, emp_ri, skew, mu, sigma, color="brown", s=40, ci=95):
    f, a = plot_aep_full(aeps, aep_qs, skew, mu, sigma, ci)
    a.scatter(x=emp_ri, y=sorted(emp_q, reverse=True), color=color, s=s)
    return f, a


def add_boostrap_plot_full(aeps, aep_qs, skew, mu, sigma, nbs=1, nsamples=50, color="brown", s=25):
    f, a = plot_aep_full(aeps, aep_qs, skew, mu, sigma)
    for i in range(0, nbs):
        r = pearson3.rvs(skew, loc=mu, scale=sigma, size=nsamples)
        emp_q, emp_ri = ecdf(r)
        a.scatter(x=emp_ri, y=sorted(10 ** np.array(emp_q), reverse=True), color=color, s=s)
    return f, a


def add_boostrap_plot_from_sample_pop_full(aeps, aep_qs, skew, mu, sigma, nbs=1, nsamples=10, color="brown", s=25):
    f, a = plot_aep_full(aeps, aep_qs, skew, mu, sigma)
    for i in range(0, nbs):
        r = np.random.choice(aep_qs, size=nsamples)
        emp_q, emp_ri = ecdf(r)
        a.scatter(x=emp_ri, y=sorted(emp_q, reverse=True), color="brown", s=s)
    return f, a
