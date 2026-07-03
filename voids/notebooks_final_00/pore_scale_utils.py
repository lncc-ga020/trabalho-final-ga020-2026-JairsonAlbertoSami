"""
pore_scale_utils.py
====================
Funções compartilhadas para homogeneização de permeabilidade (Darcy) em
microestruturas binárias 2D, usadas tanto no pipeline de produção
(fina_note.ipynb -> TESte_Geral.ipynb) quanto no notebook de validação
(validacao_solver.ipynb).

Manter isso num único lugar evita o problema que já apareceu na prática:
duas cópias da mesma lógica (ex.: build_permeability definida duas vezes
em notebooks diferentes) divergindo silenciosamente depois de um ajuste
feito em só um dos lugares.

Convenções assumidas (documentadas aqui para não se perder):
- void_array[row, col]: linha 0 = TOPO do domínio físico (y = Ly),
  última linha = BASE do domínio (y = 0). Ou seja, segue a convenção
  de imagem (linha cresce para baixo), que é invertida em relação à
  convenção do Firedrake (y cresce para cima). É por isso que
  build_permeability faz o flip de linha.
- Malha: fd.RectangleMesh(Nx, Ny, Lx, Ly, quadrilateral=True).
  Marcadores de fronteira padrão do Firedrake para RectangleMesh:
    1 = x=0 (esquerda), 2 = x=Lx (direita)
    3 = y=0 (base),     4 = y=Ly (topo)
- Keff herda a unidade física atribuída a k_poro/k_solido (a
  homogeneização de Darcy é linear em K).
"""

import numpy as np
import firedrake as fd

__all__ = [
    "criar_malha",
    "build_permeability",
    "preparar_espaco_pressao",
    "resolver_keff",
]


def criar_malha(Nx, Ny, voxel_size_m):
    """Cria a malha física (RectangleMesh) a partir da resolução do void
    e do tamanho físico do voxel.

    Parameters
    ----------
    Nx, Ny : int
        Número de voxels/células em x e y.
    voxel_size_m : tuple(float, float)
        Tamanho físico de cada voxel em metros, (dx, dy).

    Returns
    -------
    malha, Lx, Ly
    """
    Lx = Nx * voxel_size_m[0]
    Ly = Ny * voxel_size_m[1]
    malha = fd.RectangleMesh(Nx, Ny, Lx, Ly, quadrilateral=True)
    return malha, Lx, Ly


def build_permeability(void_array, V_perm, Nx, Ny, Lx, Ly, k_solido=1e-10, k_poro=1.0):
    """Constrói um campo de permeabilidade DG0 a partir de uma microestrutura binária.

    Lx, Ly devem ser as mesmas dimensões físicas usadas para criar a malha
    associada a V_perm (ex.: via criar_malha). A malha é obtida de
    V_perm.mesh() -- não depende de nenhuma variável global `malha`.

    Parameters
    ----------
    void_array : array_like
        Array 2D booleano representando a microestrutura (True = poro, False = sólido).
    V_perm : firedrake.FunctionSpace
        Espaço de funções para a permeabilidade.
    Nx, Ny : int
        Número de voxels em x e y.
    Lx, Ly : float
        Dimensões físicas do domínio em x e y.
    k_solido : float, optional
        Valor da permeabilidade do material sólido (padrão: 1e-10).
    k_poro : float, optional
        Valor da permeabilidade do material poroso (padrão: 1.0).

    Returns
    -------
    K : firedrake.Function
        Campo de permeabilidade construído.
    """
    void_array = np.asarray(void_array, dtype=bool)
    K_numpy = np.where(void_array, k_poro, k_solido)

    malha = V_perm.mesh()
    K = fd.Function(V_perm, name="Permeabilidade")

    coords = fd.Function(fd.VectorFunctionSpace(malha, "DQ", 0))
    coords.interpolate(fd.SpatialCoordinate(malha))

    cx = coords.dat.data[:, 0]
    cy = coords.dat.data[:, 1]

    # Normaliza pelas dimensões FÍSICAS do domínio (Lx, Ly).
    col = np.clip((cx / Lx * Nx).astype(int), 0, Nx - 1)
    row = np.clip((cy / Ly * Ny).astype(int), 0, Ny - 1)
    row_flipped = (Ny - 1) - row  # ver docstring do módulo (convenção linha 0 = topo)

    K.dat.data[:] = K_numpy[row_flipped, col]
    return K


def preparar_espaco_pressao(malha):
    """Monta uma única vez o espaço de pressão + trial/test/normal para uma malha.
    Reutilizar isso entre muitas amostras (mesma malha, K diferente) evita
    reconstruir o FunctionSpace a cada iteração de um loop grande.
    
    Parameters
    ----------
    malha : firedrake.Mesh
        Malha sobre a qual o espaço de pressão será construído.
    returns
    -------
    V_p : firedrake.FunctionSpace
        Espaço de funções contínuo (CG1) para a pressão.
    u : firedrake.TrialFunction
        Função de teste para a pressão.
    v : firedrake.TestFunction
        Função de teste para a pressão.
    n : firedrake.FacetNormal
        Vetor normal às faces da malha.
        """
    V_p = fd.FunctionSpace(malha, "CG", 1)
    u = fd.TrialFunction(V_p)
    v = fd.TestFunction(V_p)
    n = fd.FacetNormal(malha)
    return V_p, u, v, n


def resolver_keff(malha, K, Lx, Ly, V_p=None, u=None, v=None, n=None,
                   pressao_entrada=1.0, pressao_saida=0.0,
                   retornar_pressoes=False,
                   solver_parameters=None):
    """Resolve Darcy nas direções x e y e retorna Keff_x, Keff_y (e,
    opcionalmente, os campos de pressão).

    Se V_p/u/v/n não forem passados, são construídos internamente
    (conveniente para testes avulsos). Em loops grandes, prefira
    construir uma vez com preparar_espaco_pressao(malha) e passar aqui,
    para não pagar o custo de recriar o FunctionSpace a cada amostra.

    Returns
    -------
    dict com chaves: "keff_x", "keff_y" e, se retornar_pressoes=True,
    também "p_x_data", "p_y_data" (arrays numpy dos graus de liberdade).
    """
    if V_p is None:
        V_p, u, v, n = preparar_espaco_pressao(malha)

    if solver_parameters is None:
        solver_parameters = {"ksp_type": "cg", "pc_type": "hypre"}

    dp = pressao_entrada - pressao_saida
    if dp == 0:
        raise ValueError("pressao_entrada e pressao_saida não podem ser iguais (dp=0).")

    comprimento_x, area_x = Lx, Ly
    comprimento_y, area_y = Ly, Lx

    a = fd.inner(K * fd.grad(u), fd.grad(v)) * fd.dx
    L = fd.Constant(0.0) * v * fd.dx

    # --- Direção X (marcadores 1=x0, 2=x1) ---
    p_x = fd.Function(V_p, name="Pressao_X")
    bc_x = [
        fd.DirichletBC(V_p, fd.Constant(pressao_entrada), 1),
        fd.DirichletBC(V_p, fd.Constant(pressao_saida), 2),
    ]
    fd.solve(a == L, p_x, bcs=bc_x, solver_parameters=solver_parameters)
    fluxo_x = fd.assemble(fd.dot(-K * fd.grad(p_x), n) * fd.ds(2))
    keff_x = abs(float(fluxo_x) * comprimento_x / (area_x * dp))

    # --- Direção Y (marcadores 3=y0, 4=y1) ---
    p_y = fd.Function(V_p, name="Pressao_Y")
    bc_y = [
        fd.DirichletBC(V_p, fd.Constant(pressao_entrada), 3),
        fd.DirichletBC(V_p, fd.Constant(pressao_saida), 4),
    ]
    fd.solve(a == L, p_y, bcs=bc_y, solver_parameters=solver_parameters)
    fluxo_y = fd.assemble(fd.dot(-K * fd.grad(p_y), n) * fd.ds(4))
    keff_y = abs(float(fluxo_y) * comprimento_y / (area_y * dp))

    saida = {"keff_x": keff_x, "keff_y": keff_y}
    if retornar_pressoes:
        saida["p_x_data"] = p_x.dat.data.copy()
        saida["p_y_data"] = p_y.dat.data.copy()
    return saida
