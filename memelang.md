# Memelang v5

Memelang is a concise query language for structured data, knowledge graphs, retrieval-augmented generation, and semantic data.

### Memes

A ***meme*** comprises key-value pairs separated by spaces and is analogous to a relational database row.

```
m=123 R1=A1 R2=A2 R3=A3;
```

* ***M-identifier***: an arbitrary integer in the form `m=123`, analogous to a primary key
* ***R-relation***: an alphanumeric key analogous to a database column
* ***A-value***: an integer, decimal, or string analogous to a database cell value
* Non-alphanumeric A-values are CSV-style double-quoted `="John ""Jack"" Kennedy"`
* Memes are ended with a semicolon
* Comments are prefixed with double forward slashes `//`

```
// Example memes for the Star Wars cast
m=123 actor="Mark Hamill" role="Luke Skywalker" movie="Star Wars" rating=4.5;
m=456 actor="Harrison Ford" role="Han Solo" movie="Star Wars" rating=4.6;
m=789 actor="Carrie Fisher" role=Leia movie="Star Wars" rating=4.2;
```

### Queries

Queries are partial memes with empty parts as wildcards:
* Empty A-values retrieve all values for the specified R-relation
* Empty R-relations retrieve all relations for the specified A-value
* Empty R-relations and A-values (` = `) retrieve all pairs in the meme

```
// Query for all movies with Mark Hamill as an actor
actor="Mark Hamill" movie=;

// Query for all relations involving Mark Hamill
="Mark Hamill";

// Query for all relations and values from all memes relating to Mark Hamill:
="Mark Hamill" =;
```

A-value operators:
* String: `=` `!=`
* Numeric: `=` `!=` `>` `>=` `<` `<=`

```
firstName=Joe;
lastName!="David-Smith";
height>=1.6;
width<2;
weight!=150;
```

Comma-separated values produce an ***OR*** list:

```
// Query for (actor OR producer) = (Mark OR "Mark Hamill")
actor,producer=Mark,"Mark Hamill"
```

R-relation operators:
* `!` negates the relation name

```
// Query for Mark Hamill's non-acting relations
!actor="Mark Hamill";

// Query for an actor who is not Mark Hamill
actor!="Mark Hamill";

// Query all relations excluding actor and producer for Mark Hamill
!actor,producer="Mark Hamill"
```


### A-Joins

Open brackets `R1[R2` join memes with equal `R1` and `R2` A-values. Open brackets need **not** be closed, a semicolon closes all brackets.

```
// Generic example
R1=A1 R2[R3 R4>A4 A5=;

// Query for all of Mark Hamill's costars
actor="Mark Hamill" movie[movie actor=;

// Query for all movies in which both Mark Hamill and Carrie Fisher act together
actor="Mark Hamill" movie[movie actor="Carrie Fisher";

// Query for anyone who is both an actor and a producer
actor[producer;

// Query for a second cousin: child's parent's cousin's child
child= parent[cousin parent[child;

// Join any A-Value from the present meme to that A-Value in another meme
R1=A1 [ R2=A2
```

Joined queries return one meme with multiple `m=` M-identifiers. Each `R=A` belongs to the preceding `m=` meme.

```
m=123 actor="Mark Hamill" movie="Star Wars" m=456 movie="Star Wars" actor="Harrison Ford";
```

### Variables

R-relations and A-values may be certain variable symbols. Variables *cannot* be inside quotes.

* `@` Last matching A‑value
* `%` Last matching R‑relation
* `#` Current M-identifier

```
// Join two different memes where R1 and R2 have the same A-value (equivalent to R1[R2)
R1= m!=# R2=@;

// Two different R-relations have the same A-value
R1= R2=@;

// The first A-value is the second R-relation
R1= @=A2;

// The first R-relation equals the second A-value
=A1 R2=%;

// The pattern is run twice (redundant)
R1=A1 %=@;

// The second A-value may be Jeff or the previous A-value
R1= R2=Jeff,@;
```

### M-Joins

Explicit joins are controlled using `m` and `#`.

* `m=#` present meme (implicit default)
* `m!=#` join to a different meme
* `m= ` join to any meme (including the present)
* `m=^#` (or `]`) resets `m` and `#` to the previous meme, acts as *unjoin*

```
// Join two different memes where R1 and R2 have the same A-value (equivalent to R1[R2)
R1= m!=# R2=@;

// Join any memes (including the present one) where R1 and R2 have the same A-value
R1= m= R2=@;

// Join two different memes, unjoin, join a third meme (equivalent statements)
R1[R2] R3[R4;
R1= m!=# R2=@ m=^# R3= m!=# R4=@;

// Unjoins may be sequential (equivalent statements)
R1[R2 R3[R4]] R5=;
R1= m!=# R2=@ R3= m!=# R4=@ m=^# m=^# R5=;
R1= m!=# R2=@ R3= m!=# R4=@ m=^# ] R5=;
R1= m!=# R2=@ R3= m!=# R4=@ ]] R5=;

// Join two different memes on R1=R2, unjoin, then join the first meme to another where R4=R5
R1= m!=# R2=@ R3= m=^# R4= m!=# R5=@;

// Query for a meta-meme, R2's A-value is R1's M-identifier
R1=A1 m= R2=#
```

### SQL Comparisons

Memelang queries are significantly shorter and clearer than equivalent SQL queries.

```
movie="Star Wars" actor= role= rating>4;
SELECT actor, role FROM memes WHERE movie = 'Star Wars' AND rating > 4;

role="Luke Skywalker","Han Solo" actor=;
SELECT actor FROM movies WHERE role IN ('Luke Skywalker', 'Han Solo');

producer,actor="Mark Hamill","Harrison Ford" movie[movie actor=
SELECT m1.actor, m1.movie, m2.actor FROM movies m1 JOIN movies m2 ON m1.movie = m2.movie WHERE m1.actor IN ('Mark Hamill', 'Harrison Ford') or m1.producer IN ('Mark Hamill', 'Harrison Ford');
```

### About

Memelang was created by [Bri Holt](https://en.wikipedia.org/wiki/Bri_Holt) and first disclosed in a [2023 U.S. Provisional Patent application](https://patents.google.com/patent/US20250068615A1). ©2025 HOLTWORK LLC. Contact [info@memelang.net](mailto:info@memelang.net).