import itertools
import unittest

from pycoin.coins.tx_utils import create_tx
from pycoin.ecdsa.secp256k1 import secp256k1_generator
from pycoin.solve.utils import build_hash160_lookup
from pycoin.symbols.btc import network


Tx = network.tx


class MultisigIndividualTest(unittest.TestCase):
    def multisig_M_of_N_individually(self, M, N):
        keys = [network.keys.private(secret_exponent=i) for i in range(1, N+2)]
        tx_in = Tx.TxIn.coinbase_tx_in(script=b'')
        script = network.contract.for_multisig(m=M, sec_keys=[key.sec() for key in keys[:N]])
        tx_out = Tx.TxOut(1000000, script)
        tx1 = Tx(version=1, txs_in=[tx_in], txs_out=[tx_out])
        for partial_key_list in itertools.permutations(keys[:N], M):
            tx2 = create_tx(tx1.tx_outs_as_spendable(), [keys[-1].address()])
            for key in partial_key_list:
                self.assertEqual(tx2.bad_solution_count(), 1)
                hash160_lookup = build_hash160_lookup([key.secret_exponent()], [secp256k1_generator])
                tx2.sign(hash160_lookup=hash160_lookup)
            self.assertEqual(tx2.bad_solution_count(), 0)

    def test_multisig_one_at_a_time(self):
        for N in range(1, 4):
            for M in range(1, N+1):
                self.multisig_M_of_N_individually(M, N)


if __name__ == "__main__":
    unittest.main()
