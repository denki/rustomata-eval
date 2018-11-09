__author__ = 'kilian'

from .general_hybrid_tree import HybridTree, join_spans
from .monadic_tokens import ConstituentTerminal, ConstituentCategory



class ConstituentTree(HybridTree):
    """
    Legacy hybrid tree interface for Mark-Jan's implementation for constituent parsing.
    Supposed that the tokens are of type ConstituentTerminal or ConstituentCategory.
    """

    def __init__(self, sent_label=None):
        HybridTree.__init__(self, sent_label)

    # Add next leaf. Order of adding is significant.
    # id: string
    # pos: string (part of speech)
    # word: string
    def add_leaf(self, id, pos, word, edge='--', morph=None, lemma='--'):
        token = ConstituentTerminal(word, pos, edge, morph, lemma)
        self.add_node(id, token, True, True)

    # Add punctuation: has no parent
    # id: string
    # pos: string (part of speech)
    # word: string
    def add_punct(self, id, pos, word):
        token = ConstituentTerminal(word, pos)
        self.add_node(id, token, True, False)

    # Add label of non-leaf. If it has no children, give it empty list of
    # children.
    # id: string
    # label: string
    def set_label(self, id, label):
        token = ConstituentCategory(label)
        self.add_node(id, token, False, True)

    # All leaves of tree.
    # return: list of triples.
    def leaves(self):
        return [(id, self.leaf_pos(id), self.leaf_word(id)) for id in self.full_yield()]

    # Is leaf? (This is, the id occurs in the list of leaves.)
    # id: string
    # return: bool
    def is_leaf(self, id):
        return id in self.full_yield()

    # Get leaf for index.
    # index: int
    # return: triple
    def index_leaf(self, index):
        return self.index_node(index)

    # Get index for id of leaf.
    # id: string
    # return: int
    def leaf_index(self, id):
        return self.node_index(id)

    # Get part of speech of node.
    # id: string
    # return: string
    def leaf_pos(self, id):
        return self.node_token(id).pos()

    # Get word of node.
    # id: string
    # return: string
    def leaf_word(self, id):
        return self.node_token(id).form()

    # Get yield as list of words, omitting punctuation.
    # return: list of string
    def word_yield(self):
        return [token.form() for token in self.token_yield()]

    # Get yield as list of pos, omitting punctuation.
    # return: list of string
    def pos_yield(self):
        return [token.pos() for token in self.token_yield()]

    # Get label of (non-leaf) node.
    # id: string
    # return: string
    def label(self, id):
        return str(self.node_token(id))

    # Get ids of all internal nodes.
    # return: list of string
    def ids(self):
        return [n for n in self.nodes() if n not in self.full_yield()]

    def n_nodes(self):
        return HybridTree.n_nodes(self) + 1

    def labelled_spans(self):
        """
        :return: list of spans (each of which is string plus an even number of (integer) positions)
        Labelled spans.
        """
        spans = []
        for id in [n for n in self.nodes() if n not in self.full_yield()]:
            span = [self.node_token(id).category()]
            for (low, high) in join_spans(self.fringe(id)):
                span += [low, high]
            # TODO: this if-clause allows to handle trees, that have nodes with empty fringe
            if len(span) >= 3:
                spans += [span]
        return sorted(spans,
                      # cmp=lambda x, y: cmp([x[1]] + [-x[2]] + x[3:] + [x[0]], \
                      #                      [y[1]] + [-y[2]] + y[3:] + [y[0]])
                      key=lambda x: [tuple(x[1:]), x[0]])

    def strip_vroot(self):
        if (len(self.root) == 1) and self.node_token(self.root[0]).type() == "CONSTITUENT-CATEGORY" and self.node_token(self.root[0]).category() == "VROOT":
            old_root = self.root[0]
            new_roots = self.children(old_root)
            self._id_to_child_ids[self.virtual_root] = new_roots
            for new_root in new_roots:
                self._parent[new_root] = self.virtual_root
            self._id_to_token.pop(old_root, None)
        else:
            # print self
            pass


__all__ = ["ConstituentTree"]
