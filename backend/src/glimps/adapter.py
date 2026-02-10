from typing import Callable, Protocol

import numpy as np
from numpy.typing import NDArray

from src.core.exceptions import ModelNotTrainedError


class GlimpsModelProtocol(Protocol):
    def fit(
        self,
        cg_coords: NDArray[np.float64],
        atomistic_coords: NDArray[np.float64],
    ) -> "GlimpsModelProtocol": ...

    def transform(
        self,
        cg_coords: NDArray[np.float64],
    ) -> NDArray[np.float64]: ...

    def inverse_transform(
        self,
        atomistic_coords: NDArray[np.float64],
    ) -> NDArray[np.float64]: ...


ProgressCallback = Callable[[float, str], None]


class GlimpsAdapter:
    def __init__(self, model: GlimpsModelProtocol | None = None):
        self._model = model
        self._is_fitted = False

    @classmethod
    def create_default(cls) -> "GlimpsAdapter":
        from mdplus.multiscale import Glimps

        return cls(Glimps())

    def fit(
        self,
        cg_coords: NDArray[np.float64],
        atomistic_coords: NDArray[np.float64],
        progress_callback: ProgressCallback | None = None,
    ) -> "GlimpsAdapter":
        if self._model is None:
            raise ValueError("No model provided")

        if progress_callback:
            progress_callback(0.0, "Starting training...")

        self._model.fit(cg_coords, atomistic_coords)
        self._is_fitted = True

        if progress_callback:
            progress_callback(100.0, "Training complete")

        return self

    def transform(
        self,
        cg_coords: NDArray[np.float64],
    ) -> NDArray[np.float64]:
        if not self._is_fitted:
            raise ModelNotTrainedError("Model not fitted")

        return self._model.transform(cg_coords)

    def inverse_transform(
        self,
        atomistic_coords: NDArray[np.float64],
    ) -> NDArray[np.float64]:
        if not self._is_fitted:
            raise ModelNotTrainedError("Model not fitted")

        return self._model.inverse_transform(atomistic_coords)

    @property
    def is_fitted(self) -> bool:
        return self._is_fitted
