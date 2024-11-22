import numpy as np

# 定义多个典型的 FirstNedelecDof2d 对象
# mesh = TriangleMesh.from_box(nx = 1,ny =1)
# p =  2

init_data = [
    {
        "fdof":6,
        "cdof":12,
        "gdof":180,
        "cell2dof":np.array([[102, 103, 104, 105, 106, 107,  66,  68,  67,  71,  70,  69,  54,
         55,  56,  57,  58,  59,  48,  50,  49,  53,  52,  51, 108, 109,
        110, 111, 112, 113, 114, 115, 116, 117, 118, 119],
       [ 96,  97,  98,  99, 100, 101,  54,  55,  56,  57,  58,  59,  60,
         61,  62,  63,  64,  65,  42,  44,  43,  47,  46,  45, 120, 121,
        122, 123, 124, 125, 126, 127, 128, 129, 130, 131],
       [ 78,  79,  80,  81,  82,  83,  60,  61,  62,  63,  64,  65,  12,
         13,  14,  15,  16,  17,   6,   8,   7,  11,  10,   9, 132, 133,
        134, 135, 136, 137, 138, 139, 140, 141, 142, 143],
       [ 72,  73,  74,  75,  76,  77,  12,  13,  14,  15,  16,  17,  36,
         37,  38,  39,  40,  41,   0,   2,   1,   5,   4,   3, 144, 145,
        146, 147, 148, 149, 150, 151, 152, 153, 154, 155],
       [ 84,  85,  86,  87,  88,  89,  36,  37,  38,  39,  40,  41,  30,
         31,  32,  33,  34,  35,  18,  20,  19,  23,  22,  21, 156, 157,
        158, 159, 160, 161, 162, 163, 164, 165, 166, 167],
       [ 90,  91,  92,  93,  94,  95,  30,  31,  32,  33,  34,  35,  66,
         68,  67,  71,  70,  69,  24,  26,  25,  29,  28,  27, 168, 169,
        170, 171, 172, 173, 174, 175, 176, 177, 178, 179]], dtype=np.int32),

        "basis":np.array([[[[ 1.08,  0.84,  0.48],
         [ 1.62,  1.26,  0.72],
         [ 2.16,  1.68,  0.96],
         [-0.06,  0.42,  0.24],
         [-0.18,  1.26,  0.72],
         [-0.24,  1.68,  0.96],
         [-0.06, -0.18,  0.24],
         [-0.12, -0.36,  0.48],
         [-0.24, -0.72,  0.96],
         [-0.06, -0.18, -0.36],
         [-0.12, -0.36, -0.72],
         [-0.18, -0.54, -1.08],
         [ 0.54,  0.42,  0.24],
         [-0.12,  0.84,  0.48],
         [-0.18, -0.54,  0.72]],

        [[ 0.3 ,  0.24,  0.06],
         [ 0.9 ,  0.72,  0.18],
         [ 0.3 ,  0.24,  0.06],
         [-1.5 ,  1.2 ,  0.3 ],
         [-0.9 ,  0.72,  0.18],
         [-0.3 ,  0.24,  0.06],
         [-1.5 , -1.8 ,  0.3 ],
         [-0.3 , -0.36,  0.06],
         [-0.3 , -0.36,  0.06],
         [-1.5 , -1.8 , -2.7 ],
         [-0.3 , -0.36, -0.54],
         [-0.9 , -1.08, -1.62],
         [ 1.5 ,  1.2 ,  0.3 ],
         [-0.3 ,  0.24,  0.06],
         [-0.9 , -1.08,  0.18]]],


       [[[ 1.08,  0.48,  0.72],
         [ 1.62,  0.72,  1.08],
         [ 2.16,  0.96,  1.44],
         [ 0.06, -0.24,  0.24],
         [ 0.18, -0.72,  0.72],
         [ 0.24, -0.96,  0.96],
         [-0.06,  0.24,  0.36],
         [-0.12,  0.48,  0.72],
         [-0.24,  0.96,  1.44],
         [-0.06, -0.36, -0.24],
         [-0.12, -0.72, -0.48],
         [-0.18, -1.08, -0.72],
         [ 0.54,  0.24,  0.36],
         [-0.12,  0.48, -0.48],
         [-0.18,  0.72,  1.08]],

        [[ 0.3 ,  0.06,  0.12],
         [ 0.9 ,  0.18,  0.36],
         [ 0.3 ,  0.06,  0.12],
         [ 1.5 , -0.3 ,  2.4 ],
         [ 0.9 , -0.18,  1.44],
         [ 0.3 , -0.06,  0.48],
         [-1.5 ,  0.3 ,  0.6 ],
         [-0.3 ,  0.06,  0.12],
         [-0.3 ,  0.06,  0.12],
         [-1.5 , -2.7 , -2.4 ],
         [-0.3 , -0.54, -0.48],
         [-0.9 , -1.62, -1.44],
         [ 1.5 ,  0.3 ,  0.6 ],
         [-0.3 ,  0.06, -0.48],
         [-0.9 ,  0.18,  0.36]]],


       [[[ 0.84,  0.48,  1.08],
         [ 1.26,  0.72,  1.62],
         [ 1.68,  0.96,  2.16],
         [-0.42, -0.24,  0.06],
         [-1.26, -0.72,  0.18],
         [-1.68, -0.96,  0.24],
         [-0.18,  0.24, -0.06],
         [-0.36,  0.48, -0.12],
         [-0.72,  0.96, -0.24],
         [-0.18, -0.36, -0.06],
         [-0.36, -0.72, -0.12],
         [-0.54, -1.08, -0.18],
         [ 0.42,  0.24,  0.54],
         [ 0.84,  0.48, -0.12],
         [-0.54,  0.72, -0.18]],

        [[ 0.24,  0.06,  0.3 ],
         [ 0.72,  0.18,  0.9 ],
         [ 0.24,  0.06,  0.3 ],
         [-1.2 , -0.3 ,  1.5 ],
         [-0.72, -0.18,  0.9 ],
         [-0.24, -0.06,  0.3 ],
         [-1.8 ,  0.3 , -1.5 ],
         [-0.36,  0.06, -0.3 ],
         [-0.36,  0.06, -0.3 ],
         [-1.8 , -2.7 , -1.5 ],
         [-0.36, -0.54, -0.3 ],
         [-1.08, -1.62, -0.9 ],
         [ 1.2 ,  0.3 ,  1.5 ],
         [ 0.24,  0.06, -0.3 ],
         [-1.08,  0.18, -0.9 ]]],


       [[[ 0.48,  0.72,  1.08],
         [ 0.72,  1.08,  1.62],
         [ 0.96,  1.44,  2.16],
         [-0.24,  0.24,  0.06],
         [-0.72,  0.72,  0.18],
         [-0.96,  0.96,  0.24],
         [ 0.24,  0.36, -0.06],
         [ 0.48,  0.72, -0.12],
         [ 0.96,  1.44, -0.24],
         [-0.36, -0.24, -0.06],
         [-0.72, -0.48, -0.12],
         [-1.08, -0.72, -0.18],
         [ 0.24,  0.36,  0.54],
         [ 0.48, -0.48, -0.12],
         [ 0.72,  1.08, -0.18]],

        [[ 0.06,  0.12,  0.3 ],
         [ 0.18,  0.36,  0.9 ],
         [ 0.06,  0.12,  0.3 ],
         [-0.3 ,  2.4 ,  1.5 ],
         [-0.18,  1.44,  0.9 ],
         [-0.06,  0.48,  0.3 ],
         [ 0.3 ,  0.6 , -1.5 ],
         [ 0.06,  0.12, -0.3 ],
         [ 0.06,  0.12, -0.3 ],
         [-2.7 , -2.4 , -1.5 ],
         [-0.54, -0.48, -0.3 ],
         [-1.62, -1.44, -0.9 ],
         [ 0.3 ,  0.6 ,  1.5 ],
         [ 0.06, -0.48, -0.3 ],
         [ 0.18,  0.36, -0.9 ]]],


       [[[ 0.48,  1.08,  0.84],
         [ 0.72,  1.62,  1.26],
         [ 0.96,  2.16,  1.68],
         [-0.24,  0.06, -0.42],
         [-0.72,  0.18, -1.26],
         [-0.96,  0.24, -1.68],
         [ 0.24, -0.06, -0.18],
         [ 0.48, -0.12, -0.36],
         [ 0.96, -0.24, -0.72],
         [-0.36, -0.06, -0.18],
         [-0.72, -0.12, -0.36],
         [-1.08, -0.18, -0.54],
         [ 0.24,  0.54,  0.42],
         [ 0.48, -0.12,  0.84],
         [ 0.72, -0.18, -0.54]],

        [[ 0.06,  0.3 ,  0.24],
         [ 0.18,  0.9 ,  0.72],
         [ 0.06,  0.3 ,  0.24],
         [-0.3 ,  1.5 , -1.2 ],
         [-0.18,  0.9 , -0.72],
         [-0.06,  0.3 , -0.24],
         [ 0.3 , -1.5 , -1.8 ],
         [ 0.06, -0.3 , -0.36],
         [ 0.06, -0.3 , -0.36],
         [-2.7 , -1.5 , -1.8 ],
         [-0.54, -0.3 , -0.36],
         [-1.62, -0.9 , -1.08],
         [ 0.3 ,  1.5 ,  1.2 ],
         [ 0.06, -0.3 ,  0.24],
         [ 0.18, -0.9 , -1.08]]],


       [[[ 0.72,  1.08,  0.48],
         [ 1.08,  1.62,  0.72],
         [ 1.44,  2.16,  0.96],
         [ 0.24,  0.06, -0.24],
         [ 0.72,  0.18, -0.72],
         [ 0.96,  0.24, -0.96],
         [-0.36,  0.06, -0.24],
         [-0.72,  0.12, -0.48],
         [-1.44,  0.24, -0.96],
         [-0.24, -0.06, -0.36],
         [-0.48, -0.12, -0.72],
         [-0.72, -0.18, -1.08],
         [ 0.36,  0.54,  0.24],
         [-0.48, -0.12,  0.48],
         [ 1.08, -0.18,  0.72]],

        [[ 0.12,  0.3 ,  0.06],
         [ 0.36,  0.9 ,  0.18],
         [ 0.12,  0.3 ,  0.06],
         [ 2.4 ,  1.5 , -0.3 ],
         [ 1.44,  0.9 , -0.18],
         [ 0.48,  0.3 , -0.06],
         [-0.6 ,  1.5 , -0.3 ],
         [-0.12,  0.3 , -0.06],
         [-0.12,  0.3 , -0.06],
         [-2.4 , -1.5 , -2.7 ],
         [-0.48, -0.3 , -0.54],
         [-1.44, -0.9 , -1.62],
         [ 0.6 ,  1.5 ,  0.3 ],
         [-0.48, -0.3 ,  0.06],
         [ 0.36, -0.9 ,  0.18]]]]),

        "div_basis":np.array([[[  4.8,   7.2,   9.6,   2.4,   7.2,   9.6,   2.4,   4.8,   9.6,
           2.4,   4.8,   7.2,  -3.6,  -1.2,   1.2],
        [  2.4,   7.2,   2.4,  12. ,   7.2,   2.4,  12. ,   2.4,   2.4,
          12. ,   2.4,   7.2,   6. ,  -3.6,   1.2]],

       [[  4.8,   7.2,   9.6,  -2.4,  -7.2,  -9.6,   2.4,   4.8,   9.6,
           2.4,   4.8,   7.2,  -3.6,  -1.2,   1.2],
        [  2.4,   7.2,   2.4, -12. ,  -7.2,  -2.4,  12. ,   2.4,   2.4,
          12. ,   2.4,   7.2,   6. ,  -3.6,   1.2]],

       [[  4.8,   7.2,   9.6,  -2.4,  -7.2,  -9.6,   2.4,   4.8,   9.6,
           2.4,   4.8,   7.2,  -3.6,  -1.2,   1.2],
        [  2.4,   7.2,   2.4, -12. ,  -7.2,  -2.4,  12. ,   2.4,   2.4,
          12. ,   2.4,   7.2,   6. ,  -3.6,   1.2]],

       [[  4.8,   7.2,   9.6,  -2.4,  -7.2,  -9.6,   2.4,   4.8,   9.6,
           2.4,   4.8,   7.2,  -3.6,  -1.2,   1.2],
        [  2.4,   7.2,   2.4, -12. ,  -7.2,  -2.4,  12. ,   2.4,   2.4,
          12. ,   2.4,   7.2,   6. ,  -3.6,   1.2]],

       [[  4.8,   7.2,   9.6,  -2.4,  -7.2,  -9.6,   2.4,   4.8,   9.6,
           2.4,   4.8,   7.2,  -3.6,  -1.2,   1.2],
        [  2.4,   7.2,   2.4, -12. ,  -7.2,  -2.4,  12. ,   2.4,   2.4,
          12. ,   2.4,   7.2,   6. ,  -3.6,   1.2]],

       [[  4.8,   7.2,   9.6,  -2.4,  -7.2,  -9.6,  -2.4,  -4.8,  -9.6,
           2.4,   4.8,   7.2,  -3.6,  -1.2,   1.2],
        [  2.4,   7.2,   2.4, -12. ,  -7.2,  -2.4, -12. ,  -2.4,  -2.4,
          12. ,   2.4,   7.2,   6. ,  -3.6,   1.2]]]),

    }
]