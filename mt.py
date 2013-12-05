import os
import hashlib

class MerkleTree:

    def __init__(self, root=None):
        self._tree = None
        self._depth = 0
        self._spacer = '-' * 4
        self._arrow = '>>'
        if not root == None:
            self.generate_tree(root=root)

    def _traverse_path(self, cur_dir):
        dir_items = os.listdir(cur_dir)
        children = {}
        for item in dir_items:
            cur_item = os.path.join(cur_dir, item)
            if not os.path.isdir(cur_item):
                file_hash, file_meta = self._meta_file(cur_dir, item)
                children[file_hash] = file_meta
            else:
                dir_hash, dir_meta = self._traverse_path(cur_item)
                children[dir_hash] = dir_meta
        base_name = os.path.basename(cur_dir) # -- Get just the name
        hash_list = children.keys() # -- Get the hashes of all children
        hash_list.sort() # -- Sort all the hashes
        parent_name_hash = self._get_md5(base_name) # -- Hash the name of the parent
        children_hash = ''.join(hash_list) # -- Join all the hashes of children
        parent_hash = self._get_md5(parent_name_hash + children_hash) # -- hash(hash(parent-name)+sorted hashes of children)
        return parent_hash, (os.path.basename(cur_dir), children)

    def _meta_file(self, cur_dir, item):
        data_hash = self._get_md5(self._slurp_file(os.path.join(cur_dir,item)))
        name_hash = self._get_md5(item)
        comb_hash = self._get_md5(name_hash + data_hash)
        return comb_hash, (item, data_hash)

    def _slurp_file(self, absolute_file):
        with open(absolute_file, 'rb') as f:
            data = f.read()
        return data

    def _get_md5(self, data):
        m = hashlib.md5()
        m.update(data)
        return m.hexdigest()

    def _display_tree(self, tree, depth):
        if isinstance(tree, dict):
            r_hashes = tree.keys()
            for each_hash in r_hashes:
                (name, data) = tree[each_hash]
                if isinstance(data, str):
                    print '%s%s %s \t {SHA-of-PARENT: %s, SHA-of-DATA: %s}' % (self._spacer * depth, self._arrow, name, each_hash, data)
                else:
                    print '%s%s %s \t {SHA-of-PARENT: %s}' % (self._spacer * depth, self._arrow, name, each_hash)
                    self._display_tree(data, depth+1)

    #-- Public

    def reset_tree(self):
        self._tree = None

    def generate_tree(self, root=None):
        if root == None:
            root = os.curdir
        self._root = root
        self.reset_tree()
        self._tree = {}
        parent_hash, parent_meta = self._traverse_path(self._root)
        self._tree[parent_hash] = parent_meta
        return self._tree

    def display_tree(self):
        self._display_tree(self._tree, self._depth)

# ----

def main():
    my_mt = MerkleTree()
    my_mt.generate_tree(os.path.join('sample_folder'))
    my_mt.display_tree()

if __name__ == '__main__':
    main()
