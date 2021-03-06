# -*- coding: utf-8 -*-
""" Electron properties """

import numpy as np
from scipy.constants import speed_of_light, Planck, elementary_charge, electron_mass

def lorentz(keV):
    """
    Relativistic factor :math:`\gamma`, defined as :math:`\gamma = \\frac{1}{\sqrt{1 - v^2/c^2}}`

    Parameters
    ----------
    keV : array_like or float
        Electron energy [keV].
    
    Returns
    -------
    out : array_like or float
    """
    return 1/np.sqrt(1 + (elementary_charge*keV*1e3)/(2*electron_mass*speed_of_light**2))

def electron_wavelength(keV):
    """ 
    Relativistic wavelength of an accelerated electron.
        
    Parameters
    ----------
    keV : array_like or float
        Electron energy [keV].
    
    Returns
    -------
    out : float
        Electron wavelength [Angs]
    """
    return (Planck/np.sqrt(2*electron_mass*elementary_charge*keV*1e3))*lorentz(keV)*1e10

def interaction_parameter(keV):
    """
    Interaction parameter from relativistic electron wavelength.

    Parameters
    ----------
    keV : array_like or float
        Electron energy [keV].
    
    Returns
    -------
    out : float
        Interaction parameter [rad/(V*Angs)]

    References
    ----------
    .. Kirkland 2010 Eq. 5.6
    """
    l = electron_wavelength(keV)
    V = keV * 1e3

    return (2*np.pi)/(electron_wavelength(keV)*V)*(electron_mass*speed_of_light**2 + elementary_charge * V)/(2*electron_mass*speed_of_light**2 + elementary_charge * V)