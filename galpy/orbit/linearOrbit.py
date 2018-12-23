import warnings
import numpy as nu
from scipy import integrate
from .OrbitTop import OrbitTop
from ..potential.linearPotential import \
    _evaluatelinearForces, evaluatelinearPotentials
from ..potential.Potential import _check_c
from galpy.util.leung_dop853 import dop853
import galpy.util.bovy_symplecticode as symplecticode
from galpy.util.bovy_conversion import physical_conversion
from galpy.util import galpyWarning, galpyWarningVerbose
from .integrateLinearOrbit import integrateLinearOrbit_c, _ext_loaded
ext_loaded= _ext_loaded
class linearOrbit(OrbitTop):
    """Class that represents an orbit in a (effectively) one-dimensional potential"""
    def __init__(self,vxvv=[1.,0.],vo=220.,ro=8.0):
        """
        NAME:

           __init__

        PURPOSE:

           Initialize a linear orbit

        INPUT:

           vxvv - [x,vx]

           vo - circular velocity at ro (km/s)

           ro - distance from vantage point to GC (kpc)

        OUTPUT:

           (none)

        HISTORY:

           2010-07-13 - Written - Bovy (NYU)

        """
        OrbitTop.__init__(self,vxvv=vxvv,
                          ro=ro,zo=None,vo=vo,solarmotion=None)
        return None

    def integrate(self,t,pot,method='odeint',dt=None):
        """
        NAME:
           integrate
        PURPOSE:
           integrate the orbit
        INPUT:
           t - list of times at which to output (0 has to be in this!)
           pot - potential instance or list of instances
           method= 'odeint'= scipy's odeint, or 'leapfrog'
           dt= (None) if set, force the integrator to use this basic stepsize; must be an integer divisor of output stepsize (NOT USED FOR LINEAR ORBIT SO FAR)
        OUTPUT:
           (none) (get the actual orbit using getOrbit()
        HISTORY:
           2010-07-13 - Written - Bovy (NYU)
        """
        if hasattr(self,'_orbInterp'): delattr(self,'_orbInterp')
        self.t= nu.array(t)
        self._pot= pot
        self.orbit= _integrateLinearOrbit(self.vxvv,pot,t,method,dt)

    @physical_conversion('energy')
    def E(self,*args,**kwargs):
        """
        NAME:
           E
        PURPOSE:
           calculate the energy
        INPUT:
           t - (optional) time at which to get the radius
           pot= linearPotential instance or list thereof
        OUTPUT:
           energy
        HISTORY:
           2010-09-15 - Written - Bovy (NYU)
        """
        if not 'pot' in kwargs or kwargs['pot'] is None:
            try:
                pot= self._pot
            except AttributeError:
                raise AttributeError("Integrate orbit or specify pot=")
            if 'pot' in kwargs and kwargs['pot'] is None:
                kwargs.pop('pot')          
        else:
            pot= kwargs.pop('pot')
        if len(args) > 0:
            t= args[0]
        else:
            t= 0.
        #Get orbit
        thiso= self(*args,**kwargs)
        onet= (len(thiso.shape) == 1)
        if onet:
            return evaluatelinearPotentials(pot,thiso[0],
                                            t=t,use_physical=False)\
                                            +thiso[1]**2./2.
        else:
            return nu.array([evaluatelinearPotentials(pot,thiso[0,ii],
                                                      t=t[ii],
                                                      use_physical=False)\
                                 +thiso[1,ii]**2./2.\
                                 for ii in range(len(t))])

    def e(self,analytic=False,pot=None): #pragma: no cover
        """
        NAME:
           e
        PURPOSE:
           calculate the eccentricity
        INPUT:
        OUTPUT:
           eccentricity
        HISTORY:
           2010-09-15 - Written - Bovy (NYU)
        """
        raise AttributeError("linearOrbit does not have an eccentricity")

    def rap(self,analytic=False,pot=None): #pragma: no cover
        raise AttributeError("linearOrbit does not have an apocenter")

    def rperi(self,analytic=False,pot=None): #pragma: no cover
        raise AttributeError("linearOrbit does not have a pericenter")

    def zmax(self): #pragma: no cover
        raise AttributeError("linearOrbit does not have a zmax")

def _integrateLinearOrbit(vxvv,pot,t,method,dt):
    """
    NAME:
       integrateLinearOrbit
    PURPOSE:
       integrate a one-dimensional orbit
    INPUT:
       vxvv - initial condition [x,vx]
       pot - linearPotential or list of linearPotentials
       t - list of times at which to output (0 has to be in this!)
       method - 'odeint' or 'leapfrog'
    OUTPUT:
       [:,2] array of [x,vx] at each t
    HISTORY:
       2010-07-13- Written - Bovy (NYU)
       2018-10-05- Added support for C integration - Bovy (UofT)
    """
    #First check that the potential has C
    if '_c' in method:
        if not ext_loaded or not _check_c(pot):
            if ('leapfrog' in method or 'symplec' in method):
                method= 'leapfrog'
            else:
                method= 'odeint'
            if not ext_loaded: # pragma: no cover
                warnings.warn("Cannot use C integration because C extension not loaded (using %s instead)" % (method), galpyWarning)
            else:
                warnings.warn("Cannot use C integration because some of the potentials are not implemented in C (using %s instead)" % (method), galpyWarning)
    if method.lower() == 'leapfrog':
        # Scaling of initial condition for stepsize determination
        xscale= nu.fabs(vxvv[0])
        vscale= nu.fabs(vxvv[1])
        scaling= nu.array([xscale,vscale])
        return symplecticode.leapfrog_general(\
            lambda x: nu.array([x[1],0.]),
            lambda x,t=t: nu.array([0.,_evaluatelinearForces(pot,x[0],t=t)]),
            vxvv,t,rtol=10.**-8,
            scaling=scaling,metric=lambda x,y: nu.fabs(x-y))
    elif method.lower() == 'dop853':
        return dop853(func=_linearEOM, x=vxvv, t=t, args=(pot,))
    elif ext_loaded and \
            (method.lower() == 'leapfrog_c' or method.lower() == 'rk4_c' \
            or method.lower() == 'rk6_c' or method.lower() == 'symplec4_c' \
            or method.lower() == 'symplec6_c' or method.lower() == 'dopr54_c' \
            or method.lower() == 'dop853_c'):
        warnings.warn("Using C implementation to integrate orbits",
                      galpyWarningVerbose)
        out, msg= integrateLinearOrbit_c(pot,nu.array(vxvv),t,method,dt=dt)
        return out
    elif method.lower() == 'odeint' or not ext_loaded:
        return integrate.odeint(_linearEOM,vxvv,t,args=(pot,),rtol=10.**-8.)

def _linearEOM(y,t,pot):
    """
    NAME:
       linearEOM
    PURPOSE:
       the one-dimensional equation-of-motion
    INPUT:
       y - current phase-space position
       t - current time
       pot - (list of) linearPotential instance(s)
    OUTPUT:
       dy/dt
    HISTORY:
       2010-07-13 - Bovy (NYU)
    """
    return [y[1],_evaluatelinearForces(pot,y[0],t=t)]