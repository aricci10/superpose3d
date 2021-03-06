[![Build Status](https://travis-ci.org/jewettaij/superpose3d.svg?branch=master)](./.travis.yml)
[![GitHub](https://img.shields.io/github/license/jewettaij/superpose3d)](./LICENSE.md)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/superpose3d)](https://pypistats.org/packages/superpose3d)
[![PyPI - Version](https://img.shields.io/pypi/v/superpose3d)](https://pypi.org/project/superpose3d/)
[![python-versions](https://img.shields.io/pypi/pyversions/superpose3d.svg)](https://pypi.org/project/superpose3d/)
[![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/jewettaij/superpose3d)]()



superpose3d
===========

Note: There is a ***C++ version*** of this repository
[***here***](https://github.com/jewettaij/superpose3d_cpp).

##  Usage

```python
def Superpose3D(X,    # <-- Nx3 array of coords for the "frozen" point cloud
                x,    # <-- Nx3 array of coords for the "mobile" point cloud
                # ---- optional arguments: ----
                w = None,        # optional weights for the calculation of RMSD
                allow_rescale=False,   # attempt to rescale mobile point cloud?
                report_quaternion=False)      # report rotation angle and axis?
```

Superpose3D() takes two ordered lists (or numpy arrays) of xyz coordinates
(*of the same length*, **N**) representing points in a point cloud (**X** and
**x**). Treating them as rigid objects, "Superpose3D()" attempts to superimpose
them using **rotations**, **translations**, and (optionally) **scale**
transformations in order to minimize the root-mean-squared-distance (RMSD)
between corresponding points from either point cloud, where RMSD is defined as:

<img src="http://latex.codecogs.com/gif.latex?\large&space;RMSD=\sqrt{\,\frac{1}{N}\,\sum_{n=1}^N\,\,\sum_{i=1}^3 \left|X_{ni}-\left(\sum_{j=1}^3 cR_{ij}x_{nj}+T_i\right)\right|^2}"/>

...where:
```
   R_ij = a rotation matrix    (a 3x3 numpy array representing the rotation. |R|=1)
   T_j  = a translation vector (a 1-D numpy array containing x,y,z displacements)
    c   = a scalar             (a number. optional. 1 by default)
```
This function returns a 4-tuple containing the optimal values of:
```
   (RMSD, R, T, c)
```

### Rotation angles, axes, and quaternions
If the rotation angle and axis are needed, then set the *report_quaternion*
argument to *True*. In that case, the function will return this 4-tuple instead:
```
   (RMSD, q, T, c)
```
...where *q* is a numpy array of size 4.  The first element of *q* will store
*cos(θ/2)* (where *θ* is the rotation angle).  The remaining 3 elements of *q*
form a vector (of length *sin(θ/2)*), pointing along the axis of rotation.
Equivalently, *q* is the
[quaternion corresponding to rotation *R*](https://en.wikipedia.org/wiki/Quaternions_and_spatial_rotation).

### Weighted RMSD
A weighted version of the RMSD minimization algorithm is also available
if the caller supplies an extra argument specifying the weight of every
point in the cloud (*w<sub>n</sub>*).  In that case, RMSD is defined as:
<img src="http://latex.codecogs.com/gif.latex?\large&space;RMSD=\sqrt\left\sum_{n=1}^N\,w_n\,\sum_{i=1}^3 \left|X_{ni}-\left(\sum_{j=1}^3 c R_{ij}x_{nj}+T_i\right)\right|^2\quad\middle/\quad\sum_{n=1}^N w_n}\right}"/>

### Scale transformations
This function implements a more general variant of the method from this paper:
R. Diamond, (1988)
"A Note on the Rotational Superposition Problem",
 Acta Cryst. A44, pp. 211-216.

This version has been augmented slightly to support scale transformations.  (I.E. multiplication by scalars.  This can be useful for the registration of two different annotated volumetric 3-D images of the same object taken at different magnifications.)

Note that if you enable scale transformations (i.e. if *allow_rescale=True*), you should be wary if the function returns a negative **c** value.  Negative **c** values correspond to inversions (reflections).  For this reason, if you are using this function to compare the conformations of molecules, you should probably set *allow_rescale=False*.  This will prevent matching a molecule with its stereoisomer.

## Installation using pip

    pip install .
    pip install -r requirements.txt

Later, you can uninstall superpose3d using:

    pip uninstall superpose3d

## Requirements

superpose3d depends on numpy

## License

superpose3d is available under the terms of the [MIT license](LICENSE.md).
