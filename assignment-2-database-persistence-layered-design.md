**ASSIGNMENT 2**

**Database Persistence and Layered Design**

*Library Management System API \| 100 points*

| **Due**             | Tuesday, October 20, 2026, at 11:59 p.m.                                                      |
|---------------------|-----------------------------------------------------------------------------------------------|
| **Required branch** | assignment-2                                                                                  |
| **Course coverage** | Module 05: persistence, state, and layered design                                             |
| **Submission**      | Canvas submission with the public GitHub repository link; work must be on the required branch |

**Purpose**

Build on Assignment 1 by adding PostgreSQL persistence alongside the temporary application-memory implementation. Apply the SQLAlchemy, layered-design, transaction, dependency-injection, and service-abstraction practices demonstrated in the Project and Task Management API while preserving the Library Management System API behavior you already designed.

| **Scope boundary:** This assignment covers Module 05 persistence and layered design only. Automated testing, API conformance testing, authentication, authorization, and database migrations are introduced in later modules and are not required here. |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

**Learning outcomes**

> • Persist related API data in PostgreSQL using SQLAlchemy ORM.
>
> • Separate HTTP, application-use-case, database-query, and ORM responsibilities.
>
> • Use Sessions and transactions so a complete write succeeds or rolls back as one operation.
>
> • Use dependency injection and a shared service abstraction to support interchangeable storage implementations.
>
> • Configure the application safely and document it for a new developer.

**Persistence and database requirements**

> 1\. Use PostgreSQL with SQLAlchemy 2.x and Psycopg, matching the course demonstration.
>
> 2\. Add PostgreSQL persistence as a selectable backend alongside Assignment 1's in-memory implementation. When the database backend is selected, Library data must survive stopping and restarting the API; the in-memory backend must remain available for temporary process-local storage.
>
> 3\. Create separate SQLAlchemy ORM models for Book and Member. PostgreSQL must generate their primary-key values.
>
> 4\. Model the one-to-many Member-to-Book relationship with a database foreign key. A Book must reference an existing Member, and a Member may have many Books.
>
> 5\. Enforce non-null stored values and database-level unique constraints for ISBN, Member email address, and membership ID. Keep Assignment 1's Pydantic request validation as the API boundary.
>
> 6\. Preserve Assignment 1's business behavior: a Member with associated Books cannot be deleted, and the API must clearly report missing resources and conflicts without exposing raw database details.

**Layered application requirements**

> 1\. Organize the application into clear router, schema, service, repository, ORM-model, and database/configuration responsibilities. Equivalent names are acceptable when each responsibility remains clear.
>
> 2\. Keep routers focused on HTTP: validated request data, service calls, response models, status codes, and translation of application outcomes to HTTP responses. Do not place SQL queries, Session creation, or transaction decisions in routers.
>
> 3\. Keep services focused on Library use cases and business rules. Services must not depend on FastAPI HTTP exceptions or response details. Services raise application-specific exceptions for application outcomes; routers catch those exceptions and convert them to appropriate FastAPI HTTPException responses.
>
> 4\. Keep repositories focused on SQLAlchemy queries and writes. Repositories should not choose HTTP responses or own Library business policies.
>
> 5\. Keep Pydantic schemas distinct from ORM models: schemas define the API contract; ORM models define database tables and relationships.

**Session and transaction requirements**

> 1\. Create one application-scoped SQLAlchemy Engine and session factory. Do not create an Engine for every request and do not share one Session across concurrent requests.
>
> 2\. Each database service operation must create and close its own Session through the session factory.
>
> 3\. Each write use case must have a transaction boundary in the service layer. A normal completion commits the complete operation; an exception rolls it back so partial changes are not saved.
>
> 4\. If a use case needs more than one repository operation, use the same operation-scoped Session and transaction for the complete use case.

**Service abstraction, dependency injection, and configuration**

> 1\. Define a shared Book-service abstraction and Member-service abstraction that describe the operations routers can call.
>
> 2\. Provide both a database-backed implementation and an in-memory implementation for each service abstraction. The database implementations use repositories; the in-memory implementations own only temporary process-local state.
>
> 3\. Load and validate configuration once at application startup using a typed settings object. Configuration must select the storage backend; the database backend must be the documented default for this assignment.
>
> 4\. Use a supported, explicit backend value such as an enum rather than scattered unvalidated string literals.
>
> 5\. At startup, create the selected service implementations and store them on application state. Use FastAPI dependency functions and \`Depends(...)\` so routers receive the service abstraction instead of constructing a service, repository, or Session themselves.

| **Why this is graded:** The router should depend on the service contract, not on PostgreSQL or Python lists. This lets the selected implementation change without rewriting the API routes. |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

**Required evidence and deliverables**

> • Complete Assignment 2 source code, dependency metadata, and lockfile.
>
> • PostgreSQL setup or initialization instructions and a safe \`.env.example\` that documents required settings without real credentials.
>
> • An updated README written from the perspective of a new developer getting started with the project. Include the project purpose, prerequisites, PostgreSQL setup, configuration steps, install and run commands, \`/docs\` and \`/redoc\` links, the storage-backend setting, example related Book and Member requests, and a current project structure tree.
>
> • A clear project structure, descriptive naming, and concise comments for non-obvious behavior or design decisions. Do not add comments that merely restate obvious code.
>
> • No automated-test deliverable is required for this assignment because automated testing is introduced in a later module. You are still responsible for testing the API thoroughly before submitting.

**Git and Canvas submission**

Create and complete this milestone on a branch named exactly assignment-2. Build it from your submitted Assignment 1 work so Assignment 1 behavior remains part of the application. Do not submit Assignment 2 from main or from a differently named branch.

> • Submit the public GitHub repository URL in Canvas.
>
> • Make sure the required work is pushed to the assignment-2 branch before the deadline.
>
> • Push all required project files. Do not commit \`.env\` or passwords.

| **Deadline and late work:** Any commit added to the assignment-2 branch after the Canvas deadline makes the assignment late. As stated in the syllabus, late work is capped at a maximum grade of 80. |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

**How your submission will be evaluated**

> 1\. The instructor checks out the required assignment-2 branch from the submitted repository.
>
> 2\. The README setup, configuration, dependency-installation, and run instructions are followed from the perspective of a new developer.
>
> 3\. PostgreSQL is started using the documented setup, and the API is run with the database backend.
>
> 4\. Representative success and error cases are exercised in Swagger UI or another HTTP client, including an API restart to verify durable data.
>
> 5\. The instructor inspects ORM mappings and constraints; service/repository/router boundaries; Session and transaction handling; dependency injection; configuration; project structure; naming; and helpful code comments.

**Grading rubric**

Points will be deducted for bugs, errors, or failure to follow the project structure and code-organization practices demonstrated in the Project and Task Management API.

| **Category**                                       | **Evidence used for grading**                                                                                                                                                                    | **Points** |
|----------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------|
| **PostgreSQL and ORM design**                      | PostgreSQL setup, SQLAlchemy Book and Member models, database-generated IDs, non-null and unique constraints, and the Member–Book foreign-key relationship are correct.                          | **25**     |
| **Layered persistence and transactions**           | Routers, schemas, services, repositories, and ORM models have clear responsibilities. Service operations use short-lived Sessions and correctly commit or roll back write transactions.          | **25**     |
| **Service abstraction, DI, and configuration**     | Shared service contracts, database and in-memory implementations, startup-selected services, FastAPI dependency injection, typed settings, and backend selection are implemented as required.    | **15**     |
| **Persistent Library API behavior**                | Assignment 1 Book and Member operations, relationship behavior, validation, and HTTP outcomes remain correct while using PostgreSQL data that survives restart.                                  | **15**     |
| **Reliability and data integrity**                 | Representative success and error cases work without bugs; duplicate values, missing related records, blocked Member deletion, and failed writes preserve consistent data.                        | **10**     |
| **Organization, README, and configuration safety** | A new developer can follow the README; the project is organized by responsibility; comments clarify non-obvious decisions; \`.env.example\` is useful; \`.env\` and passwords are not committed. | **10**     |
| **Total**                                          |                                                                                                                                                                                                  | **100**    |
