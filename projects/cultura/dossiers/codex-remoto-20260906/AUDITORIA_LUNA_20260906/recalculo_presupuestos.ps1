# Recalculo independiente de los CSV auditados el 2026-09-06.
# No modifica los originales remotos.
$presupuestos = @{
  'Ama Amoedo (USD)' = @(
    @{c='Personal'; q=6; p=900}, @{c='Personal'; q=3; p=800}, @{c='Personal'; q=1; p=900},
    @{c='Operacion'; q=12; p=25}, @{c='Operacion'; q=12; p=12}, @{c='Operacion'; q=1; p=200},
    @{c='Operacion'; q=1; p=500}, @{c='Operacion'; q=1; p=150}
  )
  'Creacion (CLP)' = @(
    @{c='Personal'; q=1; p=7000000}, @{c='Personal'; q=5; p=450000}, @{c='Personal'; q=2; p=500000}, @{c='Personal'; q=3; p=400000},
    @{c='Operacion'; q=1; p=1000000}, @{c='Operacion'; q=1; p=600000}, @{c='Operacion'; q=300; p=1200}, @{c='Operacion'; q=1; p=500000}, @{c='Operacion'; q=2; p=140000}, @{c='Operacion'; q=12; p=30000},
    @{c='Inversion'; q=1; p=1300000}, @{c='Inversion'; q=1; p=900000}, @{c='Inversion'; q=1; p=650000}, @{c='Inversion'; q=1; p=280000},
    @{c='Imprevistos'; q=1; p=320000}
  )
  'Formativas (CLP)' = @(
    @{c='Personal'; q=1; p=5400000}, @{c='Personal'; q=8; p=180000}, @{c='Personal'; q=8; p=300000}, @{c='Personal'; q=1; p=700000},
    @{c='Operacion'; q=8; p=180000}, @{c='Operacion'; q=16; p=45000}, @{c='Operacion'; q=16; p=25000}, @{c='Operacion'; q=128; p=4500}, @{c='Operacion'; q=1; p=450000}, @{c='Operacion'; q=1; p=400000}, @{c='Operacion'; q=1; p=350000}, @{c='Operacion'; q=12; p=30000},
    @{c='Imprevistos'; q=1; p=264000}
  )
}

foreach ($nombre in $presupuestos.Keys) {
  $filas = $presupuestos[$nombre]
  $total = ($filas | ForEach-Object { $_.q * $_.p } | Measure-Object -Sum).Sum
  $porCategoria = $filas | Group-Object { $_['c'] } | ForEach-Object {
    $categoria = $_.Name
    $s = ($_.Group | ForEach-Object { $_.q * $_.p } | Measure-Object -Sum).Sum
    "  ${categoria}: $s"
  }
  "[$nombre]"
  $porCategoria
  "  TOTAL: $total"
}
