from geom import *

arb_capacity = 1000000

cur_flow_id = 0

class sink:
  def __init__(self):
    pass
  def add_stress(self, d, amt):
    pass
  def get_stress_on(self, d):
    """normal <--> sink: only the normal counts the stress"""
    return 0
  
  def fff_dfs(self, safety_factor, flow_id, backwards, breaking): #breaking is forbidden
    return fff_dfs_report() #we've reached the end
  
  def set_adj(self, d, val):
   pass

broken_nodes = []

class node:
  def __init__(self, adj, mass):
    self.adj = adj

    self.stress_on = [0 for i in way.all] #positive if we are learning on it.
                                          #negative if it is leaning on us.
    extra_stress = 0

    #invariant: self.stress_on sums to self.mass
    for d in way.all:
      if adj[d] == None:
        continue
      adj[d].set_adj(way.opposite(d), self)
      
      #if we were virtual and are being realized, we need to reflow,
      #since we're not a sink anymore.
      extra_stress += adj[d].get_stress_on(way.opposite(d))
      #actually, this number could be negative under obscure, stupid circumstances.
    
    self.flow_id_visited = -1
    self.fff(extra_stress + mass)

  def cut_links(self):
    for d in way.all:
      if self.adj[d] == None:
        continue
      self.adj[d].set_adj(way.opposite(d), None)
    #now we've got stress flowing through non-existent links

    for d in way.all:
      if self.adj[d] == None:
        continue
      #if we're putting weight on it, we relieve the weight.
      #if we're carrying weight from it, it needs to find a new outlet
      if self.stress_on[d] != 0:
        self.adj[d].fff(-self.get_stress_on(d))

    for d in way.all:
      self.adj[d] = None

  def add_stress(self, d, amount):
    import gfx
    self.stress_on[d] += amount
    
    if amount > 0 and self.capacity_towards(d, 2) < 0:
      print "warning: stress bottleneck!  This block is bearing",
      print  self.stress_on[d], " out of a maximum of ",
      print  self.capacity_towards(d, 1) + self.stress_on[d]
      #hack for debugging  
    if self.capacity_towards(d, 4.0) < 0:
      self.image = gfx.block_s1 ; self.repaint()
    if self.capacity_towards(d, 2.0) < 0:
      self.image = gfx.block_s2 ; self.repaint()
    if self.capacity_towards(d, 1.5) < 0:
      self.image = gfx.block_s3 ; self.repaint()


  def get_stress_on(self, d):
    return self.stress_on[d]

  def set_adj(self, d, val):
    self.adj[d] = val

  def fff(self, amount):
    """Flow Ford-Fulkerson.  Attempt to flow _amount_ through the
    graph, trying to respect _safety_factor_.  If _amount_ is
    negative, it removes stress, which is surprisingly like adding it.
    Invariant: the graph is always a correct flowing of all the
    non-virtual blocks into virtual ones."""
    global cur_flow_id
    
    backwards = amount < 0
    remaining = abs(amount)

    while remaining > 0:
      cur_flow_id += 1
      result = self.fff_bfs(2.0, cur_flow_id, backwards)
      if result == None:
        break #can't fit in the safety margin
      iter_amount = min(result.neck, remaining)
      print "found a route with", result.neck, "applying", iter_amount

      result.apply_stress(iter_amount, backwards)
      remaining -= iter_amount

    #try again, exceeding the safety margin this time
    while remaining > 0:
      cur_flow_id += 1
      result = self.fff_bfs(1, cur_flow_id, backwards)
      if result == None: #dvpns315
        print "Boom!" #can't fit.  Time to destroy!
        break
      iter_amount = min(result.neck, remaining)
      print "found a route with", result.neck, "applying", iter_amount

      result.apply_stress(iter_amount, backwards)
      remaining -= iter_amount

  def fff_bfs(self, safety_factor, flow_id, backwards, breaking=False):
    import Queue
    q = Queue.PriorityQueue(0)

    class bfs_path:
      def __init__(self, car, d, cdr, cap):
        self.car = car; self.d = d; self.cdr = cdr
        if cdr != None:
          self.dist = cdr.dist + 1
          self.neck = min(cdr.neck, cap)
        else:
          self.dist = 0; self.neck = cap
          
      def apply_stress(self, amount, backwards):
        if self.cdr != None:
          self.car.    add_stress(way.opposite(self.d),  -amount if not backwards
                                                         else amount)
          self.cdr.car.add_stress(self.d              ,  amount if not backwards
                                                         else -amount)
          self.cdr.apply_stress(amount, backwards)

          
    q.put((0, bfs_path(self, None, None, arb_capacity)))

    while not q.empty():
      cost, path = q.get()
      cur = path.car

      for d in way.flow_ordered_bias:
        other = cur.adj[d]
        if other == None or (isinstance(other, node) #sinks are always good
                             and other.flow_id_visited == cur_flow_id):
          continue

        if isinstance(other, sink):
          return bfs_path(other, d, path, arb_capacity) #Done!

        other.flow_id_visited = flow_id

        if backwards:
          cap = other.capacity_towards(way.opposite(d), safety_factor)
        else:
          cap = cur.capacity_towards(d, safety_factor)
        if cap <= 0:
          continue
        new_node = bfs_path(other, d, path, cap)
        q.put((new_node.dist/new_node.neck, new_node))
    
    return None
