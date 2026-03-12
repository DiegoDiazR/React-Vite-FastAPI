"""
API 581 COF Level 1
Section 4.2: Release Hole Size Selection

Incluye:
- Table 4.4: Release hole sizes & diameters (dn) + cálculo de área.
- Part 2, Table 3.1: Suggested Component GFFs (failures/yr).
- Regla 2025: Si D < dn_generico, entonces dn = D.

Unidades:
- D y dn en pulgadas (in)
- áreas en in^2
- GFF en failures/yr
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import pi
from typing import Dict, Iterable, Tuple


# ---------------------------------------------------------------------
# Table 4.4 — Release Hole Sizes and Areas
# ---------------------------------------------------------------------

class ReleaseHoleSize(str, Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    RUPTURE = "rupture"


@dataclass(frozen=True)
class ReleaseHole:
    """
    Un evento discreto de liberación (n = 1..4).
    """
    hole_number: int
    hole_size: ReleaseHoleSize
    range_of_hole_diameters_in: str
    dn_in: float
    area_in2: float


# Metadatos para etiquetas (Los valores numéricos se calculan dinámicamente según D)
_TABLE_4_4_META = {
    1: (ReleaseHoleSize.SMALL,   "0 to 1/4"),
    2: (ReleaseHoleSize.MEDIUM,  "> 1/4 to 2"),
    3: (ReleaseHoleSize.LARGE,   "> 2 to 6"),
    4: (ReleaseHoleSize.RUPTURE, "> 6"),
}


def compute_release_holes(D_in: float) -> Dict[int, ReleaseHole]:
    """
    Calcula los diámetros de los 4 tamaños de agujero según API 581 Table 4.4.
    
    CRITERIO (API 581 4.2.2.a):
    Determine the release hole size diameters, dn. If D < dn, dn = D.
    
    Esto asegura que nunca retornemos 0.0 si el equipo existe (D > 0).
    """
    if D_in <= 0:
        raise ValueError("D_in debe ser > 0")

    # Tamaños genéricos estándar (pulgadas)
    STD_SMALL = 0.25
    STD_MEDIUM = 1.0
    STD_LARGE = 4.0
    STD_RUPTURE_LIMIT = 16.0

    holes: Dict[int, ReleaseHole] = {}

    # 1. SMALL (n=1)
    # Generic: 0.25". Regla: min(D, 0.25)
    dn1 = min(D_in, STD_SMALL)

    # 2. MEDIUM (n=2)
    # Generic: 1.0". Regla: min(D, 1.0)
    dn2 = min(D_in, STD_MEDIUM)

    # 3. LARGE (n=3)
    # Generic: 4.0". Regla: min(D, 4.0)
    dn3 = min(D_in, STD_LARGE)

    # 4. RUPTURE (n=4)
    # Generic: D (max 16"). Regla: min(D, 16.0)
    dn4 = min(D_in, STD_RUPTURE_LIMIT)

    # Mapeo de resultados
    dn_results = {1: dn1, 2: dn2, 3: dn3, 4: dn4}

    for n, (size, rng) in _TABLE_4_4_META.items():
        dn = dn_results[n]
        holes[n] = ReleaseHole(
            hole_number=n,
            hole_size=size,
            range_of_hole_diameters_in=rng,
            dn_in=float(dn),
            area_in2=float((pi / 4.0) * dn**2)
        )

    return holes


# ---------------------------------------------------------------------
# Part 2 — Table 3.1 Suggested Component GFFs (failures/yr)
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class GFFRow:
    component_type: str
    gff_small: float
    gff_medium: float
    gff_large: float
    gff_rupture: float
    gff_total: float


def _norm_component_type(s: str) -> str:
    return " ".join(s.strip().upper().split())


def _expand_aliases(keys: Iterable[str]) -> Tuple[str, ...]:
    return tuple(_norm_component_type(k) for k in keys)


_TABLE_3_1: Dict[str, GFFRow] = {}


def _register_gff(
    component_types: Iterable[str],
    small: float,
    medium: float,
    large: float,
    rupture: float,
    total: float,
) -> None:
    for ct in _expand_aliases(component_types):
        _TABLE_3_1[ct] = GFFRow(
            component_type=ct,
            gff_small=float(small),
            gff_medium=float(medium),
            gff_large=float(large),
            gff_rupture=float(rupture),
            gff_total=float(total),
        )


# --- DATA: API 581 Part 2 Table 3.1 ---

# Compressor
_register_gff(["COMPC"], 8.00e-06, 2.00e-05, 2.00e-06, 0.00e00, 3.00e-05)
_register_gff(["COMPR"], 8.00e-06, 2.00e-05, 2.00e-06, 6.00e-07, 3.06e-05)

# Heat exchanger
_register_gff(["HEXSS", "HEXTS"], 8.00e-06, 2.00e-05, 2.00e-06, 6.00e-07, 3.06e-05)

# Pipe
# Note: For small pipes (PIPE-1, PIPE-2), Medium/Large GFF is 0.0. 
# This correctly handles risk: even if we calculate a 'dn' for Medium, GFF=0 nullifies it.
_register_gff(["PIPE-1", "PIPE-2"], 2.80e-05, 0.00e00, 0.00e00, 2.60e-06, 3.06e-05)
_register_gff(["PIPE-4", "PIPE-6"], 8.00e-06, 2.00e-05, 0.00e00, 2.60e-06, 3.06e-05)
_register_gff(
    ["PIPE-8", "PIPE-10", "PIPE-12", "PIPE-16", "PIPEGT16"],
    8.00e-06, 2.00e-05, 2.00e-06, 6.00e-07, 3.06e-05
)

# Pump
_register_gff(["PUMP2S", "PUMPR", "PUMP1S"], 8.00e-06, 2.00e-05, 2.00e-06, 6.00e-07, 3.06e-05)

# Tank
_register_gff(["TANKBOTTOM"],   7.20e-04, 0.00e00, 0.00e00, 2.00e-06, 7.22e-04)
_register_gff(["TANKBOTEDGE"],  7.20e-04, 0.00e00, 0.00e00, 2.00e-06, 7.22e-04)
_register_gff(["COURSE-1-10"],  7.00e-05, 2.50e-05, 5.00e-06, 1.00e-07, 1.00e-04)

# FinFan
_register_gff(["FINFAN TUBES", "FINFAN HEADER"], 8.00e-06, 2.00e-05, 2.00e-06, 6.00e-07, 3.06e-05)

# Vessel
_register_gff(
    ["KODRUM", "COLBTM", "FILTER", "DRUM", "REACTOR", "COLTOP", "COLMID"],
    8.00e-06, 2.00e-05, 2.00e-06, 6.00e-07, 3.06e-05
)


def get_gff_row(component_type: str) -> GFFRow:
    key = _norm_component_type(component_type)
    if key not in _TABLE_3_1:
        available = ", ".join(sorted(_TABLE_3_1.keys()))
        raise KeyError(
            f"Unknown component_type='{component_type}'. "
            f"Expected one of: {available}"
        )
    return _TABLE_3_1[key]


def gff_by_hole_size(component_type: str) -> Dict[ReleaseHoleSize, float]:
    row = get_gff_row(component_type)
    return {
        ReleaseHoleSize.SMALL: row.gff_small,
        ReleaseHoleSize.MEDIUM: row.gff_medium,
        ReleaseHoleSize.LARGE: row.gff_large,
        ReleaseHoleSize.RUPTURE: row.gff_rupture,
    }


def gff_total(component_type: str, validate_sum: bool = True) -> float:
    row = get_gff_row(component_type)
    if validate_sum:
        s = row.gff_small + row.gff_medium + row.gff_large + row.gff_rupture
        if abs(s - row.gff_total) > 1e-10:
            pass # Logging point
    return float(row.gff_total)


# ---------------------------------------------------------------------
# Resultado integrado
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class ReleaseHoleSizeResult:
    D_in: float
    component_type: str
    holes: Dict[int, ReleaseHole]
    dn_in: Dict[ReleaseHoleSize, float]
    gff: Dict[ReleaseHoleSize, float]
    gff_total: float

def compute_cof_4_2_release_hole_size(component_type: str, D_in: float) -> ReleaseHoleSizeResult:
    """
    Ejecuta Paso 4.2.
    """
    # 1. Obtenemos los objetos de los huecos (dn calculado con min(D, std))
    holes_map = compute_release_holes(D_in=D_in)
    
    # 2. Obtenemos GFF
    gff_map = gff_by_hole_size(component_type=component_type)
    total_gff = gff_total(component_type=component_type, validate_sum=True)
    
    # 3. Resumen
    dn_summary = {
        h.hole_size: h.dn_in for h in holes_map.values()
    }

    return ReleaseHoleSizeResult(
        D_in=float(D_in),
        component_type=component_type.upper(),
        holes=holes_map,
        dn_in=dn_summary,
        gff=gff_map,
        gff_total=float(total_gff)
    )


# # app/calculations/cof_4_2_release_hole_size.py
# """
# API 581 COF Level 1
# Section 4.2: Release Hole Size Selection

# Incluye:
# - Table 4.4: Release hole sizes & diameters (dn) + cálculo de área.
# - Part 2, Table 3.1: Suggested Component GFFs (failures/yr) para cada tamaño de hueco.
# - Utilidades para calcular dn y gff_n por componente y tamaño.
# - Helper para conectar 4.2 -> 4.3 (hole_diameters_by_size)

# Unidades:
# - D y dn en pulgadas (in)
# - áreas en in^2 (solo informativas; 4.3 usa área en m^2)
# - GFF en failures/yr
# """

# from __future__ import annotations

# from dataclasses import dataclass
# from enum import Enum
# from math import pi
# from typing import Dict, Iterable, Tuple


# # ---------------------------------------------------------------------
# # Table 4.4 — Release Hole Sizes and Areas Used in Level 1 and 2 COF
# # ---------------------------------------------------------------------

# class ReleaseHoleSize(str, Enum):
#     SMALL = "small"
#     MEDIUM = "medium"
#     LARGE = "large"
#     RUPTURE = "rupture"


# @dataclass(frozen=True)
# class ReleaseHole:
#     """
#     Un evento discreto de liberación (n = 1..4) según API 581 Table 4.4.
#     """
#     hole_number: int
#     hole_size: ReleaseHoleSize
#     range_of_hole_diameters_in: str
#     dn_in: float
#     area_in2: float


# # Tabla 4.4 "completa" en forma programática (reglas de dn)
# # NOTE (API 581): If D < dn, set dn = D (aplica a TODOS los n, incluido small).
# #
# # n=1 Small:   dn_base = 0.25
# # n=2 Medium:  dn_base = 1.0
# # n=3 Large:   dn_base = 4.0
# # n=4 Rupture: dn_base = 16.0
# #
# # Implementación: dn = min(D, dn_base) para cada n.
# _TABLE_4_4_META = {
#     1: (ReleaseHoleSize.SMALL,   "0 to 1/4",     0.25),
#     2: (ReleaseHoleSize.MEDIUM,  "> 1/4 to 2",   1.00),
#     3: (ReleaseHoleSize.LARGE,   "> 2 to 6",     4.00),
#     4: (ReleaseHoleSize.RUPTURE, "> 6",         16),
# }


# def _area_from_diameter_in(d_in: float) -> float:
#     if d_in < 0:
#         raise ValueError("Diameter must be non-negative.")
#     return (pi / 4.0) * d_in * d_in


# def compute_release_holes(D_in: float) -> Dict[int, ReleaseHole]:
#     if D_in <= 0:
#         raise ValueError("D_in debe ser > 0")

#     # Umbrales de tu hoja 'Tablas'
#     I39_SMALL = 0.25
#     I40_MEDIUM = 1.0
#     I41_LARGE = 4.0
#     I42_RUPTURE_LIMIT = 16.0

#     holes: Dict[int, ReleaseHole] = {}

#     # 1. SMALL: Siempre 0.25 (Tablas!$I$39)
#     dn1 = I39_SMALL

#     # 2. MEDIUM: SI(D10 >= 1.0; 1.0; 0)
#     dn2 = I40_MEDIUM if D_in >= I40_MEDIUM else 0.0

#     # 3. LARGE: SI(D10 >= 4.0; 4.0; 0)
#     dn3 = I41_LARGE if D_in >= I41_LARGE else 0.0

#     # 4. RUPTURE: SI(D10 > 4.0; SI(D10 >= 16; 16; D10); 0)
#     if D_in > I41_LARGE:
#         dn4 = min(D_in, I42_RUPTURE_LIMIT)
#     else:
#         dn4 = 0.0

#     # Mapeo de resultados para construir los objetos
#     dn_results = {1: dn1, 2: dn2, 3: dn3, 4: dn4}

#     for n, (size, rng, _) in _TABLE_4_4_META.items():
#         dn = dn_results[n]
#         holes[n] = ReleaseHole(
#             hole_number=n,
#             hole_size=size,
#             range_of_hole_diameters_in=rng,
#             dn_in=float(dn),
#             area_in2=float((pi / 4.0) * dn**2) if dn > 0 else 0.0,
#         )

#     return holes

# # ---------------------------------------------------------------------
# # Part 2 — Table 3.1 Suggested Component GFFs (failures/yr)
# # ---------------------------------------------------------------------

# @dataclass(frozen=True)
# class GFFRow:
#     """
#     Fila de GFFs por tipo de componente (API 581 Part 2 Table 3.1).
#     """
#     component_type: str
#     gff_small: float
#     gff_medium: float
#     gff_large: float
#     gff_rupture: float
#     gff_total: float


# def _norm_component_type(s: str) -> str:
#     """
#     Normaliza para buscar en tabla:
#     - strip
#     - uppercase
#     - colapsa espacios
#     """
#     return " ".join(s.strip().upper().split())


# def _expand_aliases(keys: Iterable[str]) -> Tuple[str, ...]:
#     """
#     Para permitir que un mismo row cubra múltiples component_type.
#     """
#     return tuple(_norm_component_type(k) for k in keys)


# _TABLE_3_1: Dict[str, GFFRow] = {}


# def _register_gff(
#     component_types: Iterable[str],
#     small: float,
#     medium: float,
#     large: float,
#     rupture: float,
#     total: float,
# ) -> None:
#     """
#     Registra un row para uno o varios component_types.
#     """
#     for ct in _expand_aliases(component_types):
#         _TABLE_3_1[ct] = GFFRow(
#             component_type=ct,
#             gff_small=float(small),
#             gff_medium=float(medium),
#             gff_large=float(large),
#             gff_rupture=float(rupture),
#             gff_total=float(total),
#         )


# # ---------------------------
# # Table 3.1 (según tus capturas)
# # ---------------------------

# # --- Compressor ---
# _register_gff(["COMPC"], 8.00e-06, 2.00e-05, 2.00e-06, 0.00e00, 3.00e-05)
# _register_gff(["COMPR"], 8.00e-06, 2.00e-05, 2.00e-06, 6.00e-07, 3.06e-05)

# # --- Heat exchanger ---
# _register_gff(["HEXSS", "HEXTS"], 8.00e-06, 2.00e-05, 2.00e-06, 6.00e-07, 3.06e-05)

# # --- Pipe ---
# _register_gff(["PIPE-1", "PIPE-2"], 2.80e-05, 0.00e00, 0.00e00, 2.60e-06, 3.06e-05)
# _register_gff(["PIPE-4", "PIPE-6"], 8.00e-06, 2.00e-05, 0.00e00, 2.60e-06, 3.06e-05)
# _register_gff(
#     ["PIPE-8", "PIPE-10", "PIPE-12", "PIPE-16", "PIPEGT16"],
#     8.00e-06, 2.00e-05, 2.00e-06, 6.00e-07, 3.06e-05
# )

# # --- Pump ---
# _register_gff(["PUMP2S", "PUMPR", "PUMP1S"], 8.00e-06, 2.00e-05, 2.00e-06, 6.00e-07, 3.06e-05)

# # --- Tank ---
# _register_gff(["TANKBOTTOM"],   7.20e-04, 0.00e00, 0.00e00, 2.00e-06, 7.22e-04)
# _register_gff(["TANKBOTEDGE"],  7.20e-04, 0.00e00, 0.00e00, 2.00e-06, 7.22e-04)
# _register_gff(["COURSE-1-10"],  7.00e-05, 2.50e-05, 5.00e-06, 1.00e-07, 1.00e-04)

# # --- FinFan ---
# _register_gff(["FINFAN TUBES", "FINFAN HEADER"], 8.00e-06, 2.00e-05, 2.00e-06, 6.00e-07, 3.06e-05)

# # --- Vessel ---
# _register_gff(
#     ["KODRUM", "COLBTM", "FILTER", "DRUM", "REACTOR", "COLTOP", "COLMID"],
#     8.00e-06, 2.00e-05, 2.00e-06, 6.00e-07, 3.06e-05
# )


# def get_gff_row(component_type: str) -> GFFRow:
#     """
#     Step 2.2 — Determine gff_n for the n-th release hole size
#     from Part 2 Table 3.1 (generic failure frequency).

#     component_type debe venir como los códigos de la tabla:
#     COMPC, COMPR, HEXSS, HEXTS, PIPE-1, PIPE-2, PIPE-4, PIPE-6, PIPE-8, PIPE-10,
#     PIPE-12, PIPE-16, PIPEGT16, PUMP2S, PUMPR, PUMP1S, TANKBOTTOM, TANKBOTEDGE,
#     COURSE-1-10, FINFAN TUBES, FINFAN HEADER, KODRUM, COLBTM, FILTER, DRUM, REACTOR,
#     COLTOP, COLMID
#     """
#     key = _norm_component_type(component_type)
#     if key not in _TABLE_3_1:
#         available = ", ".join(sorted(_TABLE_3_1.keys()))
#         raise KeyError(
#             f"Unknown component_type='{component_type}'. "
#             f"Expected one of: {available}"
#         )
#     return _TABLE_3_1[key]


# def gff_by_hole_size(component_type: str) -> Dict[ReleaseHoleSize, float]:
#     """
#     Retorna gff_n por tamaño de hueco (small/medium/large/rupture).
#     """
#     row = get_gff_row(component_type)
#     return {
#         ReleaseHoleSize.SMALL: row.gff_small,
#         ReleaseHoleSize.MEDIUM: row.gff_medium,
#         ReleaseHoleSize.LARGE: row.gff_large,
#         ReleaseHoleSize.RUPTURE: row.gff_rupture,
#     }




# def gff_total(component_type: str, validate_sum: bool = True) -> float:
#     """
#     Ecuación (3.2): gff_total = sum_{n=1..4} gff_n
#     La tabla también trae gff_total.

#     - Por defecto retorna el gff_total de tabla.
#     - Opcionalmente valida consistencia contra la suma (validate_sum=True).
#     """
#     row = get_gff_row(component_type)

#     if validate_sum:
#         s = row.gff_small + row.gff_medium + row.gff_large + row.gff_rupture
#         # si hay una diferencia por redondeo, no fallamos duro, pero te dejamos listo para logging
#         if abs(s - row.gff_total) > 1e-10:
#             # aquí podrías usar logging.warning(...)
#             pass

#     return float(row.gff_total)


# # ---------------------------------------------------------------------
# # Resultado integrado para 4.2
# # ---------------------------------------------------------------------

# @dataclass(frozen=True)
# class ReleaseHoleSizeResult:
#     """
#     Resultado integrado para 4.2:
#     - holes: Objetos completos (dn, área, rango)
#     - dn_in: Resumen de diámetros calculados {"small": 0.25, ...}
#     - gff: Frecuencias por tamaño {"small": 8e-6, ...}
#     - gff_total: Sumatoria total de GFF
#     """
#     D_in: float
#     component_type: str
#     holes: Dict[int, ReleaseHole]
#     dn_in: Dict[ReleaseHoleSize, float]  # Resumen explícito solicitado
#     gff: Dict[ReleaseHoleSize, float]
#     gff_total: float

# def compute_cof_4_2_release_hole_size(component_type: str, D_in: float) -> ReleaseHoleSizeResult:
#     """
#     Implementa el flujo de 4.2:
#     - Step 2.1: dn y áreas (Table 4.4) con lógica condicional de Excel
#     - Step 2.2: gff_n y gff_total (Part 2 Table 3.1)
#     """
#     # 1. Obtenemos los objetos de los huecos (incluye dn y área)
#     holes_map = compute_release_holes(D_in=D_in)
    
#     # 2. Obtenemos las frecuencias GFF de la tabla
#     gff_map = gff_by_hole_size(component_type=component_type)
#     total_gff = gff_total(component_type=component_type, validate_sum=True)
    
#     # 3. Extraemos los dn calculados para el resumen explícito
#     # Mapeamos n (1,2,3,4) a su tamaño correspondiente (small, medium, etc.)
#     dn_summary = {
#         h.hole_size: h.dn_in for h in holes_map.values()
#     }

#     return ReleaseHoleSizeResult(
#         D_in=float(D_in),
#         component_type=component_type.upper(),
#         holes=holes_map,
#         dn_in=dn_summary,
#         gff=gff_map,
#         gff_total=float(total_gff)
#     )
