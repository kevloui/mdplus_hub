import numpy as np
import pytest

from src.core.exceptions import ModelNotTrainedError
from src.glimps.adapter import GlimpsAdapter


class MockGlimpsModel:
    def __init__(self):
        self.fitted = False
        self._training_data = None

    def fit(self, cg_coords, atomistic_coords):
        self.fitted = True
        self._training_data = (cg_coords, atomistic_coords)
        return self

    def transform(self, cg_coords):
        if not self.fitted:
            raise ValueError("Model not fitted")
        n_frames, n_cg_atoms, _ = cg_coords.shape
        n_atomistic = n_cg_atoms * 3
        return np.random.randn(n_frames, n_atomistic, 3)

    def inverse_transform(self, atomistic_coords):
        if not self.fitted:
            raise ValueError("Model not fitted")
        return atomistic_coords[:, ::3, :]


class TestGlimpsAdapter:
    def test_fit_sets_fitted_flag(self):
        mock_model = MockGlimpsModel()
        adapter = GlimpsAdapter(mock_model)

        cg_coords = np.random.randn(10, 50, 3)
        atomistic_coords = np.random.randn(10, 150, 3)

        adapter.fit(cg_coords, atomistic_coords)

        assert adapter.is_fitted
        assert mock_model.fitted

    def test_transform_raises_when_not_fitted(self):
        mock_model = MockGlimpsModel()
        adapter = GlimpsAdapter(mock_model)

        with pytest.raises(ModelNotTrainedError, match="Model not fitted"):
            adapter.transform(np.random.randn(1, 50, 3))

    def test_inverse_transform_raises_when_not_fitted(self):
        mock_model = MockGlimpsModel()
        adapter = GlimpsAdapter(mock_model)

        with pytest.raises(ModelNotTrainedError, match="Model not fitted"):
            adapter.inverse_transform(np.random.randn(1, 150, 3))

    def test_transform_returns_atomistic_coordinates(self):
        mock_model = MockGlimpsModel()
        adapter = GlimpsAdapter(mock_model)

        cg_coords = np.random.randn(5, 50, 3)
        atomistic_coords = np.random.randn(5, 150, 3)

        adapter.fit(cg_coords, atomistic_coords)
        result = adapter.transform(cg_coords)

        assert result.shape[0] == 5
        assert result.shape[2] == 3

    def test_is_fitted_property_default_false(self):
        mock_model = MockGlimpsModel()
        adapter = GlimpsAdapter(mock_model)

        assert not adapter.is_fitted

    def test_progress_callback_is_called(self):
        mock_model = MockGlimpsModel()
        adapter = GlimpsAdapter(mock_model)

        progress_calls = []

        def callback(percent, message):
            progress_calls.append((percent, message))

        cg_coords = np.random.randn(5, 50, 3)
        atomistic_coords = np.random.randn(5, 150, 3)

        adapter.fit(cg_coords, atomistic_coords, progress_callback=callback)

        assert len(progress_calls) == 2
        assert progress_calls[0] == (0.0, "Starting training...")
        assert progress_calls[1] == (100.0, "Training complete")

    def test_fit_without_model_raises_error(self):
        adapter = GlimpsAdapter(None)

        with pytest.raises(ValueError, match="No model provided"):
            adapter.fit(np.random.randn(5, 50, 3), np.random.randn(5, 150, 3))
