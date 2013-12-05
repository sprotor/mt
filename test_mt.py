import os
from mt import MerkleTree

class Test_MerkleTree:

    def test_mt_init_no_arguments(self):
        '''Merkle Tree must not be generated if MerkleTree class is initialized without any arguments'''
        t_MT = MerkleTree()
        assert(t_MT._tree == None)

    def test_mt_init_with_path(self):
        '''Merkle Tree must be generated if MerkleTree class is initialized with a path'''
        t_MT = MerkleTree('.')
        assert(t_MT._tree != None)

    def test_mt_init_with_generate_tree_without_arguments(self):
        '''Merkle Tree must be generated on current directory if generate_tree is called without arguments'''
        t_MT = MerkleTree()
        t_MT.generate_tree()
        assert(t_MT._tree != None)
        t_root_hash = t_MT._tree.keys()
        assert(len(t_root_hash) == 1)
        name, meta = t_MT._tree[t_root_hash[0]]
        assert(name == '.')

    def test_mt_tree_generation_parity(self):
        '''Merkle tree generated for a given folder must be the same irrespective of how the tree is generated'''
        t1_MT = MerkleTree('sample_folder')
        t2_MT = MerkleTree()
        t2_MT.generate_tree('sample_folder')
        assert(t1_MT._tree == t2_MT._tree)
        t2_MT.reset_tree()
        t2_MT.generate_tree('sample_folder')
        assert(t1_MT._tree == t2_MT._tree)

    def test_md5_validity(self):
        '''MD5 hash calculation must work correctly'''
        t_MT = MerkleTree()
        assert(t_MT._get_md5('I am some test data. Verify my MD5.') == '79921284e9a15eff8b9cca28e0689c86')

    def test_slurp_file(self):
        '''Slurp file must work correctly'''
        t_MT = MerkleTree()
        data = t_MT._slurp_file(os.path.join(os.curdir, 'sample_folder', 'child1.txt'))
        assert(data == 'I am the first child')

    def test_traverse_path_sort(self):
        '''Parent hash must be calculated on the sorted hash string of its children'''
        t_MT = MerkleTree('sample_folder')
        root_hash = t_MT._tree.keys()[0]
        name, meta = t_MT._tree[root_hash]
        assert(name == 'sample_folder')
        ch_hash = meta.keys()
        ch_hash_str = ''.join(ch_hash)
        ch_hash.sort()
        ch_hash_sorted_str = ''.join(ch_hash)
        # Here we assume that there are sufficient number of hashes such that a retrieved list
        # of hashes without sorting, are not in sorted order already.
        name_hash = t_MT._get_md5(name)
        parent_hash_str = name_hash + ch_hash_sorted_str
        assert(ch_hash_str != ch_hash_sorted_str)
        assert(t_MT._get_md5(parent_hash_str) == root_hash)

    def test_file_meta_hash(self):
        '''The file hash must be the hash of the filename hash followed by file data hash'''
        t_MT = MerkleTree()
        f_hash, (f_name, f_data_hash) = t_MT._meta_file('sample_folder', 'child1.txt')
        assert(f_hash == 'e446917b26e3a3643aa147adfde7b787')
        assert(f_name == 'child1.txt')
        assert(f_data_hash == 'c4ab1505e17a436af78cef94bd2abebb')

    def test_empty_folder_meta(self):
        '''The tree for an empty folder must return a blank dictionary in place of data'''
        t_MT = MerkleTree(os.path.join('sample_folder','folder2','empty_folder1'))
        root_hash = t_MT._tree.keys()[0]
        name, meta = t_MT._tree[root_hash]
        # root_hash = hash(hash('empty_folder1'))
        assert(root_hash == 'f0fc295fa8ef27fb56ae193808925a89')
        assert(name == 'empty_folder1')
        assert(meta == {})

    def test_hash_hierarchy(self):
        '''The hash of a child must feature in the hash list of it's parents children'''
        t_MT = MerkleTree(os.path.join('sample_folder','folder2','empty_folder1'))
        grand_child_hash = t_MT._tree.keys()[0] # -- hash of 'empty_folder1'
        t_MT = MerkleTree(os.path.join('sample_folder','folder2'))
        child_hash = t_MT._tree.keys()[0] # -- hash of 'folder2'
        (name, meta) = t_MT._tree[child_hash] # -- meta has children of 'folder2'
        child_hash_grandchildren = meta.keys() # -- hash list of all siblings of empty_folder1
        # -- Assert that 'empty_folder1' is inside 'folder2'
        assert(grand_child_hash in child_hash_grandchildren)
        t_MT = MerkleTree('sample_folder')
        parent_hash = t_MT._tree.keys()[0]
        (name, meta) = t_MT._tree[parent_hash]
        parent_hash_children = meta.keys() # -- hash list of all siblings of folder2
        # -- Assert that 'empty_folder1' is inside 'folder2'
        assert(child_hash in parent_hash_children)
