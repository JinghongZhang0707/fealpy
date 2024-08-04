
from typing import (
    Any, Tuple, Union, Optional, overload, TypeGuard, 
    Literal, Dict
)

from .base import Backend, Size, Number
from .base import TensorLike as _DT


"""
This class serves as an interface for the computation backend.
All methods in this class are static methods by default,
unless explicitly annotated otherwise.
"""

class BackendManager():
    def __init__(self, *, default_backend: str): ... # instance method
    def set_backend(self, name: str) -> None: ... # instance method
    def load_backend(self, name: str) -> None: ... # instance method
    def get_current_backend(self) -> Backend: ... # instance method

    def context(self, tensor) -> Dict[str, Any]: ...

    ### constants ###

    pi: float
    e: float
    nan: float
    inf: float
    dtype: type
    device: type
    bool_: Any
    uint8: Any
    int_: Any
    int8: Any
    int16: Any
    int32: Any
    int64: Any
    float_: Any
    float16: Any
    float32: Any
    float64: Any
    complex_: Any
    complex64: Any
    complex128: Any
    
    ### Backend tools ###
    def is_tensor(self, obj: Any, /) -> TypeGuard[_DT]: ...
    # PyTorch
    def set_default_device(self, device: Any) -> None: ...
    def get_device(self, tensor_like: _DT, /) -> Any: ...
    def to_numpy(self, tensor_like: _DT, /) -> Any: ...
    # PyTorch
    def from_numpy(self, ndarray: Any, /) -> _DT: ...

    ### Functional programming ###

    def apply_along_axis(self, func1d, axis, arr: _DT, *args, **kwargs) -> _DT: ...

    ### Tensor creation routines ###
    ## From shape or value
    def empty(self, shape: Size, /, *, dtype=None, **kwargs) -> _DT: ...

    def empty_like(self, a: _DT, /, *, dtype=None, **kwargs) -> _DT: ...

    def eye(self, n: int, m: Optional[int]=None, /, k: int=0, dtype=None, **kwargs) -> _DT: ...
    
    #new
    #def identity(self, n: int, /, *, dtype=None, **kwargs) -> _DT:

    def ones(self, shape: Size, /, *, dtype=None, **kwargs) -> _DT: ...

    def ones_like(self, a: _DT, /, *, dtype=None, **kwargs) -> _DT: ...

    def zeros(self, shape: Size, /, *, dtype=None, **kwargs) -> _DT: ...

    def zeros_like(self, a: _DT, /, *, dtype=None, **kwargs) -> _DT: ...

    def full(self, shape: Size, fill_value: Number, /, *, dtype=None, **kwargs) -> _DT: ...

    def full_like(self, a: _DT, fill_value: Number, /, *, dtype=None, **kwargs) -> _DT: ...

    ## From existing data
    def array(self, object, /, dtype=None, **kwargs) -> _DT: ...
    # pyTorch
    def tensor(self, data, /, dtype=None, **kwargs) -> _DT: ...
    
    ## Creating record arrays

    ## Creating character arrays 

    ## Numerical ranges
    @overload
    def arange(self, stop: int, /, *, dtype=None, **kwargs) -> _DT: ...
    @overload
    def arange(self, start: int, stop: int, /, step=1, *, dtype=None, **kwargs) -> _DT: ...
    
    def linspace(self, start, stop, num, /, endpoint=True, retstep=False, dtype=None, **kwargs) -> _DT: ... 
    
    def meshgrid(self, *xi: Any, copy=True, sparse=False, indexing='xy', **kwargs) -> Tuple[_DT, ...]: ...
    
    ## Building matrices

    ## The matrix class

    

    ### Array manipulation routines ###
    
    ### Functional programming ###
    def apply_along_axis(self, func1d, axis, arr: _DT, *args, **kwargs) 

    ### Linear algebra ###
    
    ### Indexing routines  ###
    
    ### Mathematical functions ###
    ## Trigonometric functions
    def sin(self, __x1: _DT, out=None, **kwargs) -> _DT: ...
   
    def cos(self, __x1: _DT, out=None, **kwargs) -> _DT: ...
 
    def tan(self, __x1: _DT, out=None, **kwargs) -> _DT: ...

    def arcsin(self, __x1: _DT, out=None, **kwargs) -> _DT: ...

    def arccos(self, __x1: _DT, out=None, **kwargs) -> _DT: ...

    def arctan(self, __x1: _DT, out=None, **kwargs) -> _DT: ...

    def arctan2(self, __y: _DT, __x: _DT, out=None, **kwargs) -> _DT: ...
    
    ## Hyperbolic functions
    def sinh(self, __x1: _DT, out=None, **kwargs) -> _DT: ...
    
    def cosh(self, __x1: _DT, out=None, **kwargs) -> _DT: ...
    
    def tanh(self, __x1: _DT, out=None, **kwargs) -> _DT: ...
    
    def arcsinh(self, __x1: _DT, out=None, **kwargs) -> _DT: ...
    
    def arccosh(self, __x1: _DT, out=None, **kwargs) -> _DT: ...
    
    def arctanh(self, __x1: _DT, out=None, **kwargs) -> _DT: ...



    ## Sums, products, differences
    def prod(self, a: _DT, axis=None, dtype=None, out=None, keepdims=False, initial: Number=...) -> _DT: ...

    def sum(self, a: _DT, axis=None, dtype=None, out=None, keepdims=False, initial: Number=...) -> _DT: ...
    
    def cross(self, a: _DT, b: _DT, axis: Optional[int]=None, **kwargs) -> _DT: ...
    
    ## Exponents and logarithms
    def exp(self, __x1: _DT, out=None, **kwargs) -> _DT: ...
    
    def log(self, __x1: _DT, out=None, **kwargs) -> _DT: ...
    
    def log2(self, __x1: _DT, out=None, **kwargs) -> _DT: ...
    
    def log10(self, __x1: _DT, out=None, **kwargs) -> _DT: ...
    
    ## Arithmetic operations
    def add(self, __x1: _DT, __x2: _DT, out=None, **kwargs) -> _DT: ...
    
    def multiply(self, __x1: _DT, __x2: _DT, out=None, **kwargs) -> _DT: ...
    
    def divide(self, __x1: _DT, __x2: _DT, out=None, **kwargs) -> _DT: ...
    
    def power(self, __x1: _DT, __x2: _DT, out=None, **kwargs) -> _DT: ...
    
    def substract(self, __x1: _DT, __x2: _DT, out=None, **kwargs) -> _DT: ...
    
    ## Extrema finding
    def max(self, a: _DT, axis=None, out=None, keepdims=False): ...

    def min(self, a: _DT, axis=None, out=None, keepdims=False): ...
    
    ## Miscellaneous
    def sqrt(self, __x1: _DT, out=None, **kwargs) -> _DT: ...
   
    def square(self, __x1: _DT, out=None, **kwargs) -> _DT: ...

    def sign(self, __x1: _DT, out=None, **kwargs) -> _DT: ...


    ### Random ###













    ### Reduction methods ###

    # Numpy
    def all(self, a: _DT, axis=None, out=None, keepdims=False) -> _DT: ...
    # Numpy
    def any(self, a: _DT, axis=None, out=None, keepdims=False) -> _DT: ...
    # Numpy
    def mean(self, a: _DT, axis=None, dtype=None, out=None, keepdims=False) -> _DT: ...
    # Numpy
    def argmax(self, a: _DT, axis=None, out=None, *, keepdims=False) -> _DT: ...
    # Numpy
    def argmin(self, a: _DT, axis=None, out=None, *, keepdims=False) -> _DT: ...

    ### Unary operations ###

    # Numpy + PyTorch
    def abs(self, __x1: _DT, out=None, **kwargs) -> _DT: ...
    # Numpy + PyTorch
    # Numpy + PyTorch
    # Numpy + PyTorch
    
    # Numpy + PyTorch
    # Numpy + PyTorch
    def clip(self, a: _DT, a_min: Number, a_max: Number, /, out=None, **kwargs) -> _DT: ...
    # Numpy + PyTorch
    def floor(self, __x1: _DT, out=None, **kwargs) -> _DT: ...
    # Numpy + PyTorch
    def ceil(self, __x1: _DT, out=None, **kwargs) -> _DT: ...
    # Numpy + PyTorch
    def round(self, __x1: _DT, *, decimals=0, out=None, **kwargs) -> _DT: ...

    ### Binary operations ###

    # Numpy + PyTorch
    # -
    def add_at(self, a: _DT, indices, src: _DT, /) -> None: ...
    # PyTorch only
    def index_add_(self, a: _DT, /, dim: int, index: _DT, src: _DT, *, alpha: Number=1.) -> _DT: ...
    # Numpy + PyTorch
    # Numpy + PyTorch
    def matmul(self, __x1: _DT, __x2: _DT, out=None, **kwargs) -> _DT: ...
    # Numpy + PyTorch
    def dot(self, a: _DT, b: _DT, out=None) -> _DT: ...
    # Numpy
    # Numpy
    def tensordot(self, a: _DT, b: _DT, axes: Union[int, Tuple]) -> _DT: ...

    ### Other methods ###

    # Numpy
    def copy(self, a: _DT, /, **kwargs) -> _DT: ...
    # Numpy + PyTorch
    def reshape(self, a: _DT, newshape: Size, /) -> _DT: ...
    # Numpy + PyTorch
    def broadcast_to(self, array: _DT, shape: Size, /) -> _DT: ...
    # Numpy + PyTorch
    def einsum(self, subscripts: str, /, *operands: _DT, **kwargs) -> _DT: ...
    # Numpy
    def unique(self, ar: _DT, return_index=False, return_inverse=False, return_counts=False, axis=0, **kwargs): ...
    # Numpy
    def sort(self, a: _DT, axis=0, **kwargs) -> _DT: ...
    # Numpy
    def argsort(self, a: _DT, axis=-1, **kwargs) -> _DT: ...
    # -
    @overload
    def nonzero(self, a: _DT, /) -> Tuple[_DT, ...]: ...
    @overload
    def nonzero(self, a: _DT, /, as_tuple: Literal[True]) -> Tuple[_DT, ...]: ...
    @overload
    def nonzero(self, a: _DT, /, as_tuple: Literal[False]) -> _DT: ...
    # Numpy
    def cumsum(self, a: _DT, axis=None, dtype=None, out=None) -> _DT: ...
    # Numpy
    def cumprod(self, a: _DT, axis=None, dtype=None, out=None) -> _DT: ...
    # PyTorch
    def cat(self, tensors, dim=0, *, out=None) -> _DT: ...
    # Numpy
    def concatenate(self, arrays, /, axis=0, out=None, *, dtype=None) -> _DT: ...
    # Numpy
    def stack(self, arrays, axis=0, out=None, *, dtype=None) -> _DT: ...
    # Numpy + PyTorch
    def repeat(self, a: _DT, repeats: int, axis: Optional[int]=None, /) -> _DT: ...
    # Numpy + PyTorch(permute)
    def transpose(self, a: _DT, axes: Size, /) -> _DT: ...
    # Numpy + PyTorch
    def swapaxes(self, a: _DT, axis1: int, axis2: int, /) -> _DT: ...
    # Numpy
    def flip(self, a: _DT, axis: Optional[Union[int, Tuple[int, ...]]]=None) -> _DT: ...
    # Numpy
    def where(self, condition: _DT, x: Optional[_DT]=None, y: Optional[_DT]=None, /, out=None) -> _DT: ...
    # Numpy + PyTorch
    def tile(self, a: _DT, reps: Size, /) -> _DT: ...

    ### FEALPy functionals ###

    def multi_index_matrix(self, p: int, dim: int, *, dtype=None) -> _DT: ...
    def edge_length(self, edge: _DT, node: _DT, *, out=None) -> _DT: ...
    def edge_normal(self, edge: _DT, node: _DT, unit=False, *, out=None) -> _DT: ...
    def edge_tangent(self, edge: _DT, node: _DT, unit=False, *, out=None) -> _DT: ...
    def tensorprod(self, *tensors: _DT) -> _DT: ...
    def bc_to_points(self, bcs: Union[_DT, Tuple[_DT, ...]], node: _DT, entity: _DT) -> _DT: ...
    def barycenter(self, entity: _DT, node: _DT, loc: Optional[_DT]=None) -> _DT: ...
    def simplex_ldof(self, p: int, iptype: int) -> int: ... # implement in base
    def simplex_gdof(self, p: int, nums: Tuple[int, ...]) -> int: ... # implement in base
    def simplex_measure(self, entity: _DT, node: _DT) -> _DT: ...
    def simplex_shape_function(self, bc: _DT, p: int, mi: Optional[_DT]=None) -> _DT: ...
    def simplex_grad_shape_function(self, bc: _DT, p: int, mi: Optional[_DT]=None) -> _DT: ...
    def simplex_hess_shape_function(self, bc: _DT, p: int, mi: Optional[_DT]=None) -> _DT: ...
    def tensor_ldof(self, p: int, iptype: int) -> int: ... # implement in base
    def tensor_gdof(self, p: int, nums: Tuple[int, ...]) -> int: ... # implement in base
    def tensor_measure(self, entity: _DT, node: _DT) -> _DT: ...

    def interval_grad_lambda(self, line: _DT, node: _DT) -> _DT: ...
    def triangle_area_3d(self, tri: _DT, node: _DT) -> _DT: ...
    def triangle_grad_lambda_2d(self, tri: _DT, node: _DT) -> _DT: ...
    def triangle_grad_lambda_3d(self, tri: _DT, node: _DT) -> _DT: ...
    def quadrangle_grad_lambda_2d(self, quad: _DT, node: _DT) -> _DT: ...
    def tetrahedron_grad_lambda_3d(self, tet: _DT, node: _DT, local_face: _DT) -> _DT: ...
