# -*- coding: utf-8 -*-

import numpy as np
from numpy import linalg as LA
from scipy.spatial.transform import Rotation as R

def Superpose3D(aaXf_orig,   # <-- coordinates for the "frozen" object
                aaXm_orig,   # <-- coordinates for the "mobile" object
                # ---- optional arguments: ----
                aWeights=None,   # optional weights for the calculation of RMSD
                allow_rescale=False,   # attempt to rescale mobile point cloud?
                report_quaternion=False):     # report rotation angle and axis?
    """
    Superpose3D() takes two lists of xyz coordinates, (of the same length)
    and attempts to superimpose them using rotations, translations, and 
    (optionally) rescale operations in order to minimize the 
    root-mean-squared-distance (RMSD) between them.  
    These operations should be applied to the "aaXm_orig" argument.
    This function returns a tuple containing:
      (RMSD, optimal_translation, optimal_rotation, and optimal_scale_factor)
    This function implements a more general variant of the method from:
    R. Diamond, (1988)
    "A Note on the Rotational Superposition Problem", 
    Acta Cryst. A44, pp. 211-216
    This version has been augmented slightly.  The version in the original 
    paper only considers rotation and translation and does not allow the 
    coordinates of either object to be rescaled (multiplication by a scalar).

    (Additional documentation can be found at
     https://pypi.org/project/superpose3d/ )

    """

    #convert input lists as to numpy arrays

    aaXf_orig = np.array(aaXf_orig)
    aaXm_orig = np.array(aaXm_orig)


    #Assert should be used only for debugging.

    if aaXf_orig.shape[0] != aaXm_orig.shape[0]:
        raise ValueError ("Inputs should have the same size.")

    #convert weights into array
    N = aaXf_orig.shape[0]
    if (aWeights == None) or (len(aWeights) == 0):
        aWeights = np.full((N,1),1.0)
    else:
        #reshape so multiplications are done column-wise
        aWeights = np.array(aWeights).reshape(N,1)

    # Find the center of mass of each object:
    """
    aCenter_f = np.zeros(3)
    aCenter_m = np.zeros(3)
    sum_weights = 0.0
    """

    aCenter_f = np.sum(aaXf_orig * aWeights, axis=0)
    aCenter_m = np.sum(aaXm_orig * aWeights, axis=0)
    sum_weights = np.sum(aWeights, axis=0)

    """ 
    for n in range(0, N):
        for d in range(0, 3):
            aCenter_f[d] += aaXf_orig[n][d]*aWeights[n]
            aCenter_m[d] += aaXm_orig[n][d]*aWeights[n]
        sum_weights += aWeights[n]
    """

    if sum_weights != 0:
        aCenter_f /= sum_weights
        aCenter_m /= sum_weights
    """     
    if sum_weights != 0:
        for d in range(0, 3):
            aCenter_f[d] /= sum_weights
            aCenter_m[d] /= sum_weights
    """
    # Subtract the centers-of-mass from the original coordinates for each object
    aaXf = aaXf_orig-aCenter_f
    aaXm = aaXm_orig-aCenter_m

    """
    for n in range(0, N):
        for d in range(0, 3):
            aaXf[n][d] = aaXf_orig[n][d] - aCenter_f[d]
            aaXm[n][d] = aaXm_orig[n][d] - aCenter_m[d]
    """

    # Calculate the "M" array from the Diamond paper (equation 16)

    """
    M = np.zeros((3,3))
    for n in range(0, N):
        for i in range(0, 3):
            for j in range(0, 3):
                M[i][j] += aWeights[n] * aaXm[n][i] * aaXf[n][j]
    """

    M = aaXm.T @ (aaXf * aWeights)

    Q = M + M.T - 2*np.eye(3)*np.trace(M)

    # Calculate Q (equation 17)

    """
    traceM = 0.0
    for i in range(0, 3):
        traceM += M[i][i]

    Q = np.empty((3,3))
    for i in range(0, 3):
        for j in range(0, 3):
            Q[i][j] = M[i][j] + M[j][i]
            if i==j:
                Q[i][j] -= 2.0 * traceM
    """

    # Calculate V (equation 18)
    V = np.empty(3)
    V[0] = M[1][2] - M[2][1];
    V[1] = M[2][0] - M[0][2];
    V[2] = M[0][1] - M[1][0];

    # Calculate "P" (equation 22)

    """
    P = np.empty((4,4))
    for i in range(0,3):
        for j in range(0,3):
            P[i][j] = Q[i][j]
    P[0][3] = V[0]
    P[3][0] = V[0]
    P[1][3] = V[1]
    P[3][1] = V[1]
    P[2][3] = V[2]
    P[3][2] = V[2]
    P[3][3] = 0.0
    """
    P = np.zeros((4,4))
    P[:3, :3] = Q
    P[3, :3] = V
    P[:3, 3] = V


    # The vector "p" contains the optimal rotation (backwards quaternion format)
    p = np.zeros(4)
    p[3] = 1.0           # p = [0,0,0,1]    default value
    pPp = 0.0            # = p^T * P * p    (zero by default)
    singular = (N < 2)   # (it doesn't make sense to rotate a single point)

    try:
        #http://docs.scipy.org/doc/numpy/reference/generated/numpy.linalg.eigh.html
        aEigenvals, aaEigenvects = LA.eigh(P)

    except LinAlgError:
        singular = True  # (I have never seen this happen.)

    if (not singular):  # (don't crash if the caller supplies nonsensical input)

        i_eval_max = np.argmax(aEigenvals)
        pPp = np.max(aEigenvals)
        """
        eval_max = aEigenvals[0]
        i_eval_max = 0
        for i in range(1, 4):
            if aEigenvals[i] > eval_max:
                eval_max = aEigenvals[i]
                i_eval_max = i
        """

        # The vector "p" contains the optimal rotation (in quaternion format)

        p[:] = aaEigenvects[:, i_eval_max]
        """"
        p[0] = aaEigenvects[0][i_eval_max]
        p[1] = aaEigenvects[1][i_eval_max]
        p[2] = aaEigenvects[2][i_eval_max]
        p[3] = aaEigenvects[3][i_eval_max]
        pPp = eval_max
        """

    # normalize the vector
    # (It should be normalized already, but just in case it is not, do it again)
    p /= np.linalg.norm(p)

    # Finally, calculate the rotation matrix corresponding to "p"
    # (convert a quaternion into a 3x3 rotation matrix)

    the_rotation = R.from_quat(p)
    aaRotate = the_rotation.as_matrix()

    """
    aaRotate[0][0] =  (p[0]*p[0])-(p[1]*p[1])-(p[2]*p[2])+(p[3]*p[3])
    aaRotate[1][1] = -(p[0]*p[0])+(p[1]*p[1])-(p[2]*p[2])+(p[3]*p[3])
    aaRotate[2][2] = -(p[0]*p[0])-(p[1]*p[1])+(p[2]*p[2])+(p[3]*p[3])
    aaRotate[0][1] = 2*(p[0]*p[1] - p[2]*p[3]);
    aaRotate[1][0] = 2*(p[0]*p[1] + p[2]*p[3]);
    aaRotate[1][2] = 2*(p[1]*p[2] - p[0]*p[3]);
    aaRotate[2][1] = 2*(p[1]*p[2] + p[0]*p[3]);
    aaRotate[0][2] = 2*(p[0]*p[2] + p[1]*p[3]);
    aaRotate[2][0] = 2*(p[0]*p[2] - p[1]*p[3]);
    """

    # Optional: Decide the scale factor, c
    c = 1.0   # by default, don't rescale the coordinates
    if allow_rescale and (not singular):

        Waxaixai = np.sum(aWeights * aaXm ** 2)
        WaxaiXai = np.sum(aWeights * aaXf ** 2)

        """
        Waxaixai = 0.0
        WaxaiXai = 0.0
        
        for a in range(0, N):
            for i in range(0, 3):
                
                Waxaixai += aWeights[a] * aaXm[a][i] * aaXm[a][i]
                WaxaiXai += aWeights[a] * aaXm[a][i] * aaXf[a][i]
        """

        c = (WaxaiXai + pPp) / Waxaixai

    # Finally compute the RMSD between the two coordinate sets:
    # First compute E0 from equation 24 of the paper

    E0 = np.sum((aaXf - c*aaXm)**2)
    sum_sqr_dist = max(0, E0 - c * 2.0 * pPp)
    """
    E0 = 0.0
    for n in range(0, N):
        for d in range(0, 3):
            # (remember to include the scale factor "c" that we inserted)
            E0 += aWeights[n] * ((aaXf[n][d] - c*aaXm[n][d])**2)
    sum_sqr_dist = E0 - c*2.0*pPp
    if sum_sqr_dist < 0.0: #(edge case due to rounding error)
        sum_sqr_dist = 0.0
   """

    rmsd = 0.0
    if sum_weights != 0.0:
        rmsd = np.sqrt(sum_sqr_dist/sum_weights)

    # Lastly, calculate the translational offset:
    # Recall that:
    #RMSD=sqrt((Σ_i  w_i * |X_i - (Σ_j c*R_ij*x_j + T_i))|^2) / (Σ_j w_j))
    #    =sqrt((Σ_i  w_i * |X_i - x_i'|^2) / (Σ_j w_j))
    #  where
    # x_i' = Σ_j c*R_ij*x_j + T_i
    #      = Xcm_i + c*R_ij*(x_j - xcm_j)
    #  and Xcm and xcm = center_of_mass for the frozen and mobile point clouds
    #                  = aCenter_f[]       and       aCenter_m[],  respectively
    # Hence:
    #  T_i = Xcm_i - Σ_j c*R_ij*xcm_j  =  aTranslate[i]


    aTranslate = aCenter_f - (c*aaRotate @ aCenter_m).T.reshape(3,)

    """
    aTranslate = np.empty(3)
    for i in range(0,3):
        aTranslate[i] = aCenter_f[i]
        for j in range(0,3):
            aTranslate[i] -= c*aaRotate[i][j]*aCenter_m[j]
    """

    if report_quaternion: # does the caller want the quaternion?
        q = np.empty(4)
        q[0] = p[3]  # Note: The "p" variable is not a quaternion in the
        q[1] = p[0]  #       conventional sense because its elements
        q[2] = p[1]  #       are in the wrong order.  I correct for that here.
        q[3] = p[2]  #       "q" is the quaternion correspond to rotation R
        return rmsd, q, aTranslate, c
    else:
        return rmsd, aaRotate, aTranslate, c

