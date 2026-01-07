from sympy.physics.hep.gamma_matrices import GammaMatrix as G, kahane_simplify, LorentzIndex
from sympy.tensor.tensor import tensor_indices

def test_kahane_leading_gamma_matrix_bug():
    mu, nu, rho, sigma = tensor_indices("mu, nu, rho, sigma", LorentzIndex)
    
    # Test case 1: Correct behavior
    t1 = G(mu)*G(-mu)*G(rho)*G(sigma)
    r1 = kahane_simplify(t1)
    assert r1.equals(4*G(rho)*G(sigma)), "Test case 1 failed: Order of gamma matrices is incorrect"

    # Test case 2: Correct behavior expected
    t2 = G(rho)*G(sigma)*G(mu)*G(-mu)
    r2 = kahane_simplify(t2)
    assert r2.equals(4*G(rho)*G(sigma)), "Test case 2 failed: Order of gamma matrices is incorrect"
