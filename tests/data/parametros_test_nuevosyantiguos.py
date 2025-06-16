test_cases_calcular_recursos_por_cno = [
    {
        "alfa": 1,
        "ponderar": True,
        "expect_ipo_ponderado": [17, 15, 2],
        "expect_ipo": [1.1, 1.2, 0.2],
        "expect_participacion_ipo": [17/34, 15/34, 2/34],
        "expect_recursosxcno": [50, 44.1, 5.9],
        "expect_cuposxcno": [30, 25, 10],
        "expect_n_programas": [2, 2, 1]
    },
    {
        "alfa": 2,
        "ponderar": True,
        "expect_ipo_ponderado": [9.7, 9, 0.4],
        "expect_ipo": [1.1, 1.2, 0.2],
        "expect_participacion_ipo": [9.7/19.1, 9/19.1, 0.4/19.1],
        "expect_recursosxcno": [50.8, 47.1, 2.1],
        "expect_cuposxcno": [30, 25, 10],
        "expect_n_programas": [2, 2, 1]
    }
]

ids_calcular_recursos_por_cno = [
    "alfa=1_ponderar=True",
    "alfa=2_ponderar=True"
]