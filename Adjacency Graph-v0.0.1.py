# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 15:59:14 2019

@author: cosmic being
"""
"""
Ontology based on adjacency graph 

"""
class Vertex:
    """ Vertex structure for a graph
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

        substring1 = ''
        if self._state != None:
            string += '| ' + 'Object current state: ' + self._state[-1] + (18 - len(self._state[-1])) * ' ' + '|' + '\n'
            if len(self._state) >= 1:
                for i in range(len(self._state) - 1):
                    substring1 += '| ' + 'Object history state {}'.format(i) + ': ' + self._state[i] + (16 - len(
                        self._state[i])) * ' ' + '|' + '\n'

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
    """Edge structure for a graph"""
    __slots__=('_origin','_destination','_element')

    def __init__(self,u,v,x):
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

    def __str__(self):
        string1='+'+' -'*20+' +'+'\n'
        string2='| '+'                 Edge {}'.format(self._element)+'                 |\n'
        substring=self._origin._name+'('+self._origin._state[-1]+')'+ ' to '\
                  +self._destination._name+'('+self._destination._state[-1]+')'
        string3='| '+substring+(len(string1)-len(substring)-4)*' '+'|\n'
        string4='+'+' -'*20+' +'+'\n'
        string=string1+string2+string3+string4

        return string

class Graph:
    """Representation of a simple graph using adjacency map."""
    def __init__(self, title='Untitled',directed=False):
        """Create an empty directional graph (Default: undirected).
        The graph is directed if optional parameter is set to True."""

        self._outgoing={} # Secondary_map dict storing outgoing edges with vertices as keys, secondary_map as values
        # Only create second map for directed graghs; Use alias for undirected
        # Secondary_map dict storing incident edges with vertices as keys, secondary_map as values
        self._incident={} if directed else self._outgoing
        self.title=title

    def is_derected(self):
        """Return True if this is a directed graph; False if undirected."""
        return self._incident is not self._outgoing

    def vertex_count(self):
        """Return the number of vertices in the graph."""
        return len(self._outgoing)

    def vertices(self):
        """Return an iteration of vertices in the graph"""
        return self._incident.keys()

    def edge_count(self):
        """Return the number of edges in the graph"""
        total=sum(len(self._outgoing[v]) for v in self._outgoing )

        # For undirected graghs, make sure not to double count edges
        return total if self.is_derected() else total//2

    def edges(self):
        """Return a set of all edges in the graph"""
        result=set() # Use set to avoid double counting edges in undirected graph
        for secondary_map in self._outgoing.values():
            result.update(secondary_map.values())

        return result

    def get_edges(self,u,v):
        """Return the edge from u to v, or None if not adjacent"""
        return self._outgoing[u].get(v)

    def degree(self,v,incident=True):
        """Return the number of edges incident to  vertex v in the graph.
        if graph is directed, optional parameter used to count outgoing edges from v"""
        opt=self._incident if incident ==True else self._outgoing
        return len(opt[v])

    def incident_edges(self,v):
        """Return all edges incident to vertex v in the graph.
        If graph is directed, optional parameter used to request incident edges"""
        for edge in self._incident[v].values():
            yield edge

    def outgoing_edges(self,v):
        """Return all edges incident to vertex v in the graph.
        If graph is directed, optional parameter used to request incident edges"""
        for edge in self._outgoing[v].values():
            yield edge

    def insert_incident_edge(self,u,v,x):
        """ Insert an edge incident from u to v"""
        e=Edge(u,v,x)
        (self._outgoing[u]).update({v:e})#[v]=e
        (self._incident[v]).update({u:e})#[u]=e

    def insert_vertex(self,v):
        """ Insert and return a vertex with element x"""
        #v=Vertex(x)
        self._incident[v]={}
        if self.is_derected()==True:
            self._outgoing[v]={}

    def remove_vertex(self,v): # Computational complexity: O(deg(v))
        """ Remove vertex v and all edges connected to it"""
        try:
            if v not in self._outgoing and v not in self._incident:
                raise Exception
            if self.is_derected() == True:
                for it in self._incident[v].keys():
                    self._outgoing[it].pop(v)
                self._incident.pop(v)
                for it in self._outgoing[v].keys():
                    self._incidnt[it].pop(v)
                self._outgoing.pop(v)
            else:
                for it in self._incident[v].keys():
                    self._incident[it].pop(v)
                self._incident.pop(v)
        except Exception as e:
            print( 'Vertex v is not a member in the graph!')




    def remove_edge(self,u,v): # Computational complexity: O(1)
        """ Remove the edge connecting u with v"""
        try:
            if v in self._incident[u]:
                self._incident[u].pop(v)
                self._outgoing[v].pop(u)
            elif v in self._outgoing[u]:
                self._outgoing[u].pop(v)
                self._incident[v].pop(u)
            else: raise Exception
        except Exception as e:
            print('No edge connecting u with v!')


    def __str__(self):
        width=40
        string = '+ ' + '- ' * width + '+' + '\n'

        title='Graph: {}'.format(self.title)
        gap=int(width-len(title)/2)
        title_string = '| '+gap*' '+title+gap*' '+' |\n'
        string+=title_string

        list_string=''
        for start_p in self._outgoing.keys():
            for end_p in self._outgoing[start_p].keys():
                if start_p._category != 'Motion' and end_p._category != 'Motion':
                    seq_string = '{}({}) --> {}({})'.format(start_p._name, start_p._state[-1], end_p._name,
                                                            end_p._state[-1])
                elif start_p._category == 'Motion' and end_p._category != 'Motion':
                    seq_string = '{} --> {}({})'.format(start_p._name, end_p._name,
                                                            end_p._state[-1])
                elif start_p._category != 'Motion' and end_p._category == 'Motion':
                    seq_string = '{}({}) --> {}'.format(start_p._name,  start_p._state[-1],
                                                        end_p._name)

                gap=int(width-len(seq_string)/2)
                substring='| '+gap*' '+seq_string+gap*' '+' |\n'
                list_string += substring

        string+=list_string
        string+='+ ' + '- ' * width + '+' + '\n'

        return string



        string += '+ ' + '- ' * 20 + '+' + '\n'

        return string







u=Vertex(x=1,name='Knife',state=['clean'],contents=None,category='Utensil')
v=Vertex(x=2,name='Apple',state=['Unchopped'],contents=None,category='Fruit')
w=Vertex(x=3,name='Cut1',category='Motion')
u1=Vertex(x=4,name='Knife',state=['clean','dirty'],contents=None,category='Utensil')
v1=Vertex(x=2,name='Apple',state=['Unchopped','Chopped'],contents=None,category='Fruit')

g=Graph(directed=True)
g.insert_vertex(u)
g.insert_vertex(v)
g.insert_vertex(w)
g.insert_vertex(u1)
g.insert_vertex(v1)

g.insert_incident_edge(u,w,1)
g.insert_incident_edge(v,w,2)
g.insert_incident_edge(w,u1,3)
g.insert_incident_edge(w,v1,4)


print(g)

g.remove_vertex(u1)

print(g)














