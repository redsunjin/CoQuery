# CoQuery JPA Support Plan

Date: 2026-04-10

## Decision

JPA support should be treated as an ORM/model track, not as another DB backend.

Reason:

- CoQuery database backends execute SQL through a database connection.
- JPA works through Java entity metadata, JPQL, Criteria, an `EntityManager`, a persistence unit, and a Java runtime classpath.
- A `jpa://` URI alone is not enough to safely execute queries because runtime execution depends on the Java project build, provider, transaction mode, and persistence configuration.

Reference baseline:

- Jakarta Persistence 3.2 specification: https://jakarta.ee/specifications/persistence/3.2/jakarta-persistence-spec-3.2

## Current Implemented Slice

Status: `source_introspection_only`

Implemented command:

```bash
python3 main.py --command jpa_schema --jpa-project /path/to/java-project --format json
```

What it does:

- scans `.java` source files under the given project path
- detects annotation-based `@Entity` classes
- reads common entity/table/column/id/relationship annotations
- returns a JSON model that agents can use as schema context

Supported annotations in the first slice include:

- `@Entity`
- `@Table`
- `@Id`
- `@EmbeddedId`
- `@Column`
- `@JoinColumn`
- `@OneToOne`
- `@OneToMany`
- `@ManyToOne`
- `@ManyToMany`
- `@ElementCollection`
- `@Transient`

The scanner recognizes both `jakarta.persistence.*` and legacy `javax.persistence.*` annotation names because it reads the annotation short names from source.

## Explicit Non-Goals For This Slice

This slice does not:

- execute JPQL
- execute Criteria queries
- start a Java process
- load a Maven or Gradle classpath
- inspect compiled bytecode
- parse XML-only entity mappings
- guarantee full JPA provider behavior
- claim Spring Data JPA repository support

## Next Viable Slices

### Slice 2. JPQL Drafting

Add a `jpa_generate` command that returns JPQL, not SQL.

Example:

```bash
python3 main.py --command jpa_generate --jpa-project app --skill select_simple --params '{"entity":"User"}'
```

Gate:

- generated output is labelled JPQL
- tests prove entity names are used instead of table names
- no runtime execution claim is made

### Slice 3. Java Runtime Probe

Add a small Java runner that can execute one read-only JPQL query through `EntityManager`.

Required inputs:

- project path
- build tool or classpath
- persistence unit name
- provider dependencies
- read-only JPQL

Gate:

- one local fixture project proves `SELECT e FROM Entity e`
- no write support until transaction handling is explicit

### Slice 4. Transaction-Gated Writes

Add explicit write support only after read-only JPQL execution is stable.

Gate:

- `--write` is required
- transaction behavior is explicit
- rollback/failure behavior is tested

## Product Label

Current label:

- JPA: `experimental source introspection`

Do not label JPA as:

- working backend
- JPQL runtime support
- Spring Data JPA support
- production ORM integration
