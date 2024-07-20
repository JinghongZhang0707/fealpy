
from typing import Any, Tuple, Union, Optional, overload

from .base import Backend, Size
from .base import TensorLike as _DT


class BackendManager():
    def __init__(self, *, default_backend: str): ...
    def set_backend(self, name: str) -> None: ...
    def load_backend(self, name: str) -> None: ...
    def get_current_backend(self) -> Backend: ...

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
    @staticmethod
    def is_tensor(obj: Any, /) -> bool: ...

    ### Tensor creation methods ###

    @staticmethod
    def tensor(data, *, dtype=None, device=None) -> _DT: ...
    @staticmethod
    def array(data, *, dtype=None, device=None) -> _DT: ...
    @staticmethod
    def cat(iterable, axis=None) -> _DT: ...
    @staticmethod
    def concatenate(iterable, axis=0) -> _DT: ...
    @staticmethod
    def stack(iterable, axis=0) -> _DT: ...
    @staticmethod
    def transpose(tensor: _DT, axes=None) -> _DT: ...
    @staticmethod
    def arange(start, stop, step=1) -> _DT: ...
    @staticmethod
    def linspace(start, stop, num, endpoint=True, retstep=False, dtype=None) -> _DT: ...
    @staticmethod
    def empty(shape, dtype=None, device=None): ...
    @staticmethod
    def zeros(shape, dtype=None, device=None): ...
    @staticmethod
    def ones(shape, dtype=None, device=None): ...
    @staticmethod
    def empty_like(tensor, dtype=None, device=None): ...
    @staticmethod
    def zeros_like(tensor, dtype=None, device=None): ...
    @staticmethod
    def ones_like(tensor, dtype=None, device=None): ...
    @staticmethod
    def eye(num_rows: int, num_cols: Optional[int]=None, k=0, *, dtype=None, device=None) -> _DT: ...
    @staticmethod
    def diag(diagonal: _DT, k: int=0) -> _DT: ...

    ### Reduction methods ###

    @staticmethod
    def all(tensor, axis=None, keepdims=False): ...
    @staticmethod
    def any(tensor, axis=None, keepdims=False): ...
    @staticmethod
    def sum(tensor, axis=None, keepdims=False): ...
    @staticmethod
    def prod(tensor, axis=None, keepdims=False): ...
    @staticmethod
    def cumsum(tensor, axis=None, dtype=None): ...
    @staticmethod
    def mean(tensor, axis=None, keepdims=False): ...
    @staticmethod
    def max(tensor, axis=None, keepdims=False): ...
    @staticmethod
    def min(tensor, axis=None, keepdims=False): ...

    ### Unary operations ###

    @staticmethod
    def abs(tensor: _DT) -> _DT: ...
    @staticmethod
    def sign(tensor: _DT) -> _DT: ...
    @staticmethod
    def sqrt(tensor: _DT) -> _DT: ...
    @staticmethod
    def log(tensor: _DT) -> _DT: ...
    @staticmethod
    def log10(tensor: _DT) -> _DT: ...
    @staticmethod
    def log2(tensor: _DT) -> _DT: ...

    ### Binary operations ###

    @staticmethod
    def add(input: _DT, other: _DT, *, out=None) -> _DT: ...
    @staticmethod
    def substract(input, other, *, out=None): ...
    @staticmethod
    def multiply(input, other, *, out=None): ...
    @staticmethod
    def divide(input, other, *, out=None): ...
    @staticmethod
    def matmul(input, other, *, out=None): ...
    @staticmethod
    def dot(input, other, *, out=None): ...
    @staticmethod
    def cross(input, other, *, out=None): ...
    @staticmethod
    def tensordot(tensor1, tensor2, dims=2): ...

    ### Other methods ##

    @staticmethod
    def reshape(tensor: _DT, shape: Size) -> _DT: ...
    @staticmethod
    def ravel(tensor: _DT) -> _DT: ...
    @staticmethod
    def flatten(tensor: _DT) -> _DT: ...
    @staticmethod
    def flip(tensor: _DT, axis: Union[None, int, Size]=None) -> _DT: ...
    @staticmethod
    def broadcast_to(tensor: _DT, shape: Size) -> _DT: ...
    @staticmethod
    def einsum(equation: str, *tensors: _DT) -> _DT: ...
    @staticmethod
    def unique(tensor: _DT, axis=0, return_indices=False, return_inverse=False): ...
    @staticmethod
    def sort(tensor: _DT, axis=0): ...
    @staticmethod
    def nonzero(tensor: _DT) -> Tuple[_DT, ...]: ...