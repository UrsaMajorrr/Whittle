"""
OpenFOAM dictionary file templates
"""

def create_blockmesh_dict(dimensions: dict, cells_per_dim: dict) -> str:
    """
    Create a blockMeshDict file content for a simple box mesh
    """
    # Extract dimensions
    x_min, x_max = dimensions['x_min'], dimensions['x_max']
    y_min, y_max = dimensions['y_min'], dimensions['y_max']
    z_min, z_max = dimensions['z_min'], dimensions['z_max']
    
    # Extract cell counts
    nx, ny, nz = cells_per_dim['x'], cells_per_dim['y'], cells_per_dim['z']
    
    return f"""/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2312                                 |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

scale 1;

vertices
(
    ({x_min} {y_min} {z_min})  // vertex 0
    ({x_max} {y_min} {z_min})  // vertex 1
    ({x_max} {y_max} {z_min})  // vertex 2
    ({x_min} {y_max} {z_min})  // vertex 3
    ({x_min} {y_min} {z_max})  // vertex 4
    ({x_max} {y_min} {z_max})  // vertex 5
    ({x_max} {y_max} {z_max})  // vertex 6
    ({x_min} {y_max} {z_max})  // vertex 7
);

blocks
(
    hex (0 1 2 3 4 5 6 7)
    ({nx} {ny} {nz})
    simpleGrading (1 1 1)
);

boundary
(
    minX
    {{
        type patch;
        faces
        (
            (0 4 7 3)
        );
    }}
    maxX
    {{
        type patch;
        faces
        (
            (1 2 6 5)
        );
    }}
    minY
    {{
        type patch;
        faces
        (
            (0 1 5 4)
        );
    }}
    maxY
    {{
        type patch;
        faces
        (
            (3 7 6 2)
        );
    }}
    minZ
    {{
        type patch;
        faces
        (
            (0 3 2 1)
        );
    }}
    maxZ
    {{
        type patch;
        faces
        (
            (4 5 6 7)
        );
    }}
);

// ************************************************************************* //"""

def create_snappyhexmesh_dict(stl_name: str, n_layers: int = 3) -> str:
    """
    Create a snappyHexMeshDict file content
    """
    return f"""/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2312                                 |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      snappyHexMeshDict;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

castellatedMesh true;
snap            true;
addLayers       true;

geometry
{{
    {stl_name}
    {{
        type triSurfaceMesh;
        file "{stl_name}.stl";
    }}
}};

castellatedMeshControls
{{
    maxLocalCells 100000;
    maxGlobalCells 2000000;
    minRefinementCells 0;
    maxLoadUnbalance 0.10;
    nCellsBetweenLevels 3;
    features
    (
        {{
            file "{stl_name}.eMesh";
            level 0;
        }}
    );
    refinementSurfaces
    {{
        {stl_name}
        {{
            level (0 0);
        }}
    }}
    resolveFeatureAngle 30;
    refinementRegions
    {{
    }}
    locationInMesh (0 0 0);
    allowFreeStandingZoneFaces true;
}};

snapControls
{{
    nSmoothPatch 3;
    tolerance 2.0;
    nSolveIter 30;
    nRelaxIter 5;
}};

addLayersControls
{{
    relativeSizes true;
    layers
    {{
        {stl_name}
        {{
            nSurfaceLayers {n_layers};
        }}
    }}
    expansionRatio 1.2;
    finalLayerThickness 0.3;
    minThickness 0.1;
    nGrow 0;
    featureAngle 60;
    slipFeatureAngle 30;
    nRelaxIter 3;
    nSmoothSurfaceNormals 1;
    nSmoothNormals 3;
    nSmoothThickness 10;
    maxFaceThicknessRatio 0.5;
    maxThicknessToMedialRatio 0.3;
    minMedialAxisAngle 90;
    nBufferCellsNoExtrude 0;
    nLayerIter 50;
}};

meshQualityControls
{{
    maxNonOrtho 65;
    maxBoundarySkewness 20;
    maxInternalSkewness 4;
    maxConcave 80;
    minVol 1e-13;
    minTetQuality 1e-15;
    minArea -1;
    minTwist 0.02;
    minDeterminant 0.001;
    minFaceWeight 0.05;
    minVolRatio 0.01;
    minTriangleTwist -1;
    nSmoothScale 4;
    errorReduction 0.75;
}};

// ************************************************************************* //""" 