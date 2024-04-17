# Cubit - A Cube Pruning Decoder for Phrase-based Translation

Welcome! This page contains information about Cubit, an efficient Python implementation of phrase-based decoding, à la Pharaoh, but using Cube Pruning inspired by k-best parsing to accelerate the language model integration (hence the name "cubit"). Under typical parameter settings, it can achieve 10-30 fold relative speed up (at the same level of search errors) against conventional beam search, or an even bigger speed up at the same level of BLEU. It is described in Section 5.1 of the following paper:

* Liang Huang and David Chiang (2007). [Forest Rescoring: Faster Decoding with Integrated Language Models](https://aclanthology.org/P07-1019.pdf). In Proceedings of the ACL, Prague, Czech Rep.

Version 0.8 (only for referencial uses for implementation of cube pruning). Released Feb. 27, 2008.

The [manual](README) will contain a more detailed description of the adaptation of cube pruning to phrase-based decoding.

Related papers:

* David Chiang (2007). [Hierarchical Phrase-based Translation](https://aclanthology.org/J07-2003.pdf). Computational Linguistics, 33 (2).
* Liang Huang and David Chiang (2005). [Better k-best Parsing](https://aclanthology.org/W05-1506v2.pdf). In Proceedings of IWPT, Vancouver, B.C.
* Philipp Koehn (2004). [Pharaoh: A beam search decoder for phrase-based statistical machine translation models](https://www.cs.cornell.edu/courses/cs5740/2016sp/resources/pharaoh.pdf). In Proceedings of AMTA.

The name "cubit" is suggested by [Jonathan May](https://jonmay.github.io/webpage/).

[Liang Huang](https://web.engr.oregonstate.edu/~huanlian/)
