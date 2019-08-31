# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 15:59:14 2019

@author: cosmic being
"""

class Vertex:
    """ Vertex structure for a gragh
    @ Members: 'name'
               'state': A list storing previous and current states of this object
               'content': A set storing contents of this object if it is not a type of motion
               'category': category this object belongs to
               'img_path': file path where storing images of this object 
    """

    __slots__='_element', '_name', '_state', '_contents', '_category', '_img_path'

    def __init__(self,x,name,state=None,contents=None,category=None,imgpath=None):
        self._element=x
        self._name=name
        self._state=state
        self._contents=contents
        self._category=category
        self._img_path=imgpath

    def get_element(self):
        """Return element associated with this vertex"""
        return self.element

    def set_img_path(self, path):
        self.img_path=path

    def get_img_path(self):
        return self.img_path

    def __str__(self):
        string='+ ' + '- '*20 + '+'+'\n'
        string+='|'+15*' '+'Object Node'+15*' '+'|'+'\n'
        string+='| '+'Object name: '+self._name+(27-len(self._name))*' '+'|'+'\n'
        string+='| '+'Object category: '+self._category+(23 - len(self._category)) * ' ' + '|'+'\n'

        string+='| '+'Object current state: '+self._state[-1]+(18 - len(self._state[-1])) * ' ' + '|'+'\n'

        substring1=''
        if len(self._state) >=1:
            for i in range(len(self._state)-1):
                substring1+='| '+'Object history state {}'.format(i)+': '+self._state[i]+(16 - len(self._state[i])) * ' ' + '|'+'\n'

        string+=substring1
        substring2=''
        if self._contents !=None:
            for i in range(len(self._contents)):
                substring2+='| '+'Object contents: '+self._contents[i]+(28 - len(self._contents[i])) * ' ' + '|'+'\n'
        else:
            substring2='| '+'Object contents: None'+19*' ' + '|'+'\n'

        string+=substring2
        string+='+ '+'- '*20+'+'+'\n'

        return string

    def __hash__(self):   #Allow vertex to be a map/set key
        return hash(id(self))


class Edge:
    """Edge structure for a gragh"""
    __slots__=('_origin','_destination','_element')

    def __init(self,u,v,x):
        self._origin=u
        self._destination=v
        self._element=x

    def get_endpoint(self):
        """Return (u, v) tuple"""
        return (self._origin,self._destination)

    def get_opposite(self,v):
        """Return the vertex that is opposite to v on this edge"""
        if v is self._origin:
            return self._destination
        else:
            return self._origin

    def get_element(self):
        """"Return element associated with this edge."""
        return self._element

    def __hash__(self):
        """Allow edge to be a map/set key."""
        return hash((self._origin, self._destination))

class Graph:
    """Representation of a simple gragh using adjacency map."""
    def __init__(self, directed=False):
        """Create an empty directional gragh (Default: undirected).
        The Gragh is directed if optional parameter is set to True."""

        self._outgoing={} # Secondary_map dict storing outgoing edges with vertices as keys, secondary_map as values
        # Only create second map for directed graghs; Use alias for undirected
        # Secondary_map dict storing incident edges with vertices as keys, secondary_map as values
        self._incident={} if directed else self._outgoing

    def is_derected(self):
        """Return True if this is a directed gragh; False if undirected."""
        return self._incident is not _outgoing

    def vertex_count(self):
        """Return the number of vertices in the gragh."""
        return len(self._outgoing)

    def vertices(self):
        """Return an iteration of vertices in the gragh"""
        return self._outgoing.keys()

    def edge_count(self):
        """Return the number of edges in the gragh"""
        total=sum(len(self._outgoing[v]) for v in self._outgoing )

        # For undirected graghs, make sure not to double count edges
        return total if self.is_derected() else total//2

    def edges(self):
        """Return a set of all edges in the gragh"""
        result=set() # Use set to avoid double counting edges in undirected gragh
        for secondary_map in self._outgoing.values():
            result.update(secondary_map.values())

        return result

    def get_edges(self,u,v):
        """Return the edge from u to v, or None if not adjacent"""
        return self._outgoing[u].get(v)

    def degree(self,v,incident=True):
        """Return the number of edges incident to  vertex v in the gragh.
        if gragh is directed, optional parameter used to count outgoing edges from v"""
        opt=self._incident if incident ==True else self._outgoing
        return len(opt[v])

    def incident_edges(self,v):
        """Return all edges incident to vertex v in the gragh.
        If gragh is directed, optional parameter used to request incident edges"""
        for edge in self._incident[v].values():
            yield edge

    def outgoing_edges(self,v):
        """Return all edges incident to vertex v in the gragh.
        If gragh is directed, optional parameter used to request incident edges"""
        for edge in self._outgoing[v].values():
            yield edge

    def insert_incident_edge(self,u,v,x):
        """ Insert an edge incident from u to v"""
        e=self.Edge(u,v,x)
        self._outgoing[u][v]=e
        self._incident[v][u]=e

    def insert_vertex(self,x):
        """ Insert and return a vertex with element x"""
        v=self.Vertex(x)
        self._incident[v]={}
        if self.is_derected()==True:
            self._outgoing[v]={}
        return v

    def remove_vertex(self,v):
        for it in self.vertices():
            if v is it:







v=Vertex(x=1,name='Apple',state=['Unchopped','Chopped'],contents=None,category='Fruit')

print(v)


















