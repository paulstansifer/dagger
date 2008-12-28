from geom import *

inf = float('inf')

flow_id = 0

class network_node:
  def cut_links(self):
    for d in way.all:
      if self.adj[d] == None:
        continue
      self.adj[d].adj[way.opposite(d)] = None
    #now we've got stress flowing through non-existent links

    for d in way.all:
      if self.adj[d] == None:
        continue
      #if we're putting weight on it, we relieve the weight.
      #if we're carrying weight from it, it needs to find a new outlet
      stress = self.stress_on[d]
      if stress != 0:
        self.adj[d].stress_on[way.opposite(d)] = 0
        self.adj[d].fff(-stress)

    for d in way.all:
      self.adj[d] = None


class sink(network_node):
  def fff_dfs(self, safety_factor, flow_id, backwards, breaking): #breaking is forbidden
    return fff_dfs_report() #we've reached the end

  def add_stress(self, d, amount):
    pass

  def fff(self, amount):
    pass

  #sinks have no capacity limit in distributing stress
  def capacity_towards(self, d, safety_factor):
    return inf
  
broken_nodes = []

class node(network_node):
  def __init__(self, adj, mass):
    self.adj = adj
    self.stress_on = [0 for i in way.all] #positive if we are learning on it.
                                          #negative if it is leaning on us.
    extra_stress = 0

    #invariant: self.stress_on sums to self.mass
    for d in way.all:
      if adj[d] == None:
        continue
      adj[d].adj[way.opposite(d)] = self
      
      #if we were virtual and are being realized, we need to reflow,
      #since we're not a sink anymore.
      extra_stress += adj[d].stress_on[way.opposite(d)]
    
    self.flow_id_visited = -1
    self.fff(extra_stress + mass)

  def add_stress(self, d, amount):
    import gfx
    self.stress_on[d] += amount
    
    if amount > 0 and self.capacity_towards(d, 2) < 0:
      print "warning: stress bottleneck!  This block is bearing",
      print  self.stress_on[d], " out of a maximum of ",
      print  self.capacity_towards(d, 1) + self.stress_on[d]
      
    #hacks for debugging  
    if self.capacity_towards(d, 4.0) < 0:
      self.image = gfx.block_s1 ; self.repaint()
    if self.capacity_towards(d, 2.0) < 0:
      self.image = gfx.block_s2 ; self.repaint()
    if self.capacity_towards(d, 1.5) < 0:
      self.image = gfx.block_s3 ; self.repaint()

    #if isinstance(self.adj[d], sink):
    #  self.adj[d].image = gfx.seltop; self.adj[d].repaint()

  def fff(self, amount):
    """Flow Ford-Fulkerson.  Attempt to flow _amount_ through the
    graph, trying to respect _safety_factor_.  If _amount_ is
    negative, it removes stress, which is surprisingly like adding it.
    Invariant: the graph is always a correct flowing of all the
    non-virtual blocks into virtual ones."""
    backwards = amount < 0
    remaining = abs(amount)

    while remaining > 0:
      result = self.fff_bfs(2.0, backwards)
      if result == None:
        break #can't fit in the safety margin
      iter_amount = min(result.neck, remaining)

      result.apply_stress(iter_amount, backwards)
      remaining -= iter_amount

    #try again, exceeding the safety margin this time
    while remaining > 0:
      result = self.fff_bfs(1, backwards)
      if result == None: #dvpns315
        self.fff_bfs(1, backwards, breaking=True)
        print "Boom!" #can't fit.  Time to destroy!
        break
      iter_amount = min(result.neck, remaining)

      result.apply_stress(iter_amount, backwards)
      remaining -= iter_amount

    print "net stress", sum(self.stress_on)

  def fff_bfs(self, safety_factor, backwards, breaking=False):
    global flow_id
    import Queue
    frontier = Queue.PriorityQueue(0)
    #ret_options = Queue.PriorityQueue(0)
    return_timeout = 2 #number of rounds to find a better route
    best_ret_option = (inf, None) #we can use this to guarantee finding the
                           #best path by only bailing out when we know
                           #all intermediate states are worse than the
                           #current path, but it could get quite
                           #expensive.

    flow_id += 1

    class bfs_path:
      def __init__(self, car, step_d, cdr, cap):
        self.car = car; self.step_d = step_d; self.cdr = cdr
        if cdr != None:
          self.dist = cdr.dist + 1
          self.neck = min(cdr.neck, cap)
        else:
          self.dist = 0; self.neck = cap
          
      def apply_stress(self, amount, backwards):
        if self.cdr != None:
          self.car.    add_stress(way.opposite(self.step_d),
                                  -amount if not backwards else amount)
          self.cdr.car.add_stress(self.step_d              ,
                                  amount if not backwards else -amount)
          self.cdr.apply_stress(amount, backwards)

          
    frontier.put((0, bfs_path(self, None, None, inf)))
    self.flow_id_visited = flow_id

    while not frontier.empty():
      cost, path = frontier.get()
      cur = path.car

      for d in way.flow_ordered_bias:
        other = cur.adj[d]
        if other == None or (isinstance(other, node) #sinks are always good
                             and other.flow_id_visited == flow_id):
          continue

        other.flow_id_visited = flow_id

        if backwards:
          cap = other.capacity_towards(way.opposite(d), safety_factor)
        else:
          cap = cur.capacity_towards(d, safety_factor)

        if cap <= 0:
          continue
        new_node = bfs_path(other, d, path, cap)
        cost = new_node.dist/new_node.neck
        frontier.put((cost, new_node))

        if isinstance(other, sink):
          #don't return yet; maybe another direction will reveal a
          #better path.
          (best_cost, best_path) = best_ret_option
          if cost < best_cost:
            best_ret_option = (cost, new_node)
          #ret_options.put((cost, new_node))

        
        if breaking:
          broken_nodes.append(cur)
      #gone through all directions.

      (cost, path) = best_ret_option
      if cost < inf:
        return_timeout -= 1
        if return_timeout == 0:
          return path #done!

      #(best_cost, best_path) = best_ret_option
      #(pending_cost, pending_path) = frontier.get()
      #if best_cost <= pending_cost: #there's no possible better path
      #  return best_path
      #else:
      #  frontier.put((pending_cost, pending_path))
      
    
    return None
