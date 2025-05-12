# MEMELANG

### Syntax

Memelang is a universal structured data and query language. Memelang uses key-value pairs separated by spaces as:

```
m=123 R1=A1 R2=A2 R3=A3;
```

The key is an alphanumeric string termed a *R-relation* and is analogous to a relational database column.

The *A-value* is is analogous to a relational database cell value. An A-value may be an integer `=123`, decimal `=45.6`, plain string `=Walmart`, or string wrapped in double quotes `="Top Gun"`. Nested double quotes are escaped by a preceding backslash `="John \"Jack\" Kennedy"`.

A *meme* is formed from two or more `R=A` pairs. Each meme starts with an arbitrary integer M-identifier `m=123` and ends in a semicolon `;`. A meme is analogous to a relational database row without column constraints.

Comments are prefixed with double forward slashes `//`.

```
// Example memes for the Star Wars cast
m=123 actor="Mark Hamill" role="Luke Skywalker" movie="Star Wars" rating=4.5;
m=456 actor="Harrison Ford" role="Han Solo" movie="Star Wars" rating=4.6;
m=789 actor="Carrie Fisher" role=Leia movie="Star Wars" rating=4.2;
```

### Queries

Search queries are partially specified Memelang statements. Empty parts of the statement are wildcards. An empty A-value queries the specified R-relation for any A-value. An empty R-relation queries the specified A-value for any R-relation. An empty R-relation and A-value (` = `) queries for all pairs in the meme.

```
// Example query for all movies with Mark Hamill as an actor
actor="Mark Hamill" movie=;

// Example query for all relations involving Mark Hamill
="Mark Hamill";

// Example query for all relations and values from all memes relating to Mark Hamill:
="Mark Hamill" =;
```

String A-values may use `=` and `!=` operators. Numeric A-values may use standard comparison operators `=` `>`, `>=`, `<`, `<=`, and `!=`.

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

Using `R1:R2` allows for queries matching multiple memes where the A-value for `R1` equals the A-value for `R2`. This is analogous to relational database joins.

```
// Generic example
R1=A1 R2:R3 R4>A4 A5=

// Example query for all of Mark Hamill's costars
actor="Mark Hamill" movie:movie actor=

// Example query for all movies in which both Mark Hamill and Carrie Fisher act together
actor="Mark Hamill" movie:movie actor="Carrie Fisher"

// Example query for anyone who is both an actor and a producer:
actor:producer

// Example query for a second cousin: child's parent's cousin's child
child= parent:cousin parent:child
```

## Variables

R-relations or A-values may be certain variable symbols. Variables *cannot* be wrapped in quotes.

* `@` Last matching **A‑value**
* `~` Last matching **R‑relation**
* `#` Last matching **M-identifier**
* `^` Second to last matching **M-identifier** - used to "unjoin" and branch the query

```
// Join two different memes where R1 and R2 have the same A-value (equivalent to R1:R2)
R1= m!=# R2=@;

// Join any memes (including the current one) where R1 and R2 have the same A-value
R1= m= R2=@;

// Join two different memes on R1=R2, unjoin, then join the first meme to another where R4=R5
R1= m!=# R2=@ R3= m=^ R4= m!=# R5=@;

// Two different R-relations have the same A-value
R1= R2=@;

// The first A-value is the second R-relation
R1= @=A2;

// The first R-relation equals the second A-value
=A1 R2=~;

// The pattern is run twice (redundant)
R1=A1 ~=@;
```


### About

Memelang was created by [Bri Holt](https://en.wikipedia.org/wiki/Bri_Holt) and first disclosed in a 2023 U.S. Provisional Patent application. Version 4 was released on March 29, 2025 with sporadic updates. Memelang license fees are trivial compared to savings in compute costs. Copyright 2025 HOLTWORK LLC. Patents pending. Contact [info@memelang.net](mailto:info@memelang.net).