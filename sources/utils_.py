from pprint import pprint

import pytz
from datetime import datetime
from PIL import Image
import io
import steembase

import hashlib
import logging
import struct
import time
import array
import sys
from binascii import hexlify, unhexlify
from collections import OrderedDict
from datetime import datetime

import ecdsa

from steem.utils import compat_bytes, compat_chr
from steembase.account import PrivateKey, PublicKey
from steembase.chains import known_chains
from steembase.operations import Operation, GrapheneObject, isArgsThisClass
from steembase.types import (
    Array,
    Set,
    Signature,
    PointInTime,
    Uint16,
    Uint32,
)

try:
    import secp256k1

    USE_SECP256K1 = True
    #log.debug("Loaded secp256k1 binding.")
except:  # noqa FIXME(sneak)
    USE_SECP256K1 = False
    #log.debug("To speed up transactions signing install \n"
    #          "    pip install secp256k1")


class SignProcess(steembase.transactions.SignedTransaction):

    def __init__(self, steemd_instance, *args, **kwargs):
        # super 인자에 아무것도 안 적어주면 디폴트로 현 클래스명이 들어감
        self.steemd = steemd_instance
        super(SignProcess, self).__init__(*args, **kwargs)

    def deriveDigest(self, message, chain=None):
        # Do not serialize signatures
        sigs = self.data["signatures"]
        self.data["signatures"] = []

        # Get message to sign
        self.message = message
        self.digest = hashlib.sha256(message).digest()
        # restore signatures
        self.data["signatures"] = sigs

        # test ----
        chain_params = self.getChainParams(chain)
        pprint(chain_params)
        # Chain ID
        self.chainid = chain_params["chain_id"]
        message2 = unhexlify(self.chainid) + compat_bytes(self)
        message2 = hashlib.sha256(message2).digest()
        print(type(message2), message2)
        print(type(self.digest), self.digest)

    def sign(self, message, wifkeys):
        """ Sign the transaction with the provided private keys.
            :param list wifkeys: Array of wif keys
            :param str chain: identifier for the chain
        """

        self.deriveDigest(message, chain=self.steemd.chain_params)

        # Get Unique private keys
        self.privkeys = []
        [
            self.privkeys.append(item) for item in wifkeys
            if item not in self.privkeys
        ]

        # Sign the message with every private key given!
        sigs = []
        for wif in self.privkeys:
            # print(wif)
            print(self.digest)
            p = compat_bytes(PrivateKey(wif))
            i = 0
            if USE_SECP256K1:
                ndata = secp256k1.ffi.new("const int *ndata")
                ndata[0] = 0
                while True:
                    ndata[0] += 1
                    privkey = secp256k1.PrivateKey(p, raw=True)
                    sig = secp256k1.ffi.new(
                        'secp256k1_ecdsa_recoverable_signature *')
                    signed = secp256k1.lib.secp256k1_ecdsa_sign_recoverable(
                        privkey.ctx, sig, self.digest, privkey.private_key,
                        secp256k1.ffi.NULL, ndata)
                    assert signed == 1
                    signature, i = privkey.ecdsa_recoverable_serialize(sig)
                    if self._is_canonical(signature):
                        i += 4  # compressed
                        i += 27  # compact
                        break
            else:
                cnt = 0
                sk = ecdsa.SigningKey.from_string(p, curve=ecdsa.SECP256k1)
                while 1:
                    cnt += 1
                    if not cnt % 20:
                        print("Still searching for a canonical signature. "
                                 "Tried %d times already!" % cnt)

                    # Deterministic k
                    k = ecdsa.rfc6979.generate_k(
                        sk.curve.generator.order(),
                        sk.privkey.secret_multiplier,
                        hashlib.sha256,
                        hashlib.sha256(
                            self.digest + struct.pack("d", time.time(
                            ))  # use the local time to randomize the signature
                        ).digest())

                    # Sign message
                    #
                    sigder = sk.sign_digest(
                        self.digest, sigencode=ecdsa.util.sigencode_der, k=k)

                    # Reformating of signature
                    #
                    r, s = ecdsa.util.sigdecode_der(sigder,
                                                    sk.curve.generator.order())
                    signature = ecdsa.util.sigencode_string(
                        r, s, sk.curve.generator.order())

                    # This line allows us to convert a 2.7 byte array(which is just binary) to an array of byte values.
                    # We can then use the elements in sigder as integers, as in the following two lines.
                    sigder = array.array('B', sigder)

                    # Make sure signature is canonical!
                    #
                    lenR = sigder[3]
                    lenS = sigder[5 + lenR]
                    if lenR == 32 and lenS == 32:
                        # Derive the recovery parameter
                        #
                        i = self.recoverPubkeyParameter(
                            self.digest, signature, sk.get_verifying_key())
                        i += 4  # compressed
                        i += 27  # compact
                        break

            # pack signature
            #
            sigstr = struct.pack("<B", i)
            sigstr += signature

            sigs.append(Signature(sigstr))

        self.data["signatures"] = Array(sigs)
        return self

    def verify(self, pubkeys=[] , chain=None):
        '''
        if not chain:
            raise ValueError("Chain needs to be provided!")
        chain_params = self.getChainParams(chain)
        self.deriveDigest(chain)
        '''

        self.deriveDigest(self.message, chain=self.steemd.chain_params)

        signatures = self.data["signatures"].data
        print('signatures in verify: ',signatures[0])
        pubKeysFound = []

        for signature in signatures:
            sig = compat_bytes(signature)[1:]
            if sys.version >= '3.0':
                recoverParameter = (compat_bytes(signature)[0]) - 4 - 27  # recover parameter only
            else:
                recoverParameter = ord((compat_bytes(signature)[0])) - 4 - 27

            if USE_SECP256K1:
                ALL_FLAGS = secp256k1.lib.SECP256K1_CONTEXT_VERIFY | \
                            secp256k1.lib.SECP256K1_CONTEXT_SIGN
                # Placeholder
                pub = secp256k1.PublicKey(flags=ALL_FLAGS)
                # Recover raw signature
                sig = pub.ecdsa_recoverable_deserialize(sig, recoverParameter)
                # Recover PublicKey
                verifyPub = secp256k1.PublicKey(
                    pub.ecdsa_recover(compat_bytes(self.message), sig))
                # Convert recoverable sig to normal sig
                normalSig = verifyPub.ecdsa_recoverable_convert(sig)
                # Verify
                verifyPub.ecdsa_verify(compat_bytes(self.message), normalSig)
                phex = hexlify(
                    verifyPub.serialize(compressed=True)).decode('ascii')
                pubKeysFound.append(phex)
            else:
                p = self.recover_public_key(self.digest, sig, recoverParameter)
                # Will throw an exception of not valid
                p.verify_digest(
                    sig, self.digest, sigdecode=ecdsa.util.sigdecode_string)
                phex = hexlify(self.compressedPubkey(p)).decode('ascii')
                pubKeysFound.append(phex)

        for pubkey in pubkeys:
            if not isinstance(pubkey, PublicKey):
                raise Exception("Pubkeys must be array of 'PublicKey'")

            k = pubkey.unCompressed()[2:]
            if k not in pubKeysFound and repr(pubkey) not in pubKeysFound:
                k = PublicKey(PublicKey(k).compressed())
                # f = format(k, chain_params["prefix"])
                #f = format(k, )
                #raise Exception("Signature for %s missing!" % f)
        return pubKeysFound

# tmp
def get_timestamp():
    KST = pytz.timezone('Asia/Seoul')
    return datetime.utcnow().replace(tzinfo=KST).strftime("%Y-%m-%dT%H:%M:%S%z")


def img2byte(img_path=None):
    if not img_path:
        img_path = "./data/lotte.png"
    img = Image.open(img_path)
    bytearr = io.BytesIO()
    img.save(bytearr, format="png")
    return bytearr.getvalue()
