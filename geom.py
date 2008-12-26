class way:
  (up, down, north, south, east, west) = range(6)
  all = [up, down, north, south, east, west]
  vert = [up, down]
  horiz = [north, south, east, west]
  ns = [north, south]
  ew = [east, west]

  @staticmethod
  def opposite(d):
    return [1, 0, 3, 2, 5, 4][d]
  #[down, up, south, north, west, east][d]

  @staticmethod
  def rel(d, (x, y, z)): #could be faster
    return [ (x, y, z+1), #up
             (x, y, z-1), #down
             (x, y+1, z), #north
             (x, y-1, z), #south
             (x+1, y, z), #east
             (x-1, y, z)  #west
             ][d]

  #flow_ordered_bias = [1, 0, 4, 5, 2, 3]
  #[down, up, east, west, north, south]

  flow_ordered_bias = [1, 4, 2, 5, 3, 0]
  #[down, east, north, west, south, up]
