prefetchers = [
    "StridePrefetcher",
    "TaggedPrefetcher",
    "AMPMPrefetcher",
    "IndirectMemoryPrefetcher",
    "DCPTPrefetcher", 
    "None",
    "MultiPrefetcher"
]

multiprefetcher_priority_list = {
    "StridePrefetcher": 3,
    "TaggedPrefetcher": 4,
    "AMPMPrefetcher" : 2,
    "IndirectMemoryPrefetcher": 1,
    "DCPTPrefetcher": 0
}