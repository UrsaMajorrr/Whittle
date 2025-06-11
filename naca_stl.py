import numpy as np
from stl import mesh

# NACA 0012 coordinates (symmetric airfoil, 2D)
# You can get higher resolution or more accurate data from airfoiltools.com or generate programmatically
x = np.linspace(0, 1, 100)
yt = 0.12 / 0.2 * (0.2969*np.sqrt(x) - 0.1260*x - 0.3516*x**2 + 0.2843*x**3 - 0.1015*x**4)

xu = x
yu = yt
xl = x
yl = -yt

# Stack upper and lower surfaces
X = np.concatenate([xu, xl[::-1]])
Y = np.concatenate([yu, yl[::-1]])
Z = np.zeros_like(X)

# Make it a thin extrusion (3D)
thickness = 0.01
Z1 = np.zeros_like(Z)
Z2 = np.ones_like(Z) * thickness

vertices = np.array([[x, y, z] for x, y, z in zip(X, Y, Z1)] + [[x, y, z] for x, y, z in zip(X, Y, Z2)])
faces = []

# Create triangular faces (simplified — refine for real use)
for i in range(len(X) - 1):
    faces.append([i, i+1, i+len(X)])
    faces.append([i+1, i+len(X)+1, i+len(X)])

faces = np.array(faces)

# Create mesh
airfoil = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
for i, f in enumerate(faces):
    for j in range(3):
        airfoil.vectors[i][j] = vertices[f[j], :]

# Save STL
airfoil.save('naca0012.stl')
