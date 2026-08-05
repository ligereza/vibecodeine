# pycount.py
import sys
from pathlib import Path

def count_file(path: str) -> tuple[int, int, int]:
    """Cuenta líneas de código, comentarios y en blanco en *path*."""
    code = comment = blank = 0
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            blank += 1
        elif stripped.startswith("#"):
            comment += 1
        else:
            code += 1
    return code, comment, blank

def _cli():
    if len(sys.argv) != 2:
        sys.stderr.write("Uso: python -m pycount <ruta>\n")
        sys.exit(1)
    counts = count_file(sys.argv[1])
    print(*counts)

if __name__ == "__main__":
    # ---------- TEST 1 ----------
    txt1 = """# Comentario inicial

def foo():    # función simple
    pass      # nada
# Otro comentario
"""
    p1 = Path("tmp_test1.py")
    p1.write_text(txt1, encoding="utf-8")
    assert count_file(str(p1)) == (2, 2, 2)
    p1.unlink()

    # ---------- TEST 2 ----------
    txt2 = """# primer comentario

# segundo comentario

"""
    p2 = Path("tmp_test2.py")
    p2.write_text(txt2, encoding="utf-8")
    assert count_file(str(p2)) == (0, 2, 3)
    p2.unlink()

    # ---------- TEST 3 ----------
    txt3 = """a=1
b=2
c=3"""
    p3 = Path("tmp_test3.py")
    p3.write_text(txt3, encoding="utf-8")
    assert count_file(str(p3)) == (3, 0, 0)
    p3.unlink()

    # Si se proporciona un argumento, ejecutar CLI; si no, mostrar éxito de pruebas
    if len(sys.argv) == 1:
        print("PRUEBAS OK")
    else:
        _cli()
