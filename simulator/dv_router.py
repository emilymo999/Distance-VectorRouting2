"""
Your awesome Distance Vector router for CS 168

Based on skeleton code by:
  MurphyMc, zhangwen0411, lab352
"""

import sim.api as api
from cs168.dv import (
    RoutePacket,
    Table,
    TableEntry,
    DVRouterBase,
    Ports,
    FOREVER,
    INFINITY,
)


class DVRouter(DVRouterBase):

    # A route should time out after this interval
    ROUTE_TTL = 15

    # -----------------------------------------------
    # At most one of these should ever be on at once
    SPLIT_HORIZON = False
    POISON_REVERSE = False
    # -----------------------------------------------

    # Determines if you send poison for expired routes
    POISON_EXPIRED = False

    # Determines if you send updates when a link comes up
    SEND_ON_LINK_UP = False

    # Determines if you send poison when a link goes down
    POISON_ON_LINK_DOWN = False

    def __init__(self):
        """
        Called when the instance is initialized.
        DO NOT remove any existing code from this method.
        However, feel free to add to it for memory purposes in the final stage!
        """
        assert not (
            self.SPLIT_HORIZON and self.POISON_REVERSE
        ), "Split horizon and poison reverse can't both be on"

        self.start_timer()  # Starts signaling the timer at correct rate.

        # Contains all current ports and their latencies.
        # See the write-up for documentation.
        self.ports = Ports()

        # This is the table that contains all current routes
        self.table = Table()
        self.table.owner = self

        ##### Begin Stage 10A #####

        ##### End Stage 10A #####

    def add_static_route(self, host, port):
        """
        Adds a static route to this router's table.

        Called automatically by the framework whenever a host is connected
        to this router.

        :param host: the host.
        :param port: the port that the host is attached to.
        :returns: nothing.
        """
        # `port` should have been added to `peer_tables` by `handle_link_up`
        # when the link came up.
        assert port in self.ports.get_all_ports(), "Link should be up, but is not."

        ##### Begin Stage 1 #####
        l = self.ports.get_latency(port)
        self.table[host] = TableEntry(dst=host, port=port, latency=l, expire_time=api.current_time()+FOREVER)
        ##### End Stage 1 #####

    def handle_data_packet(self, packet, in_port):
        """
        Called when a data packet arrives at this router.

        You may want to forward the packet, drop the packet, etc. here.

        :param packet: the packet that arrived.
        :param in_port: the port from which the packet arrived.
        :return: nothing.
        """
        
        ##### Begin Stage 2 #####

        # get destination and any routes toward that dest
        destination = packet.dst
        route = self.table.get(destination)

        # if there are no routes then return
        if route is None:
            return
        
        # total cost of path in routing table for that dest
        if route.latency >= INFINITY:

            return
        
        # current cost of physical link on port p rn
        if self.ports.get_latency(route.port) >= INFINITY:
            return

        # send out of the packet I decided to use
        self.send(packet, port=route.port)

        ##### End Stage 2 #####

    def send_routes(self, force=False, single_port=None):
        """
        Send route advertisements for all routes in the table.

        :param force: if True, advertises ALL routes in the table;
                      otherwise, advertises only those routes that have
                      changed since the last advertisement.
               single_port: if not None, sends updates only to that port; to
                            be used in conjunction with handle_link_up.
        :return: nothing.
        """
        
        ##### Begin Stages 3, 6, 7, 8, 10 #####

        for destination, route in self.table.items():
            for port in self.ports.get_all_ports():

                # if not at port we want to advertise to
                if single_port is not None and port is not single_port:
                    continue
                
                if self.POISON_REVERSE and port == route.port:
                    latency = INFINITY
                elif self.SPLIT_HORIZON and port == route.port:
                    continue
                else:
                    latency = route.latency

                if latency > INFINITY:
                    latency = INFINITY

                self.send_route(port, destination, latency)

        ##### End Stages 3, 6, 7, 8, 10 #####

    def expire_routes(self):
        """
        Clears out expired routes from table.
        accordingly.
        """
        
        ##### Begin Stages 5, 9 #####
        expired = []
        for dst, route in self.table.items():
            if route.expire_time <= api.current_time():
                expired.append(dst)
        
        for dst in expired:
            if self.POISON_EXPIRED:
                old = self.table[dst]
                poisoned = TableEntry(dst=dst, port=old.port, latency=INFINITY, expire_time=api.current_time()+self.ROUTE_TTL)
                self.table[dst] = poisoned
            else:
                self.table.pop(dst)

        # this entry is expired

        ##### End Stages 5, 9 #####

    def handle_route_advertisement(self, route_dst, route_latency, port):
        """
        Called when the router receives a route advertisement from a neighbor.

        :param route_dst: the destination of the advertised route.
        :param route_latency: latency from the neighbor to the destination.
        :param port: the port that the advertisement arrived on.
        :return: nothing.
        """
        
        ##### Begin Stages 4, 10 #####
        current_entry = self.table.get(route_dst)
        new_latency = route_latency + self.ports.get_latency(port)

        if current_entry is not None:
            current_next_hop = current_entry.port
        else:
            current_next_hop = None

        if current_entry is None or (current_entry is not None and new_latency < current_entry.latency) or port == current_next_hop:
            self.table[route_dst] = TableEntry(dst=route_dst, port=port, latency=new_latency, expire_time=api.current_time()+self.ROUTE_TTL)
        ##### End Stages 4, 10 #####

    def handle_link_up(self, port, latency):
        """
        Called by the framework when a link attached to this router goes up.

        :param port: the port that the link is attached to.
        :param latency: the link latency.
        :returns: nothing.
        """
        self.ports.add_port(port, latency)

        ##### Begin Stage 10B #####

        ##### End Stage 10B #####

    def handle_link_down(self, port):
        """
        Called by the framework when a link attached to this router goes down.

        :param port: the port number used by the link.
        :returns: nothing.
        """
        self.ports.remove_port(port)

        ##### Begin Stage 10B #####

        ##### End Stage 10B #####

    # Feel free to add any helper methods!
