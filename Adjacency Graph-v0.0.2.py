# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 15:59:14 2019
Last modified on Sun Sept 8 10:07 2019
@author: 
"""
"""
Ontology based on adjacency graph 

"""
import copy


class Vertex:
    """ Vertex structure for a graph
    @ Members: 'name'
               'state': A list storing previous and current states of this object
               'content': A set storing contents of this object if it is not a type of motion
               'category': category this object belongs to
               'img_path': file path where storing images of this object 
    """

    __slots__='_element', '_name', '_state', '_contents', '_category', '_img_path'

    def __init__(self,x=None,name=None,state=None,contents=None,category=None,imgpath=None):
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

    def __eq__(self,other):
        return self._name==other._name and self._state==other._state and self._contents==other._contents and self._category==other._category and self._img_path==other._img_path

class Edge:
    """Edge structure for a graph.
    Every edge represents a motions which consists of utensils and motions.
    """

    # The origin(an object with initial states) goes through the motions and
    # will then  become destination(the same object with new states).
    #
    # The private variable 'motions'  is a list storing utensil-motion pair. It consists of 'utensils' and 'motions', which means these 'utensils' impose effects
    # on 'origin' with thess very 'motions'. For example: (Knife, Cut), (Blender, blend)
    __slots__=('_origin','_destination','_motions')

    def __init__(self,u,v,motions_pairs=None):
        self._origin=u
        self._destination=v
        if motions_pairs is None:
            self._motions=[]
        else:
            self._motions=copy.deepcopy(motions_pairs)

    def add_motions(self, pairs):
        """ add a new motions to this edge"""
        self._motions+=pairs

    def display_motions(self):
        for i in range(len(self._motions)):
            print('Motion {}:'.format(i),self._motions[i][1]._name,'with',self._motions[i][0]._name)


    def get_endpoint(self):
        """Return (u, v) tuple"""
        return (self._origin,self._destination)

    def get_opposite(self,v):
        """Return the vertex that is opposite to v on this edge"""
        if v is self._origin:
            return self._destination
        else:
            return self._origin


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
        self.recipe=set()

    def is_derected(self):
        """Return True if this is a directed graph; False if undirected."""
        return self._incident is not self._outgoing

    def vertex_count(self):
        """Return the number of vertices in the graph."""
        return len(self._outgoing)

    def object_amount(self):
        return self.vertex_count()

    def vertices(self):
        """Return an iteration of vertices in the graph"""
        return self._incident.keys()

    def edge_count(self,is_only_direction=True):
        """Return the number of edges in the graph"""
        total=0
        for u in self._outgoing:
            for v in self._outgoing[u]:
                total+= len(self._outgoing[u][v])

        # For undirected graghs, make sure not to double count edges
        return total if self.is_derected() else total//2

    def process_amount(self):
        return self.edge_count()

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

    def insert_vertex(self,v):
        """ Insert a vertex"""
        if v._category=='Recipe':
            self.recipe.add(v)
        self._incident[v]={}
        if self.is_derected()==True:
            self._outgoing[v]={}

    def insert_incident_edge(self,u,v,e=None):
        """ Insert the edge e incident from u to v"""
        if e is None:
            e=Edge(u,v)
        else:
            for it in self._incident[v].values():
                if e in it:
                    print('The edge  to be inserted already existed')
                    return

        # (self._outgoing[u]).update({v: e})  # [v]=e
        # (self._incident[v]).update({u: e})  # [u]=e

        if len(self._outgoing[u]) == 0:
            self._outgoing[u].update({v:[e]})
        else:
            if v in self._outgoing[u]:
                (self._outgoing[u][v]).append(e)
            else:
                (self._outgoing[u][v])=[e]

        if len(self._incident[v]) == 0:
            self._incident[v].update({u:[e]})
        else:
            if u in self._incident[v]:
                (self._incident[v][u]).append(e)
            else:
                self._incident[v][u]=[e]

    def remove_vertex(self,v): # Computational complexity: O(deg(v))
        """ Remove vertex v and all edges connected to it"""
        try:
            if v not in self._incident:
                raise Exception
            if self.is_derected():
                for it in self._incident[v].keys(): # Delete all processes generating this object
                    self._outgoing[it].pop(v)

                self._incident.pop(v)

                for it in self._outgoing[v].keys(): # Delete all processes generating the object next to this object
                    self._incident[it].pop(v)

                self._outgoing.pop(v)

            else:
                for it in self._incident[v].keys():
                    self._incident[it].pop(v)
                self._incident.pop(v)
        except Exception as e:
            print( 'Vertex v is not a member of this graph!')

    def remove_edge(self,u,v,e=None): # Computational complexity: O(1)
        """ Remove the edge e connecting u with v if e is not None;
        Remove all edges connecting u with v if e is None
        """
        try:
            if e is None:   # Remove all edges connecting u with v
                if v in self._incident[u]:
                    self._incident[u].pop(v)
                    self._outgoing[v].pop(u)

                elif v in self._outgoing[u]:
                    self._outgoing[u].pop(v)
                    self._incident[v].pop(u)

                return True

            else:   # Remove the edge e connecting u with v
                for i in range(len(self._outgoing[u][v])):
                    if e is self._outgoing[u][v][i]:
                        (self._outgoing[u][v]).remove(e)
                        return True

                for i in range(len(self._incident[u][v])):
                    if e is self._incident[u][v][i]:
                        (self._incident[u][v]).remove(e)
                        return True

            raise Exception

        except Exception as e:
            print('No edge connecting u with v!')

        return False

    def DFSTraverse(self,u,is_complete=False):
        """ Depth-first search from vertex u.
        Return a dict with visited vertices as keys and their discovering edges as values
        if the argument is_complete is False, the DF-search will only be implemented once from u, thus some vertices may not be visited;
        if the is_complete is True, the DF-search will be implemented until every vertices are visited"""

        # visited_dict acts as a mechanism for recognizing visited vertices, with
        # visited vertices as keys and their discovering edges as values.
        # Newly visited vertices will be added to the dict

        search_path_list = []
        visited_dict = {u: None}

        path1=[u]
        self.DFS(u, visited_dict,path1)
        search_path_list.append(path1)

        if is_complete:
            for vertex in self.vertices():
                if vertex not in visited_dict:
                    path=[vertex]
                    visited_dict[vertex]=None
                    self.DFS(vertex, visited_dict,path)
                    search_path_list.append(path)

        return search_path_list

    def DFS(self,u,visited_dict,path):
        """ Implement DFS of the unvisited portion of graph g starting at vertex u."""
        #print(u)
        for v in self._incident[u].keys():
            if v not in visited_dict:
                path.append(v)
                visited_dict[v]=self._incident[u][v]
                self.DFS(v,visited_dict,path)

    def construct_path(self,head,tail,visited_dict):
        """ """
        path=[]
        if tail in visited_dict:
            path.append(tail)
            cur=tail
            while cur is not head:
                e=visited_dict[cur]
                parent=e.get_opposite(cur)
                path.append(parent)
                cur=parent
            path.reverse()
        return path

    def display_processes(self,v=None):
        """ Given the target recipe v, find all functional units belonging to recipe v.
        This function uses BFS to find all functional units.
        Functional units are the steps needed to accomplish the given target recipe
        """
        if v is None:
            for recipe_vertex in self.recipe:
                print('------------- {} --------------'.format(recipe_vertex._name))
                self.__BFS_find_gradients(recipe_vertex)
        else:
            print('------------- {} --------------'.format(v._name))
            self.__BFS_find_gradients(v)

    def __BFS_find_gradients(self,v):
        level={v}
        while len(level)>0:
            next_level=set()
            for u in level:
                output_name=u._name
                for motion_vertex in self._incident[u].keys():
                    string=''
                    utensil_name=''
                    for input_vertex in self._incident[motion_vertex].keys():
                        if input_vertex._category=='Utensil':
                            utensil_name=input_vertex._name
                        else:
                            string+='{}({}) '.format(input_vertex._name,input_vertex._state[-1])
                            next_level.add(input_vertex)
                    string+='>>> {} {} >>> {}({})\n'.format(motion_vertex._name,utensil_name,output_name,u._state[-1])
                    print(string)
            level=next_level

    def add_process(self,process_list):
        """ Merge new processes(Graph) to current graph.
        param: process_list is a list storing new process. 
        Each process is a small graph which consists of only one outcome , one motion, one input and one utensil
        """
        for process in process_list:
            self.__add_functional_unit(process)

    def add_recipe(self,recipe):
        """ merge a new recipe(Graph) to this graph.
        Firstly, the new recipe is divided into single process units, and then these process
        units will """
        if recipe is self:
            return
        self.__add_functional_unit(recipe)
        self.recipe.clear()
        for v in self.vertices():
            if len(self._outgoing[v])==0:
                self.recipe.add(v)

    # Not available
    def search_in_vertices(self,v,vertices):
        found_vertex=None
        for u in self.vertices():
            if v == u:
                found_vertex = u
                break
        return found_vertex

    def __add_functional_unit(self,fu):

        for v in fu.vertices():
            if v._category=='Motion':  # Insert motion vertex first
                current_vertices = self.vertices()
                motion = copy.deepcopy(v)
                self.insert_vertex(motion)

                for input in fu._incident[v].keys():
                    found_vertex = self.search_in_vertices(input, current_vertices)
                    if found_vertex is None:
                        new_input = copy.deepcopy(input)
                        self.insert_vertex(new_input)
                        self.insert_incident_edge(new_input, motion)
                    else:
                        self.insert_incident_edge(found_vertex, motion)


                for outcome in fu._outgoing[v].keys():
                    found_vertex = self.search_in_vertices(outcome, current_vertices)
                    if found_vertex is None:
                        new_outcome = copy.deepcopy(outcome)
                        self.insert_vertex(new_outcome)
                        self.insert_incident_edge(motion, new_outcome)
                    else:
                        self.insert_incident_edge(motion,found_vertex)

    def BFSTraverse(self,s,visited_dict):
        """ Perform BFS of the unvisited portion of graph g starting at vertex s.
        
        visited_dict is a dict mapping each vertex to the edge that was used to visit it
        (s should be mapped to None prior to the call)
        Newly visited vertices will be added to the dict
        """
        level=[s]
        while len(level)>0:
            next_level=[]  # Prepare to gather newly found vertices
            for u in level:
                for v in self._incident[u].keys():
                    if v not in visited_dict:
                        visited_dict[v]=self._incident[u][v]
                        next_level.append(v)
            level=next_level

    # Minimum spanning tree, not yet completed
    def prim(self,u):
        """ Compute a minimum spanning tree of weighted graph g.
        Return a list of edges that compreise the MST (in arbitrary order)"""
        pass

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
                for process_index in range(len(self._outgoing[start_p][end_p])):
                    temp_edge=self._outgoing[start_p][end_p][process_index]
                    # for motion_index in range(len(temp_edge._motions)):
                        # if start_p._category != 'Motion' and end_p._category != 'Motion':
                        #     seq_string = '{}({}) >>> {} {} >>> {}({})'.format(start_p._name, start_p._state[-1],
                        #                                                            temp_edge._motions[motion_index][1]._name,
                        #                                                            temp_edge._motions[motion_index][0]._name,
                        #                                                            end_p._name, end_p._state[-1])
                        #
                        # elif start_p._category == 'Motion' and end_p._category != 'Motion':
                        #     seq_string = '{} --> {}({})'.format(start_p._name, end_p._name,
                        #                                         end_p._state[-1])
                        # elif start_p._category != 'Motion' and end_p._category == 'Motion':
                        #     seq_string = '{}({}) --> {}'.format(start_p._name, start_p._state[-1],
                        #                                         end_p._name)
                        #
                        # gap = int(width - len(seq_string) // 2)
                        # substring = '| ' + gap * ' ' + seq_string + gap * ' ' + ' |\n'
                        # list_string += substring
                    if start_p._category != 'Motion' and end_p._category != 'Motion':
                        seq_string = '{}({}) >>>>>> {}({})'.format(start_p._name, start_p._state[-1],

                                                                          end_p._name, end_p._state[-1])

                    elif start_p._category == 'Motion' and end_p._category != 'Motion':
                        seq_string = '{} --> {}({})'.format(start_p._name, end_p._name,
                                                            end_p._state[-1])
                    elif start_p._category != 'Motion' and end_p._category == 'Motion':
                        seq_string = '{}({}) --> {}'.format(start_p._name, start_p._state[-1],
                                                            end_p._name)

                    gap = int(width - len(seq_string) // 2)
                    substring = '| ' + gap * ' ' + seq_string + gap * ' ' + ' |\n'
                    list_string += substring



        string+=list_string
        string+='+ ' + '- ' * width + '+' + '\n'

        return string



        string += '+ ' + '- ' * 20 + '+' + '\n'

        return string

knife=Vertex(x=1,name='Knife',state=['Clean'],contents=None,category='Utensil')
blender=Vertex(x=2,name='Blender',state=['Clean'],contents=None,category='Utensil')
apple=Vertex(x=3,name='Apple',state=['Unchopped'],contents=None,category='Fruit')
bowl=Vertex(x=4,name='Bowl',state=['Empty'],contents=None,category='Container')
salad_sauce=Vertex(x=5,name='Salad_sauce',state=['Fluid'],contents=None,category='Seasoning')
salad_sauce_container=Vertex(x=6,name='Salad_sauce_container',state=['Full'],contents=[salad_sauce],category='Seasoning')
salad=Vertex(x=7,name='Salad',state=['Enough'],contents=None,category='Recipe')
hand=Vertex(x=8,name='Hand',state=['Clean'],contents=None,category='Utensil')

cut=Vertex(x=1,name='Cut with',category='Motion')
blend=Vertex(x=2,name='Blend with',category='Motion')
squeeze=Vertex(x=3,name='Squeeze with',category='Motion')
pick_and_place=Vertex(x=4,name='Pick_and_place in/with',category='Motion')
pick_and_place1=Vertex(x=4,name='Pick_and_place in/with',category='Motion')
pick_and_place2=Vertex(x=4,name='Pick_and_place in/with',category='Motion')
dirty_knife=Vertex(x=1,name='Knife',state=['Clean','Dirty'],contents=None,category='Utensil')
chopped_apple=Vertex(x=2,name='Apple',state=['Unchopped','Chopped'],contents=None,category='Fruit')
bowl_apple=Vertex(x=3,name='Bowl',state=['Non-empty'],contents=[chopped_apple],category='MotionResult')
bowl_apple_salad=Vertex(x=4,name='Bowl',state=['Non-empty'],contents=[chopped_apple,salad],category='MotionResult')



# g=Graph(directed=True)
#
# g.insert_vertex(apple)
# g.insert_vertex(knife)
# g.insert_vertex(cut)
# g.insert_vertex(squeeze)
# g.insert_vertex(chopped_apple)
# g.insert_vertex(salad_sauce_container)
# g.insert_vertex(salad_sauce)
# g.insert_vertex(salad)
# g.insert_vertex(bowl)
# g.insert_vertex(pick_and_place)
# g.insert_vertex(hand)
#
#
# g.insert_incident_edge(apple,cut)
# g.insert_incident_edge(knife,cut)
# g.insert_incident_edge(cut,chopped_apple)
#
# g.insert_incident_edge(hand,squeeze)
# g.insert_incident_edge(salad_sauce_container,squeeze)
# g.insert_incident_edge(hand,squeeze)
# g.insert_incident_edge(squeeze,salad_sauce)
#
# g.insert_incident_edge(chopped_apple,pick_and_place)
# g.insert_incident_edge(salad_sauce,pick_and_place)
# g.insert_incident_edge(bowl,pick_and_place)
# g.insert_incident_edge(pick_and_place,salad)
#
#
# g.display_processes(salad)
g1=Graph(directed=True)
g2=Graph(directed=True)

g1.insert_vertex(apple)
g1.insert_vertex(knife)
g1.insert_vertex(cut)
g1.insert_vertex(chopped_apple)
g1.insert_vertex(salad_sauce)
g1.insert_vertex(bowl)
g1.insert_vertex(pick_and_place)
g1.insert_vertex(hand)
g1.insert_vertex(salad)

g2.insert_vertex(salad_sauce_container)
g2.insert_vertex(salad_sauce)
g2.insert_vertex(squeeze)
g2.insert_vertex(hand)


g1.insert_incident_edge(apple,cut)
g1.insert_incident_edge(knife,cut)
g1.insert_incident_edge(cut,chopped_apple)
g1.insert_incident_edge(chopped_apple,pick_and_place)
g1.insert_incident_edge(salad_sauce,pick_and_place)
g1.insert_incident_edge(bowl,pick_and_place)
g1.insert_incident_edge(pick_and_place,salad)
g1.insert_incident_edge(hand,pick_and_place)
g1.recipe.add(salad)

g2.insert_incident_edge(hand,squeeze)
g2.insert_incident_edge(salad_sauce_container,squeeze)
g2.insert_incident_edge(squeeze,salad_sauce)
g2.recipe.add(salad_sauce)

g1.display_processes()
g2.display_processes()
#g2.add_recipe(g1)
g1.add_recipe(g2)
#
# f=Vertex()
# for it in g1.vertices():
#     if it._name=='Salad':
#         f=it
#         break
#
g1.display_processes()
print(g1)
#print(salad)





















