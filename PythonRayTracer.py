import numpy as np
import matplotlib.pyplot as plt

def normalize(vector):
  return vector / np.linalg.norm(vector)

def reflected(vector, axis):
  return vector - 2 * np.dot(vector, axis) * axis
  def sphere_intersect(center, radius, ray_origin, ray_direction):
  b = 2 * np.dot(ray_direction, ray_origin - center)
  c = np.linalg.norm(ray_origin - center) ** 2 - radius ** 2
  delta = b ** 2 - 4 * c
  if delta > 0:
    t1 = (-b + np.sqrt(delta)) / 2
    t2 = (-b - np.sqrt(delta)) / 2
    if t1 > 0 and t2 > 0:
      return min(t1, t2)
  return None

def nearest_intersected_object(objects, ray_origin, ray_direction):
  distances = [sphere_intersect(obj['center'], obj['radius'], ray_origin, ray_direction) for obj in objects]
  nearest_object = None
  min_distance = np.inf
  
  for index, distance in enumerate(distances):
    if distance and distance < min_distance:
      min_distance = distance
      nearest_object = objects[index]
  return nearest_object, min_distance

width = 400
height = 300
max_depth = 3

camera = np.array([0, 1, 5]) # Position camera further away to view the entire scene
ratio = float(width) / height
screen = (-1, 1 / ratio, 1, -1 / ratio) # left, top, right, bottom

light = {
  'position': np.array([5, 5, 5]),
  'ambient': np.array([1, 1, 1]),
  'diffuse': np.array([1, 1, 1]),
  'specular': np.array([1, 1, 1]) }

objects = [
  { 'center': np.array([0, -9000, 0]), 'radius': 9000 - 0.7, 'ambient':
  np.array([0.1, 0.1, 0.1]), 'diffuse': np.array([0.6, 0.6, 0.6]), 'specular':
  np.array([1, 1, 1]), 'shininess': 100, 'reflection': 0.5 }]

radius = 0.1 # Size of each sphere

# Colors for the A shape
colors = np.array([1, 0, 0]) # Red for A

#A didnt work so there is no A... :'( Wanted to do initials but its hard
# Define the A shape along the diagonal
A_positions = [
  [0, 0, 0], [1, 0, 0], [0.5, 0.5, 0], # Base of A
  [0, 0, 0.5], [1, 0, 0.5], [0.5, 0.5, 0.5], # Crossbar of A
  [0.5, 0, 0.25], [0.5, 0.5, 0.25] # Diagonal lines of A
]

for pos in A_positions:
  objects.append({
    'center': np.array(pos),
    'radius': radius,
    'ambient': colors * 0.1,
    'diffuse': colors, # Red
    'specular': np.array([1, 1, 1]),
    'shininess': 100,
    'reflection': 0.3
  })

# Colors for each axis
colors = [
    np.array([1, 0, 0]), # Red for X-axis
    np.array([0, 1, 0]), # Green for Y-axis
    np.array([0, 0, 1]), # Blue for Z-axis
  ]

# Spheres along the X-axis (red)
for i, x in enumerate(np.linspace(-1, 1, 10)): # Adjust number of spheres for each axis
  objects.append({
    'center': np.array([x, 0, 0]), # Position on the X-axis
    'radius': radius,
    'ambient': colors[0] * 0.1,
    'diffuse': colors[0],
    'specular': np.array([1, 1, 1]),
    'shininess': 100,
    'reflection': 0.3
  })

# Spheres along the Y-axis (green)
for i, y in enumerate(np.linspace(-1, 1, 10)): # Adjust number of spheres for each axis
  objects.append({
    'center': np.array([0, y, 0]), # Position on the Y-axis
    'radius': radius,
    'ambient': colors[1] * 0.1,
    'diffuse': colors[1],
    'specular': np.array([1, 1, 1]),
    'shininess': 100,
    'reflection': 0.3
    })

# Spheres along the Z-axis (blue)
for i, z in enumerate(np.linspace(-1, 1, 10)): # Adjust number of spheres for each axis
  objects.append({
    'center': np.array([0, 0, z]), # Position on the Z-axis
    'radius': radius,
    'ambient': colors[2] * 0.1,
    'diffuse': colors[2],
    'specular': np.array([1, 1, 1]),
    'shininess': 100,
    'reflection': 0.3
  })

# Add a large floor to ensure it's visible
floor = {
  'center': np.array([0, -1.5, 0]),
  'radius': 10,
  'ambient': np.array([0.2, 0.2, 0.2]),
  'diffuse': np.array([0.5, 0.5, 0.5]),
  'specular': np.array([1, 1, 1]),
  'shininess': 50,
  'reflection': 0.3
}

objects.append(floor)

image = np.zeros((height, width, 3))
for i, y in enumerate(np.linspace(screen[1], screen[3], height)):
  for j, x in enumerate(np.linspace(screen[0], screen[2], width)):
    # screen is on origin
    pixel = np.array([x, y, 0])
    origin = camera
    direction = normalize(pixel - origin)
    
    color = np.zeros((3))
    reflection = 1
  
    for k in range(max_depth):
      # check for intersections
      nearest_object, min_distance = nearest_intersected_object(objects, origin, direction)
      if nearest_object is None:
        break
      
      intersection = origin + min_distance * direction
      normal_to_surface = normalize(intersection - nearest_object['center'])
      shifted_point = intersection + 1e-5 * normal_to_surface
      intersection_to_light = normalize(light['position'] - shifted_point)
      _, min_distance = nearest_intersected_object(objects, shifted_point, intersection_to_light)
      intersection_to_light_distance = np.linalg.norm(light['position'] - intersection)
      is_shadowed = min_distance < intersection_to_light_distance
      if is_shadowed:
        break

      illumination = np.zeros((3))
      
      # ambiant
      illumination += nearest_object['ambient'] * light['ambient']
      
      # diffuse
      illumination += nearest_object['diffuse'] * light['diffuse'] * np.dot(intersection_to_light, normal_to_surface)
      
      # specular
      intersection_to_camera = normalize(camera - intersection)
      H = normalize(intersection_to_light + intersection_to_camera)
      illumination += nearest_object['specular'] * light['specular'] * np.dot(normal_to_surface, H) ** (nearest_object['shininess'] / 4)
      
      # reflection
      color += reflection * illumination
      reflection *= nearest_object['reflection']

      origin = shifted_point
      direction = reflected(direction, normal_to_surface)

    image[i, j] = np.clip(color, 0, 1)
  print("%d/%d" % (i + 1, height)) 

plt.imsave('image.png', image)
plt.imshow(image)
plt.show()
