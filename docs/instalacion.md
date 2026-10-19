# Instalación

## Requisitos

- Python 3.10 o superior.
- Una cuenta de PagoTIC con credenciales de API (`client_id`,
  `client_secret`, usuario y contraseña).

## pip

```bash
pip install pagotic-sdk
```

## pipx

Para instalarlo en un entorno aislado:

```bash
pipx install pagotic-sdk
```

## Poetry

```bash
poetry add pagotic-sdk
```

## Extra de QR

La generación local de códigos QR usa [`segno`](https://github.com/heuer/segno)
y es opcional:

```bash
pip install "pagotic-sdk[qr]"
pipx install "pagotic-sdk[qr]"
poetry add "pagotic-sdk[qr]"
```

## Desde el repositorio

```bash
git clone https://github.com/Alitux/pagotic-sdk.git
cd pagotic-sdk
poetry install --with docs
```

También podés instalarlo como dependencia directa:

```bash
pip install "pagotic-sdk @ git+https://github.com/Alitux/pagotic-sdk.git"
```

## Verificar la instalación

```python
import pagotic

print(pagotic.__version__)
```

El nombre de distribución es `pagotic-sdk`, pero el paquete se importa como
`pagotic`.
