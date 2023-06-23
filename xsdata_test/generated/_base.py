from dataclasses import fields


class MyMixin:
    def __repr__(self) -> str:
        name = self.__class__.__qualname__
        reprs = []
        for f in fields(self):
            val = getattr(self, f.name)
            if val is not None:
                reprs.append(f"{f.name}={val!r}")
        return f"{name}({', '.join(reprs)})"
