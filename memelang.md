# Memelang 4.1

Memelang is an elegant and powerful query language with broad applicability in structured data querying, knowledge graph handling, retrieval-augmented generation, and semantic data processing.

### Syntax

A meme is analogous to a relational database row. A meme comprises key-value pairs, separated by spaces, starting with an arbitrary integer M-identifier, and ending with a semicolon: `m=123 R1=A1 R2=A2;`

* ***R-relations*** are alphanumeric keys analogous to relational database columns.
* ***A-values*** are integers, decimals, or strings analogous to relational database cell values.
* A-value strings containing `[^A-Za-z0-9_]` characters are double-quoted `="John \"Jack\" Kennedy"`
* Comments are prefixed with double forward slashes `//`.

```
// Example memes for the Star Wars cast
m=123 actor="Mark Hamill" role="Luke Skywalker" movie="Star Wars" rating=4.5;
m=456 actor="Harrison Ford" role="Han Solo" movie="Star Wars" rating=4.6;
m=789 actor="Carrie Fisher" role=Leia movie="Star Wars" rating=4.2;
```

### Queries

Search queries are partially specified Memelang statements. Empty parts of the statement are wildcards. 
* Empty A-value queries the specified R-relation for any A-value. 
* Empty R-relation queries the specified A-value for any R-relation. 
* Empty R-relation and A-value (` = `) queries for all pairs in the meme.

```
// Example query for all movies with Mark Hamill as an actor
actor="Mark Hamill" movie=;

// Example query for all relations involving Mark Hamill
="Mark Hamill";

// Example query for all relations and values from all memes relating to Mark Hamill:
="Mark Hamill" =;
```

String A-values use `=` and `!=` operators. Numeric A-values use standard comparison operators `=` `>`, `>=`, `<`, `<=`, and `!=`. Examples:

```
firstName=Joe lastName!="David-Smith" height>=1.6 width<2 weight!=150;
```

R-relations may be prefixed with `!` for "relation must not equal."

```
// Example query for Mark Hamill's non-acting relations
!actor="Mark Hamill";

// Which is distinct from an actor who is not Mark Hamill
actor!="Mark Hamill";
```

### A-Joins

Analogous to relational database joins, using `R1[R2` allows for queries matching multiple memes where the A-value for `R1` equals the A-value for `R2`. Open brackets do ***not*** need to be closed.

```
// Generic example
R1=A1 R2[R3 R4>A4 A5=;

// Example query for all of Mark Hamill's costars
actor="Mark Hamill" movie[movie actor=;

// Example query for all movies in which both Mark Hamill and Carrie Fisher act together
actor="Mark Hamill" movie[movie actor="Carrie Fisher";

// Example query for anyone who is both an actor and a producer
actor[producer;

// Example query for a second cousin: child's parent's cousin's child
child= parent[cousin parent[child;

// Join any A-Value from the current meme to that A-Value in any another meme
R1=A1 [ R2=A2
```

Joined queries return one meme with multiple `m=` M-identifiers. Each `R=A` belongs to the preceding `m=` meme.

```
m=123 actor="Mark Hamill" movie="Star Wars" m=456 movie="Star Wars" actor="Harrison Ford";
```

### Variables

R-relations or A-values may be certain variable symbols. Variables *cannot* be wrapped in quotes.

* `@` Last matching A‑value
* `~` Last matching R‑relation
* `#` Current M-identifier

```
// Join two different memes where R1 and R2 have the same A-value (equivalent to R1[R2)
R1= m!=# R2=@;

// Two different R-relations have the same A-value
R1= R2=@;

// The first A-value is the second R-relation
R1= @=A2;

// The first R-relation equals the second A-value
=A1 R2=~;

// The pattern is run twice (redundant)
R1=A1 ~=@;
```

### M-Joins

More complex joins are made by specifying `m` and using the `#` variable.

* `m=#` is implicit in every `R=A` pair, which are assumed to belong to the current M-identifier
* `m!=#` joins to any other meme, excluding the current one
* `m= ` joins to any meme, including the current one
* `m=^#` (shorthand `]`) sets `m` and `#` to the *previous* M-identifer, used to unjoin and branch queries.

```
// Join two different memes where R1 and R2 have the same A-value (equivalent to R1[R2)
R1= m!=# R2=@;

// Join any memes (including the current one) where R1 and R2 have the same A-value
R1= m= R2=@;

// Join two different memes, unjoin, join a third meme (two equivalent statements)
R1[R2] R3[R4;
R1= m!=# R2=@ m=^# R3= m!=# R4=@;

// Unjoins may be sequential
R1[R2 R3[R4]] R5=;
R1= m!=# R2=@ R3= m!=# R4=@ m=^# m=^# R5=;

// Join two different memes on R1=R2, unjoin, then join the first meme to another where R4=R5
R1= m!=# R2=@ R3= m=^# R4= m!=# R5=@;

// Query for a meta-meme. R2's A-value is R1's M-identifier
R1=A1 m= R2=#
```

### About

Memelang was created by [Bri Holt](https://en.wikipedia.org/wiki/Bri_Holt) and first disclosed in a [2023 U.S. Provisional Patent application](https://patents.google.com/patent/US20250068615A1). Copyright 2025 HOLTWORK LLC. Contact [info@memelang.net](mailto:info@memelang.net).