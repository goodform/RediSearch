<center>![logo.png](logo.png)</center>

# RediSearch - Redis Powered Search Engine

RediSearch is a an open-source Full-Text and Secondary Index engine over Redis.

!!! note "Quick Links:"
    * [Source Code at GitHub](https://github.com/goodform/RediSearch).
    * [Latest Release: 1.2.0](https://github.com/goodform/RediSearch/releases)
    * [Docker Image: goodform/redisearch](https://hub.docker.com/g/goodform/redisearch/)
    * [Quick Start Guide](/Quick_Start)
    * [Mailing list / Forum](https://groups.google.com/forum/#!forum/redisearch)

!!! tip "Supported Platforms"
    RediSearch is developed and tested on Linux and Mac OS, on x86_64 CPUs.

    i386 CPUs should work fine for small data-sets, but are not tested and not recommended. Atom CPUs are not supported currently. 

## Overview

Redisearch implements a search engine on top of Redis, but unlike other Redis 
search libraries, it does not use internal data structures like sorted sets.

This also enables more advanced features, like exact phrase matching and numeric filtering for text queries, 
that are not possible or efficient with traditional Redis search approaches.

## Client Libraries

Official and community client libraries in Python, Java, JavaScript, Ruby, Go, C#, and PHP. 
See [Clients Page](/Clients)

## Primary Features:

* Full-Text indexing of multiple fields in documents.
* Incremental indexing without performance loss.
* Document ranking (provided manually by the user at index time).
* Complex boolean queries with AND, OR, NOT operators between sub-queries.
* Optional query clauses.
* Prefix based searches.
* Field weights.
* Auto-complete suggestions (with fuzzy prefix suggestions)
* Exact Phrase Search, Slop based search.
* Stemming based query expansion in [many languages](/Stemming/) (using [Snowball](http://snowballstem.org/)).
* Support for custom functions for query expansion and scoring (see [Extensions](/Extensions)).
* Limiting searches to specific document fields (**Up to ~~32~~ 128 TEXT fields supported; Unlimited TAG and NUMERIC fields**).
* Numeric filters and ranges.
* Geo filtering using Redis' own Geo-commands. 
* Unicode support (UTF-8 input required)
* Retrieve full document content or just ids
* Document deletion and updating with index garbage collection.
* Partial document updates.


