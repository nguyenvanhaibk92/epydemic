# SIR with a fixed recovery time
#
# Copyright (C) 2017 Simon Dobson
# 
# This file is part of epydemic, epidemic network simulations in Python.
#
# epydemic is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# epydemic is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with epydemic. If not, see <http://www.gnu.org/licenses/gpl.html>.

from epydemic import SIR

class SIR_FixedRecovery(SIR):
    '''The Susceptible-Infected-Removed :term:`compartmented model of disease`,
    in the variation where the time spent infected is fixed rather than happening
    with some probability.'''
    
    # the additional model parameter
    T_INFECTED = 'epydemic.SIR_FR.tInfected'    #: Parameter for the time spent infected before removal/recovery.

    # node attribute for infection time
    INFECTION_TIME = 'infection_time'           #: Attribute recording when a node became infected
    
    def __init__( self ):
        super(SIR_FixedRecovery, self).__init__()

    def build( self, params ):
        '''Build the variant SIR model. The difference between this and the
        reference :class:`SIR` model is that only infection events happen
        probabilistically, with removal events happening on a fixed schedule
        depending on the :attr:`T_INFECTED` parameter.

        :param params: the model parameters'''
        pInfected = params[self.P_INFECTED]
        pInfect = params[self.P_INFECT]
        self._tInfected = params[self.T_INFECTED]
        
        self.addCompartment(self.SUSCEPTIBLE, 1 - pInfected)
        self.addCompartment(self.INFECTED, pInfected)
        self.addCompartment(self.REMOVED, 0.0)

        self.trackEdgesBetweenCompartments(self.SUSCEPTIBLE, self.INFECTED, name = self.SI)
        self.addFixedRateEvent(self.SI, pInfect, self.infect)

    def setUp( self, params ):
        '''After setting up as normal, post remove events for any nodes that are
        initially infected.

        :param params: the simulation parameters'''
        super(SIR_FixedRecovery, self).setUp(params)

        # traverse the set of initially-infected nodes
        tInfected = params[self.T_INFECTED]
        g = self.network()
        for n in self.compartment(self.INFECTED):
            # record that the node was initially infected
            g.nodes[n][self.INFECTION_TIME] = 0.0
        
            # post the corresponding removal event
            self.postEvent(tInfected, n, self.remove)
        
    def infect( self, t, e ):
        '''Perform the normal infection event, and then post an event to remove the
        infected node at the appropriate time.

        :param t: the simulation time
        :param e: the edge transmitting the infection, susceptible-infected'''

        # infect as normal
        super(SIR_FixedRecovery, self).infect(t, e)

        # record the infection time
        (n, _) = e
        self.network().nodes[n][self.INFECTION_TIME] = t
        
        # post the removal event for the appropriate time in the future
        self.postEvent(t + self._tInfected, n, self.remove)
   
