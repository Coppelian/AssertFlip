from sympy.utilities.iterables import partitions

def test_partitions_reuse_bug():
    # Collect partitions into a list
    partition_list = list(partitions(6, k=2))
    
    # Check if all elements in the list are distinct objects
    first_partition = partition_list[0]
    for partition in partition_list:
        assert partition is not first_partition  # Correct behavior: each partition should be a distinct object

