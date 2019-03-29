r"""
DES

AUTHORS:

- Lukas Stennes (2019-03-29): initial version
"""

# ****************************************************************************
#       Copyright (C) 2013 Lukas Stennes <lukas.stennes@rub.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  https://www.gnu.org/licenses/
# ****************************************************************************
from sage.structure.sage_object import SageObject
from sage.modules.free_module_element import vector
from sage.rings.finite_rings.finite_field_constructor import GF


class DES(SageObject):
    r"""
    This class implements DES described in [TODO: ADD REF]_.
    """

    def __init__(self, rounds=None, keySchedule=False):
        r"""
        Construct an instance of DES.

        INPUT:

        - ``rounds``  -- integer (default: ``None``); the number of rounds. If
          ``None`` the number of rounds of the key schedule is used.

        - ``keySchedule`` -- (default: ``None``); the key schedule that will be
          used for encryption and decryption. If ``None`` the default DES key
          schedule is used.

        """
        if keySchedule is None:
            self._keySchedule = DES_KS()
        else:
            self._keySchedule = keySchedule
        if rounds is None:
            self._rounds = self._keySchedule._rounds
        elif rounds <= self._keySchedule._rounds:
            self._rounds = rounds
        else:
            raise ValueError('number of rounds must be less or equal to the '
                             'number of rounds of the key schedule')
        self._blocksize = 64

    def __call__(self, B, K, algorithm='encrypt'):
        r"""
        Apply DES encryption or decryption on ``B`` using the key ``K``.
        The flag ``algorithm`` controls what action is to be performed on
        ``B``.

        INPUT:

        - ``B`` -- integer or bit list-like; the plaintext or ciphertext

        - ``K`` -- integer or bit list-like; the key

        - ``algorithm`` -- string (default: ``'encrypt'``); a flag to signify
          whether encryption or decryption is to be applied to ``B``. The
          encryption flag is ``'encrypt'`` and the decryption flag is
          ``'decrypt'``

        OUTPUT:

        - The plaintext or ciphertext corresponding to ``B``, obtained using
          the key ``K``. If ``B`` is an integer the output will be too. If
          ``B`` is list-like the output will be a bit vector.
        """
        if algorithm == 'encrypt':
            return self.encrypt(B, K)
        elif algorithm == 'decrypt':
            return self.decrypt(B, K)
        else:
            raise ValueError('Algorithm must be \'encrypt\' or \'decrypt\' and'
                             ' not \'%s\'' % algorithm)

    def __eq__(self, other):
        r"""
        Compare ``self`` with ``other``.

        DES objects are the same if all attributes are the same.
        """
        if not isinstance(other, DES):
            return False
        else:
            return self.__dict__ == other.__dict__

    def __repr__(self):
        r"""
        A string representation of this DES.
        """
        raise NotImplementedError

    def encrypt(self, P, K):
        r"""
        Return the ciphertext corresponding to the plaintext ``P``,
        using DES encryption with key ``K``.
        """
        raise NotImplementedError

    def decrypt(self, C, K):
        r"""
        Return the plaintext corresponding to the ciphertext ``C``,
        using DES decryption with key ``K``.
        """
        raise NotImplementedError


class DES_KS(SageObject):
    r"""
    This class implements the DES key schedules described in [BKLPPRSV2007]_.
    """

    def __init__(self, rounds=16, master_key=None):
        r"""
        Construct an instance of DES_KS.
        """
        self._rounds = rounds
        self._master_key = master_key

    def __call__(self, K):
        r"""
        Return all round keys in a list.

        INPUT:

        - ``K`` -- integer or bit list-like; the key

        OUTPUT:

        - A list containing the round keys

        .. NOTE::

            If you want to use a DES_KS object as an iterable you have to
            pass a ``master_key`` value on initialisation. Otherwise you can
            omit ``master_key`` and pass a key when you call the object.
        """
        raise NotImplementedError

    def __eq__(self, other):
        r"""
        Compare ``self`` with ``other``.

        DES_KS objects are the same if all attributes are the same.
        """
        if not isinstance(other, DES_KS):
            return False
        else:
            return self.__dict__ == other.__dict__

    def __repr__(self):
        r"""
        A string representation of this DES_KS.
        """
        return ('Original DES key schedule with %s-bit keys and %s rounds'
                % (self._keysize, self._rounds))

    def __getitem__(self, r):
        r"""
        Computes the sub key for round ``r`` derived from initial master key.

        The key schedule object has to have been initialised with the
        `master_key` argument.

        INPUT:

        - ``r`` integer; the round for which the sub key is computed
        """
        if self._master_key is None:
            raise ValueError('Key not set during initialisation')
        return self(self._master_key)[r]

    def __iter__(self):
        r"""
        Iterate over the ``self._rounds + 1`` PRESENT round keys, derived from
        `master_key`

        EXAMPLES::

            sage: from sage.crypto.block_cipher.present import PRESENT_KS
            sage: K = [k for k in PRESENT_KS(master_key=0x0)]
            sage: K[0] == 0x0 # indirect doctest
            True
            sage: K[31] == 0x6dab31744f41d700 # indirect doctest
            True
        """
        if self._master_key is None:
            raise ValueError('Key not set during initialisation')
        return iter(self(self._master_key))

    def _pc1(self, key):
        r"""
        Compute Permuted Choice 1 of ``key``.
        """
        raise NotImplementedError

    def _pc2(self, key):
        r"""
        Compute Permuted Choice 2 of ``key``.
        """
        raise NotImplementedError

    def _left_shift(self, half, i):
        r"""
        Shift ``half`` one or two positions to the left depending on the
        iteration number ``i``.

        EXAMPLES::

            sage: from sage.crypto.block_cipher.des import DES_KS
            sage: ks = DES_KS()
            sage: bits = vector(GF(2), 6, [1,0,1,0,1,0])
            sage: ks._left_shift(bits, 1)
            (0, 1, 0, 1, 0, 1)
            sage: bits
            (1, 0, 1, 0, 1, 0)
            sage: ks._left_shift(bits, 3)
            (1, 0, 1, 0, 1, 0)
        """
        amount = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]
        return vector(GF(2),
                      list(half[amount[i-1]:]) + list(half[0:amount[i-1]]))
