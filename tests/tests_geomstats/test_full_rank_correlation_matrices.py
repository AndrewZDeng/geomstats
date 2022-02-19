"""Unit tests for the manifold of matrices."""

import random


import geomstats.backend as gs
from geomstats.geometry.full_rank_correlation_matrices import (
    CorrelationMatricesBundle,
    FullRankCorrelationAffineQuotientMetric,
    FullRankCorrelationMatrices,
)
from geomstats.geometry.general_linear import GeneralLinear
from geomstats.geometry.matrices import Matrices
from geomstats.geometry.symmetric_matrices import SymmetricMatrices
from tests.conftest import TestCase, autograd_tf_and_torch_only
from tests.data_generation import LevelSetTestData, TestData
from tests.parametrizers import LevelSetParametrizer, Parametrizer


class TestFullRankCorrelationMatrices(TestCase, metaclass=LevelSetParametrizer):

    space = FullRankCorrelationMatrices
    skip_test_extrinsic_intrinsic_composition = True
    skip_test_intrinsic_extrinsic_composition = True

    class TestDataRankFullRankCorrelationMatrices(LevelSetTestData):

        n_list = random.sample(range(2, 5), 2)
        space_args_list = [(n,) for n in n_list]
        shape_list = [(n, n) for n in n_list]
        n_samples_list = random.sample(range(2, 5), 2)
        n_points_list = random.sample(range(2, 5), 2)
        n_vecs_list = random.sample(range(2, 5), 2)

        def random_point_belongs_data(self):
            smoke_space_args_list = [(2,), (3,)]
            smoke_n_points_list = [1, 2]
            return self._random_point_belongs_data(
                smoke_space_args_list,
                smoke_n_points_list,
                self.space_args_list,
                self.n_points_list,
            )

        def projection_belongs_data(self):
            return self._projection_belongs_data(
                self.space_args_list, self.shape_list, self.n_samples_list
            )

        def to_tangent_is_tangent_data(self):
            return self._to_tangent_is_tangent_data(
                FullRankCorrelationMatrices,
                self.space_args_list,
                self.shape_list,
                self.n_vecs_list,
            )

    testing_data = TestDataRankFullRankCorrelationMatrices()


class TestCorrelationMatricesBundle(TestCase, metaclass=Parametrizer):
    space = CorrelationMatricesBundle

    class TestDataCorrelationMatricesBundle(TestData):
        n_list = random.sample(range(2, 7), 3)
        n_samples_list = random.sample(range(1, 7), 3)

        def riemannian_submersion_belongs_to_base_data(self):
            random_data = []
            for n, n_samples in zip(self.n_list, self.n_samples_list):
                bundle = CorrelationMatricesBundle(n)
                point = bundle.base.random_point(n_samples)
                random_data.append(dict(n=n, point=point))
            return self.generate_tests([], random_data)

        def lift_riemannian_submersion_composition_data(self):
            random_data = []
            for n, n_samples in zip(self.n_list, self.n_samples_list):
                bundle = CorrelationMatricesBundle(n)
                point = bundle.base.random_point(n_samples)
                random_data.append(dict(n=n, point=point))
            return self.generate_tests([], random_data)

        def tangent_riemannian_submersion_data(self):
            random_data = []
            for n, n_samples in zip(self.n_list, self.n_samples_list):
                bundle = CorrelationMatricesBundle(n)
                mat = bundle.random_point()
                point = bundle.riemannian_submersion(mat)
                vec = bundle.random_point(n_samples)
                random_data.append(dict(n=n, vec=vec, point=point))
            return self.generate_tests([], random_data)

        def vertical_projection_tangent_submersion_data(self):
            random_data = []
            for n in self.n_list:
                bundle = CorrelationMatricesBundle(n)
                mat = bundle.random_point(2)
                vec = SymmetricMatrices(n).random_point(2)
                random_data.append(dict(n=n, vec=vec, mat=mat))
            return self.generate_tests([], random_data)

        def horizontal_projection_data(self):
            random_data = []
            for n in self.n_list:
                bundle = CorrelationMatricesBundle(n)
                mat = bundle.random_point()
                vec = bundle.random_point()
                random_data.append(dict(n=n, vec=vec, mat=mat))
            return self.generate_tests([], random_data)

        def horizontal_lift_is_horizontal_data(self):
            random_data = []
            for n, n_samples in zip(self.n_list, self.n_samples_list):
                bundle = CorrelationMatricesBundle(n)
                mat = bundle.base.random_point()
                vec = bundle.base.random_point(n_samples)
                tangent_vec = bundle.base.to_tangent(vec, mat)
                random_data.append(dict(n=n, tangent_vec=tangent_vec, mat=mat))
            return self.generate_tests([], random_data)

        def vertical_projection_is_vertical_data(self):
            random_data = []
            for n, n_samples in zip(self.n_list, self.n_samples_list):
                bundle = CorrelationMatricesBundle(n)
                mat = bundle.random_point()
                vec = bundle.random_point(n_samples)
                tangent_vec = bundle.base.to_tangent(vec, mat)
                random_data.append(dict(n=n, tangent_vec=tangent_vec, mat=mat))
            return self.generate_tests([], random_data)

        def horizontal_lift_and_tangent_riemannian_submersion_data(self):
            random_data = []
            for n, n_samples in zip(self.n_list, self.n_samples_list):
                bundle = CorrelationMatricesBundle(n)
                mat = bundle.base.random_point()
                vec = bundle.base.random_point(n_samples)
                tangent_vec = bundle.base.to_tangent(vec, mat)
                random_data.append(dict(n=n, tangent_vec=tangent_vec, mat=mat))

            return self.generate_tests([], random_data)

    testing_data = TestDataCorrelationMatricesBundle()

    def test_riemannian_submersion_belongs_to_base(self, n, point):
        bundle = self.space(n)
        result = bundle.base.belongs(bundle.riemannian_submersion(gs.array(point)))
        self.assertAllClose(result, gs.array(True))

    def test_lift_riemannian_submersion_composition(self, n, point):
        bundle = self.space(n)
        result = bundle.riemannian_submersion(bundle.lift(gs.array(point)))
        self.assertAllClose(result, gs.array(point))

    def test_tangent_riemannian_submersion(self, n, vec, point):
        bundle = self.space(n)
        tangent_vec = bundle.tangent_riemannian_submersion(
            gs.array(vec), gs.array(point)
        )
        result = gs.all(bundle.is_tangent(vec, gs.array(point)))
        self.assertAllClose(result, gs.array(True))

    def test_vertical_projection_tangent_submersion(self, n, vec, mat):
        bundle = self.space(n)
        tangent_vec = bundle.to_tangent(vec, mat)
        proj = bundle.vertical_projection(gs.array(tangent_vec), gs.array(mat))
        result = bundle.tangent_riemannian_submersion(proj, gs.array(mat))
        expected = gs.zeros_like(vec)
        self.assertAllClose(result, gs.array(expected))

    def test_horizontal_projection(self, n, vec, mat):
        bundle = self.space(n)
        horizontal_vec = bundle.horizontal_projection(vec, mat)
        inverse = GeneralLinear.inverse(mat)
        product_1 = Matrices.mul(horizontal_vec, inverse)
        product_2 = Matrices.mul(inverse, horizontal_vec)
        is_horizontal = gs.all(
            bundle.base.is_tangent(product_1 + product_2, mat, atol=gs.atol * 10)
        )
        self.assertAllClose(is_horizontal, gs.array(True))

    def test_horizontal_lift_is_horizontal(self, n, tangent_vec, mat):
        bundle = self.space(n)
        lift = bundle.horizontal_lift(gs.array(tangent_vec), gs.array(mat))
        result = gs.all(bundle.is_horizontal(lift, gs.array(mat)))
        self.assertAllClose(result, gs.array(True))

    def test_vertical_projection_is_vertical(self, n, tangent_vec, mat):
        bundle = self.space(n)
        proj = bundle.vertical_projection(gs.array(tangent_vec), gs.array(mat))
        result = gs.all(bundle.is_vertical(proj, gs.array(mat)))
        self.assertAllClose(result, gs.array(True))

    @autograd_tf_and_torch_only
    def test_align_is_horizontal(
        self,
        point1,
        point2,
    ):
        aligned = self.bundle.align(point1, point2, tol=1e-10)
        log = self.bundle.ambient_metric.log(aligned, point2)
        result = self.bundle.is_horizontal(log, point2, atol=gs.atol * 100)
        self.assertTrue(result)

    def test_horizontal_lift_and_tangent_riemannian_submersion(
        self, n, tangent_vec, mat
    ):
        bundle = self.space(n)
        horizontal = bundle.horizontal_lift(gs.array(tangent_vec), gs.array(mat))
        result = bundle.tangent_riemannian_submersion(horizontal, gs.array(mat))
        self.assertAllClose(result, tangent_vec)


# class TestFullRankCorrelationAffineQuotientMetric(
#     TestCase, metaclass=Parametrizer
# ):
#     metric = connection = FullRankCorrelationAffineQuotientMetric

#     class TestDataFullRankcorrelationAffineQuotientMetric(TestData):

#         @geomstats.tests.autograd_tf_and_torch_only
#         def test_exp_and_log(self):
#             mats = self.bundle.random_point(2)
#             points = self.bundle.riemannian_submersion(mats)

#             log = self.quotient_metric.log(points[1], points[0])
#             result = self.quotient_metric.exp(log, points[0])
#             self.assertAllClose(result, points[1], atol=gs.atol * 100)


#     testing_data =TestDataFullRankcorrelationAffineQuotientMetric()
