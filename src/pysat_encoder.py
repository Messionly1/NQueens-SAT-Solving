import math
from pysat.card import CardEnc, EncType
from verify import verify_sat_model

PYSAT_ENCODINGS = {
    'binomial': EncType.pairwise,
    'sequential': EncType.seqcounter,
    'binary': EncType.bitwise,
    'commander': EncType.cardnetwrk,
    'product': EncType.mtotalizer,
}

PYSAT_ALL_ENCODINGS = {
    'pairwise': EncType.pairwise,
    'seqcounter': EncType.seqcounter,
    'bitwise': EncType.bitwise,
    'cardnetwrk': EncType.cardnetwrk,
    'mtotalizer': EncType.mtotalizer,
    'totalizer': EncType.totalizer,
    'kmtotalizer': EncType.kmtotalizer,
    'sortnetwrk': EncType.sortnetwrk,
    'ladder': EncType.ladder,
    'native': EncType.native,
}

class PySatNQueensEncoder:
    def __init__(self, n: int, encoding: str = 'sequential', top_id: int = 0):
        if encoding in PYSAT_ENCODINGS:
            self._enc_type = PYSAT_ENCODINGS[encoding]
        elif encoding in PYSAT_ALL_ENCODINGS and encoding != 'native':
            self._enc_type = PYSAT_ALL_ENCODINGS[encoding]
        else:
            raise ValueError('Unknown encoding: ' + str(encoding))
        self.n = n
        self.encoding = encoding
        self.top_id = top_id
        self.nvars = n * n

    def var(self, r: int, c: int) -> int:
        return r * self.n + c + 1

    def _amo(self, lits):
        if len(lits) <= 1:
            return [], self.top_id

        cnf = CardEnc.atmost(
            lits=lits,
            bound=1,
            encoding=self._enc_type,
            top_id=self.top_id,
        )
        return cnf.clauses, cnf.nv

    @staticmethod
    def _alo(lits):
        return [lits]

    def verify_solution(self, model, n: int) -> bool:
        return verify_sat_model(model, n)

    def generate_clauses(self):
        clauses = []
        n = self.n
        self.top_id = self.nvars

        for r in range(n):
            lits = [self.var(r, c) for c in range(n)]
            clauses.extend(self._alo(lits))
            amo, self.top_id = self._amo(lits)
            clauses.extend(amo)

        for c in range(n):
            lits = [self.var(r, c) for r in range(n)]
            amo, self.top_id = self._amo(lits)
            clauses.extend(amo)

        for d in range(-n + 1, n):
            lits = [self.var(r, r - d) for r in range(n) if 0 <= r - d < n]
            if len(lits) > 1:
                amo, self.top_id = self._amo(lits)
                clauses.extend(amo)

        for d in range(2 * n - 1):
            lits = [self.var(r, d - r) for r in range(n) if 0 <= d - r < n]
            if len(lits) > 1:
                amo, self.top_id = self._amo(lits)
                clauses.extend(amo)

        for c in range(math.ceil(n / 2), n):
            clauses.append([-self.var(0, c)])

        return clauses, self.top_id

if __name__ == '__main__':
    for name in ['binomial', 'sequential', 'binary', 'commander', 'product']:
        enc = PySatNQueensEncoder(8, encoding=name)
        clauses, nvars = enc.generate_clauses()
        print(name + ': ' + str(len(clauses)) + ' clauses, ' + str(nvars) + ' vars')
